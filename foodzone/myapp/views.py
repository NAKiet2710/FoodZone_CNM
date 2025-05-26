from django.shortcuts import render, get_object_or_404, reverse, redirect
from myapp.models import Contact, Dish, Category, Profile, Order, Shipper, DeliveryAddress, Delivery, DeliveryTracking, DeliveryStatus, Restaurant, OrderStatus, DeliveryReview, Cart, CartItem, OrderItem
from myapp.forms import ShipperRegistrationForm, DeliveryAddressForm, UpdateDeliveryStatusForm, RestrictedDeliveryStatusForm, RestaurantDeliveryStatusForm, DeliveryTrackingForm, ShipperAvailabilityForm, RestaurantRegistrationForm, DeliveryReviewForm, DishForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.db.models import Q, Sum
from django.contrib import messages
from datetime import datetime, timedelta
import json
import uuid
import google.generativeai as genai
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def index(request):
    context ={}
    cats = Category.objects.all().order_by('name')
    context['categories'] = cats
    # print()
    dishes = []
    for cat in cats:
        dishes.append({
            'cat_id':cat.id,
            'cat_name':cat.name,
            'cat_img':cat.image,
            'items':list(cat.dish_set.all().values())
        })
    context['menu'] = dishes
    return render(request,'index.html', context)

def contact_us(request):
    context={}
    if request.method=="POST":
        name = request.POST.get("name")
        em = request.POST.get("email")
        sub = request.POST.get("subject")
        msz = request.POST.get("message")
        
        obj = Contact(name=name, email=em, subject=sub, message=msz)
        obj.save()
        context['message']=f"Dear {name}, Thanks for your time!"

    return render(request,'contact.html', context)

def about(request):
    return render(request,'about.html')

def all_dishes(request):
    context={}
    dishes = Dish.objects.all()
    if "q" in request.GET:
        id = request.GET.get("q")
        dishes = Dish.objects.filter(category__id=id)
        context['dish_category'] = Category.objects.get(id=id).name 

    context['dishes'] = dishes
    return render(request,'all_dishes.html', context)

def register(request):
    context={}
    if request.method=="POST":
        #fetch data from html form
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        contact = request.POST.get('number')
        check = User.objects.filter(username=email)
        if len(check)==0:
            #Save data to both tables
            usr = User.objects.create_user(email, email, password)
            usr.first_name = name
            usr.save()

            profile = Profile(user=usr, contact_number = contact)
            profile.save()
            
            context['status'] = f"User {name} Registered Successfully!"
        else:
            context['error'] = f"A User with this email already exists"

    return render(request,'register.html', context)

def check_user_exists(request):
    email = request.GET.get('usern')
    check = User.objects.filter(username=email)
    if len(check)==0:
        return JsonResponse({'status':0,'message':'Not Exist'})
    else:
        return JsonResponse({'status':1,'message':'A user with this email already exists!'})

def signin(request):
    context={}
    if request.method=="POST":
        email = request.POST.get('email')
        passw = request.POST.get('password')

        check_user = authenticate(username=email, password=passw)
        if check_user:
            login(request, check_user)
            if check_user.is_superuser or check_user.is_staff:
                return HttpResponseRedirect('/admin')
            return HttpResponseRedirect('/dashboard')
        else:
            context.update({'message':'Invalid Login Details!','class':'alert-danger'})

    return render(request,'login.html', context)

@login_required
def dashboard(request):
    if request.method == "POST":
        if "update_profile" in request.POST:
            name = request.POST.get('name')
            contact = request.POST.get('contact_number')
            address = request.POST.get('address')

            usr = User.objects.get(id=request.user.id)
            usr.first_name = name
            usr.save()

            # Tìm hoặc tạo profile cho người dùng
            profile, created = Profile.objects.get_or_create(
                user=usr,
                defaults={'contact_number': contact, 'address': address}
            )
            
            if not created:
                profile.contact_number = contact
                profile.address = address

            if "profile_pic" in request.FILES:
                pic = request.FILES['profile_pic']
                profile.profile_pic = pic
            profile.save()
            context = {'status': 'Profile updated successfully!'}

        elif "change_pass" in request.POST:
            c_password = request.POST.get('current_password')
            password = request.POST.get('new_password')

            check = authenticate(username=request.user.username, password=c_password)
            if check == None:
                context = {'status': 'Current password is wrong!'}
            else:
                usr = User.objects.get(id=request.user.id)
                usr.set_password(password)
                usr.save()
                login(request, usr)
                context = {'status': "Password updated successfully"}
        
        return render(request, 'dashboard.html', context)

    # Tìm hoặc tạo profile cho người dùng hiện tại
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'contact_number': ''}
    )
    
    # Lấy tất cả các đơn hàng của người dùng, sắp xếp theo thời gian giảm dần (mới nhất trước)
    orders = Order.objects.filter(customer=profile).order_by('-ordered_on')
    
    # Lấy danh sách địa chỉ giao hàng
    addresses = DeliveryAddress.objects.filter(customer=profile).order_by('-is_default')
    
    # Lấy danh sách đơn hàng đang chờ giao (chưa hoàn thành giao hàng)
    pending_orders = []
    # Lấy cả đơn hàng đã thanh toán và đơn hàng COD (chưa thanh toán)
    for order in orders:
        # Đơn hàng COD (status=False, payment_method='cash') cũng cần hiển thị
        if order.status or order.payment_method == 'cash':
            try:
                delivery = Delivery.objects.get(order=order)
                if delivery.status != 'DE' and delivery.status != 'CA':  # Không phải đã giao hoặc đã hủy
                    pending_orders.append(order)
            except Delivery.DoesNotExist:
                # Đơn hàng chưa có thông tin giao hàng, vẫn thêm vào danh sách đang chờ
                pending_orders.append(order)
    
    # Lấy danh sách đơn hàng đã giao
    completed_orders = []
    for order in orders:
        # Đơn hàng đã thanh toán hoặc đơn hàng COD
        if order.status or order.payment_method == 'cash':
            try:
                delivery = Delivery.objects.get(order=order)
                if delivery.status == 'DE':
                    completed_orders.append(order)
            except Delivery.DoesNotExist:
                pass

    context = {
        'profile': profile,
        'orders': orders,  # Tất cả các đơn hàng
        'addresses': addresses,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_order': orders.count(),
        'success_order': orders.filter(status=True).count(),
        'pending_order': orders.filter(status=False).count()
    }
    
    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def single_dish(request, id):
    context = {}
    dish = get_object_or_404(Dish, id=id)
    context['dish'] = dish
    
    if request.user.is_authenticated:
        if request.method == "POST":
            profile = Profile.objects.get(user=request.user)
            
            # Kiểm tra xem khách hàng có địa chỉ giao hàng không
            has_address = DeliveryAddress.objects.filter(customer=profile).exists()
            
            if not has_address:
                messages.error(request, "Bạn cần thêm địa chỉ giao hàng trước khi đặt hàng")
                return redirect('manage_addresses')
            
            # Lấy phương thức thanh toán từ query string
            payment_method = request.GET.get('payment_method')
            
            if payment_method == 'cash':
                # Xử lý đơn hàng COD trực tiếp
                
                # Kiểm tra xem có đơn hàng cũ chưa thanh toán không
                order = None
                order_id = request.session.get('order_id')
                
                if order_id:
                    try:
                        # Tìm đơn hàng cũ chưa thanh toán
                        existing_order = Order.objects.get(
                            id=order_id, 
                            customer=profile,
                            status=False,  # Chưa thanh toán
                            payment_method='cash'  # Kiểm tra phương thức thanh toán phải là cash
                        )
                        
                        # Nếu có, xóa tất cả các item cũ trong đơn hàng
                        OrderItem.objects.filter(order=existing_order).delete()
                        
                        # Sử dụng lại đơn hàng cũ
                        order = existing_order
                        print(f"[SINGLE_DISH] Sử dụng lại đơn hàng COD #{order.order_number}")
                    except Order.DoesNotExist:
                        # Nếu không tìm thấy đơn hàng cũ hoặc đơn hàng đã thanh toán
                        order_id = None
                
                # Nếu không có đơn hàng cũ hợp lệ, tạo đơn hàng mới
                if not order:
                    # Gán số đơn hàng chính thức ngay khi tạo đơn hàng
                    last_order = Order.objects.filter(order_number__isnull=False).order_by('-order_number').first()
                    next_order_number = 1
                    if last_order:
                        next_order_number = last_order.order_number + 1
                    
                    # Tạo đơn hàng mới
                    order = Order(
                        customer=profile,
                        payment_method='cash',
                        order_number=next_order_number
                    )
                    order.save()
                    print(f"[SINGLE_DISH] Tạo đơn hàng COD mới #{order.order_number}")
                
                # Đảm bảo món ăn được liên kết với nhà hàng duy nhất
                if not dish.restaurant:
                    # Lấy nhà hàng duy nhất trong hệ thống
                    restaurant = Restaurant.objects.first()
                    if restaurant:
                        dish.restaurant = restaurant
                        dish.save()
                
                # Tạo OrderItem cho món ăn này
                OrderItem.objects.create(
                    order=order,
                    dish=dish,
                    quantity=1,
                    price=dish.discounted_price or dish.price
                )
                
                request.session['order_id'] = order.id
                
                # Chuyển đến trang xác nhận thanh toán tiền mặt
                return redirect('cash_payment_confirm')
            elif payment_method == 'paypal':
                # Xử lý đơn hàng PayPal trực tiếp
                
                # Kiểm tra xem có đơn hàng cũ chưa thanh toán không
                order = None
                order_id = request.session.get('order_id')
                
                if order_id:
                    try:
                        # Tìm đơn hàng cũ chưa thanh toán
                        existing_order = Order.objects.get(
                            id=order_id, 
                            customer=profile,
                            status=False,  # Chưa thanh toán
                            payment_method='paypal'  # Kiểm tra phương thức thanh toán phải là paypal
                        )
                        
                        # Nếu có, xóa tất cả các item cũ trong đơn hàng
                        OrderItem.objects.filter(order=existing_order).delete()
                        
                        # Sử dụng lại đơn hàng cũ
                        order = existing_order
                        print(f"[SINGLE_DISH] Sử dụng lại đơn hàng PayPal #{order.order_number}")
                    except Order.DoesNotExist:
                        # Nếu không tìm thấy đơn hàng cũ hoặc đơn hàng đã thanh toán
                        order_id = None
                
                # Nếu không có đơn hàng cũ hợp lệ, tạo đơn hàng mới
                if not order:
                    # Gán số đơn hàng chính thức ngay khi tạo đơn hàng
                    last_order = Order.objects.filter(order_number__isnull=False).order_by('-order_number').first()
                    next_order_number = 1
                    if last_order:
                        next_order_number = last_order.order_number + 1
                    
                    # Tạo đơn hàng mới
                    order = Order(
                        customer=profile,
                        payment_method='paypal',
                        order_number=next_order_number
                    )
                    order.save()
                    print(f"[SINGLE_DISH] Tạo đơn hàng PayPal mới #{order.order_number}")
                
                # Đảm bảo món ăn được liên kết với nhà hàng duy nhất
                if not dish.restaurant:
                    # Lấy nhà hàng duy nhất trong hệ thống
                    restaurant = Restaurant.objects.first()
                    if restaurant:
                        dish.restaurant = restaurant
                        dish.save()
                
                # Tạo OrderItem cho món ăn này
                item_price = dish.discounted_price or dish.price
                OrderItem.objects.create(
                    order=order,
                    dish=dish,
                    quantity=1,
                    price=item_price
                )
                
                request.session['order_id'] = order.id
                
                # Tạo form thanh toán PayPal
                host = request.get_host()
                paypal_dict = {
                    'business': settings.PAYPAL_RECEIVER_EMAIL,
                    'amount': item_price,
                    'item_name': dish.name,
                    'invoice': str(order.id),
                    'currency_code': 'USD',
                    'notify_url': f'http://{host}{reverse("paypal-ipn")}',
                    'return_url': f'http://{host}{reverse("cart_payment_done")}',
                    'cancel_return': f'http://{host}{reverse("cart_payment_cancel")}',
                }
                
                # Tạo form thanh toán PayPal và tự động submit
                form = PayPalPaymentsForm(initial=paypal_dict)
                
                # Chuyển hướng trực tiếp đến trang thanh toán PayPal
                return HttpResponse(f'''
                    <html>
                        <head>
                            <title>Chuyển hướng đến PayPal</title>
                            <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    text-align: center;
                                    padding-top: 50px;
                                }}
                                .loader {{
                                    border: 5px solid #f3f3f3;
                                    border-radius: 50%;
                                    border-top: 5px solid #3498db;
                                    width: 50px;
                                    height: 50px;
                                    animation: spin 1s linear infinite;
                                    margin: 20px auto;
                                }}
                                @keyframes spin {{
                                    0% {{ transform: rotate(0deg); }}
                                    100% {{ transform: rotate(360deg); }}
                                }}
                            </style>
                        </head>
                        <body>
                            <h2>Đang chuyển hướng đến PayPal...</h2>
                            <div class="loader"></div>
                            <p>Vui lòng đợi trong giây lát...</p>
                            {form.render()}
                            <script>
                                document.forms[0].submit();
                            </script>
                        </body>
                    </html>
                ''')
            else:
                # Thêm vào giỏ hàng trực tiếp thay vì chuyển hướng
                # Đảm bảo món ăn được liên kết với nhà hàng duy nhất
                if not dish.restaurant:
                    # Lấy nhà hàng duy nhất trong hệ thống
                    restaurant = Restaurant.objects.first()
                    if restaurant:
                        dish.restaurant = restaurant
                        dish.save()
                
                # Lấy hoặc tạo giỏ hàng cho người dùng
                cart = None
                if request.user.is_authenticated:
                    # Kiểm tra xem có giỏ hàng active trong session không
                    active_cart_id = request.session.get('active_cart_id')
                    if active_cart_id:
                        try:
                            cart = Cart.objects.get(id=active_cart_id, user=request.user)
                        except Cart.DoesNotExist:
                            # Nếu không tìm thấy, tạo mới
                            cart = Cart.objects.create(user=request.user)
                    else:
                        # Tìm giỏ hàng hiện có hoặc tạo mới
                        cart, created = Cart.objects.get_or_create(user=request.user)
                
                # Đảm bảo cart không phải là None
                if not cart:
                    cart = Cart.objects.create(user=request.user)
                
                # Lưu ID giỏ hàng vào session để sử dụng sau này
                request.session['active_cart_id'] = cart.id
                
                # Kiểm tra xem món ăn đã có trong giỏ hàng chưa
                try:
                    cart_item = CartItem.objects.get(cart=cart, dish=dish)
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, f"Đã tăng số lượng {dish.name} trong giỏ hàng")
                except CartItem.DoesNotExist:
                    # Nếu món ăn chưa có trong giỏ, tạo mới
                    CartItem.objects.create(cart=cart, dish=dish, quantity=1)
                    messages.success(request, f"Đã thêm {dish.name} vào giỏ hàng")
                
                # Chuyển đến trang giỏ hàng
                return redirect('view_cart')
                
        elif 'form' not in context and request.user.is_authenticated:
            # Hiển thị form đặt hàng khi trang được tải lần đầu
            profile = Profile.objects.get(user=request.user)
            
            # Kiểm tra xem khách hàng có địa chỉ giao hàng không
            has_address = DeliveryAddress.objects.filter(customer=profile).exists()
            
            if not has_address:
                context['address_required'] = True
            else:
                context['can_order'] = True
            
    return render(request, "dish.html", context)

def payment_done(request):
    # Lấy order_id từ session hoặc từ query parameter
    order_id = request.session.get('order_id')
    paypal_invoice = request.GET.get('invoice')
    
    # Nếu không có order_id trong session, thử lấy từ invoice của PayPal
    if not order_id and paypal_invoice:
        order_id = paypal_invoice
        
    # Nếu vẫn không có order_id, hiển thị lỗi
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('index')
    
    try:
        order = Order.objects.get(id=order_id)
        order.status = True
        order.save()
        
        # Đảm bảo tất cả món ăn trong đơn hàng được liên kết với nhà hàng
        restaurant = Restaurant.objects.first()
        if restaurant:
            for order_item in OrderItem.objects.filter(order=order):
                if not order_item.dish.restaurant:
                    order_item.dish.restaurant = restaurant
                    order_item.dish.save()
        
        # Tạo đơn hàng giao hàng
        try:
            profile = Profile.objects.get(user=request.user)
            # Lấy địa chỉ mặc định của khách hàng
            default_address = DeliveryAddress.objects.filter(customer=profile, is_default=True).first()
            
            if not default_address:
                # Nếu không có địa chỉ mặc định, thử lấy địa chỉ đầu tiên
                default_address = DeliveryAddress.objects.filter(customer=profile).first()
            
            if default_address:
                # Tính thời gian dự kiến giao hàng (1 giờ kể từ khi đặt hàng)
                est_delivery_time = datetime.now() + timedelta(hours=1)
                
                # Tìm người giao hàng đang rảnh và không có đơn hàng đang giao
                # Lấy tất cả shipper có trạng thái available
                available_shippers = Shipper.objects.filter(availability_status=True)
                available_shipper = None
                
                # Kiểm tra từng shipper có đơn hàng đang giao hay không
                for shipper in available_shippers:
                    # Kiểm tra xem shipper này có đơn hàng đang giao không
                    # Các trạng thái đơn hàng đang giao: Đã xác nhận, Đang chuẩn bị, Sẵn sàng lấy hàng, Đã lấy hàng, Đang giao
                    active_deliveries = Delivery.objects.filter(
                        shipper=shipper,
                        status__in=['CO', 'PR', 'RP', 'PU', 'OW']
                    ).count()
                    
                    # Nếu shipper không có đơn hàng đang giao, chọn shipper này
                    if active_deliveries == 0:
                        available_shipper = shipper
                        print(f"Found shipper without active deliveries: {shipper.user.username}")
                        break
                
                # Nếu tất cả shipper đều đang bận, chọn shipper đầu tiên có trạng thái available
                if not available_shipper and available_shippers.exists():
                    available_shipper = available_shippers.first()
                    print(f"All shippers have active deliveries, using first available: {available_shipper.user.username}")
                
                # Nếu không có shipper available, lấy shipper đầu tiên trong hệ thống
                if not available_shipper:
                    available_shipper = Shipper.objects.first()
                    print("No available shippers, using first shipper in system")
                
                if available_shipper:
                    # Tạo đơn hàng giao hàng
                    delivery = Delivery.objects.create(
                        order=order,
                        shipper=available_shipper,
                        delivery_address=default_address,
                        status='CO',  # Sử dụng string chính xác thay vì DeliveryStatus.CONFIRMED
                        estimated_delivery_time=est_delivery_time,
                        delivery_notes="Đơn hàng mới từ thanh toán trực tuyến"
                    )
                    
                    # Tạo log theo dõi đầu tiên
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        status='CO',  # Sử dụng string chính xác thay vì DeliveryStatus.CONFIRMED 
                        notes="Đơn hàng đã được xác nhận và đang được chuẩn bị"
                    )
                    
                    # In thông tin debug
                    print(f"Created delivery: {delivery.id} for order: {order.id}, assigned to shipper: {available_shipper.user.username}")
                else:
                    print("Error: No shippers available in the system")
            
        except Exception as e:
            # Xử lý lỗi (có thể ghi log hoặc thông báo cho admin)
            print(f"Error creating delivery: {str(e)}")
        
        return render(request, "payment_successfull.html")
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('index')

def payment_cancel(request):
    ## remove comment to delete cancelled order
    # order_id = request.session.get('order_id')
    # Order.objects.get(id=order_id).delete()

    return render(request, 'payment_failed.html')

# Chức năng liên quan đến người giao hàng
def register_shipper(request):
    context = {}
    if request.method == "POST":
        form = ShipperRegistrationForm(request.POST)
        if form.is_valid():
            # Tạo User
            user_data = {
                'username': form.cleaned_data['email'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            }
            user = User.objects.create_user(**user_data)
            
            # Tạo Shipper
            shipper = form.save(commit=False)
            shipper.user = user
            # Đảm bảo vehicle_type luôn là Xe máy
            shipper.vehicle_type = 'Xe máy'
            shipper.save()
            
            # Tạo Profile cho user để có thể truy cập dashboard
            profile = Profile(user=user, contact_number=form.cleaned_data.get('contact_number', ''))
            profile.save()
            
            context['status'] = f"Người giao hàng {user.first_name} đã đăng ký thành công! Vui lòng đăng nhập."
            return redirect('login')
        else:
            context['form'] = form
    else:
        form = ShipperRegistrationForm()
        context['form'] = form
    
    return render(request, 'register_shipper.html', context)

@login_required
def shipper_dashboard(request):
    context = {}
    try:
        shipper = Shipper.objects.get(user=request.user)
        context['shipper'] = shipper
        
        # Debug: In thông tin shipper
        print(f"Shipper: {shipper.user.username} (ID: {shipper.id})")
        
        # Lấy tất cả đơn giao hàng của shipper (không lọc status)
        all_deliveries = Delivery.objects.filter(shipper=shipper)
        
        # Debug: In ra tất cả đơn hàng tìm thấy
        print(f"Found {all_deliveries.count()} deliveries for this shipper")
        for d in all_deliveries:
            print(f"  - Delivery ID: {d.id}, Order ID: {d.order.id}, Status: {d.status}")
        
        # Get active deliveries - chỉ lấy đơn có status đang thực hiện
        active_deliveries = all_deliveries.filter(
            status__in=['CO', 'PR', 'RP', 'PU', 'OW']
        ).order_by('created_at')
        
        # Get completed deliveries
        completed_deliveries = all_deliveries.filter(
            status='DE'  # Đã giao hàng
        ).order_by('-actual_delivery_time')[:10]
        
        context['active_deliveries'] = active_deliveries
        context['completed_deliveries'] = completed_deliveries
        
        # Debug: In số lượng đơn active để xác nhận
        print(f"Active deliveries: {active_deliveries.count()}")
        print(f"Completed deliveries: {completed_deliveries.count()}")
        
        # Availability form
        if request.method == "POST":
            form = ShipperAvailabilityForm(request.POST, instance=shipper)
            if form.is_valid():
                form.save()
                messages.success(request, "Trạng thái của bạn đã được cập nhật!")
        else:
            form = ShipperAvailabilityForm(instance=shipper)
        
        context['availability_form'] = form
        
        # Đảm bảo profile tồn tại cho người dùng hiện tại
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={'contact_number': ''}
        )
        
    except Shipper.DoesNotExist:
        context['error'] = "Bạn không phải là người giao hàng"
        print("Error: User is not a shipper")
    
    return render(request, 'shipper_dashboard.html', context)

@login_required
def update_delivery_status(request, delivery_id):
    if request.method == "POST":
        try:
            shipper = Shipper.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, shipper=shipper)
            
            form = RestrictedDeliveryStatusForm(request.POST, instance=delivery)
            if form.is_valid():
                updated_delivery = form.save()
                
                # Create tracking log
                tracking_form = DeliveryTrackingForm(request.POST)
                if tracking_form.is_valid():
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        status=updated_delivery.status,
                        location=tracking_form.cleaned_data['location'],
                        notes=tracking_form.cleaned_data['notes']
                    )
                
                # Update actual delivery time if delivered
                if updated_delivery.status == 'DE':  # Đã giao hàng
                    updated_delivery.actual_delivery_time = datetime.now()
                    updated_delivery.save()
                    
                    # Update shipper stats
                    shipper.total_deliveries += 1
                    shipper.save()
                    
                    # Cập nhật trạng thái thanh toán của đơn hàng thành "Đã thanh toán"
                    order = updated_delivery.order
                    if not order.status:  # Nếu đơn hàng chưa được đánh dấu là đã thanh toán
                        order.status = True  # Đánh dấu là đã thanh toán
                        order.save()
                        messages.success(request, "Đơn hàng đã được giao thành công và đánh dấu là đã thanh toán!")
                    else:
                        messages.success(request, "Đơn hàng đã được giao thành công!")
                else:
                    messages.success(request, "Cập nhật trạng thái đơn hàng thành công!")
                
                return redirect('shipper_dashboard')
            else:
                messages.error(request, "Lỗi cập nhật trạng thái đơn hàng")
        except Shipper.DoesNotExist:
            messages.error(request, "Bạn không có quyền cập nhật đơn hàng này")
    
    return redirect('shipper_dashboard')

@login_required
def delivery_detail(request, delivery_id):
    context = {}
    try:
        shipper = Shipper.objects.get(user=request.user)
        delivery = get_object_or_404(Delivery, id=delivery_id, shipper=shipper)
        
        context['delivery'] = delivery
        context['tracking_logs'] = delivery.tracking_logs.all().order_by('-timestamp')
        context['status_form'] = RestrictedDeliveryStatusForm(instance=delivery)
        context['tracking_form'] = DeliveryTrackingForm(initial={
            'status': delivery.status,
            'location': shipper.current_location
        })
        
        return render(request, 'delivery_detail.html', context)
    except Shipper.DoesNotExist:
        messages.error(request, "Bạn không có quyền xem đơn hàng này")
        return redirect('login')

# Chức năng quản lý giao hàng cho khách hàng
@login_required
def manage_addresses(request):
    context = {}
    try:
        profile = Profile.objects.get(user=request.user)
        addresses = DeliveryAddress.objects.filter(customer=profile)
        
        if request.method == "POST":
            form = DeliveryAddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.customer = profile
                
                # Check if this is the first address or marked as default
                if form.cleaned_data['is_default'] or not addresses.exists():
                    # Set all other addresses to non-default
                    addresses.update(is_default=False)
                
                address.save()
                messages.success(request, "Địa chỉ mới đã được lưu!")
                return redirect('manage_addresses')
        else:
            form = DeliveryAddressForm()
        
        context['addresses'] = addresses
        context['form'] = form
        
        return render(request, 'manage_addresses.html', context)
    except Profile.DoesNotExist:
        messages.error(request, "Bạn cần đăng nhập để quản lý địa chỉ")
        return redirect('login')

@login_required
def delete_address(request, address_id):
    if request.method == "POST":
        try:
            profile = Profile.objects.get(user=request.user)
            address = get_object_or_404(DeliveryAddress, id=address_id, customer=profile)
            
            # If this was the default address, set another one as default
            if address.is_default:
                other_address = DeliveryAddress.objects.filter(customer=profile).exclude(id=address_id).first()
                if other_address:
                    other_address.is_default = True
                    other_address.save()
            
            address.delete()
            messages.success(request, "Địa chỉ đã được xóa thành công")
        except Profile.DoesNotExist:
            messages.error(request, "Bạn không có quyền xóa địa chỉ này")
    
    return redirect('manage_addresses')

@login_required
def set_default_address(request, address_id):
    if request.method == "POST":
        try:
            profile = Profile.objects.get(user=request.user)
            
            # Set all addresses to non-default
            DeliveryAddress.objects.filter(customer=profile).update(is_default=False)
            
            # Set the selected address as default
            address = get_object_or_404(DeliveryAddress, id=address_id, customer=profile)
            address.is_default = True
            address.save()
            
            messages.success(request, "Địa chỉ mặc định đã được cập nhật")
        except Profile.DoesNotExist:
            messages.error(request, "Bạn không có quyền thực hiện hành động này")
    
    return redirect('manage_addresses')

@login_required
def track_order(request, order_id):
    context = {}
    from .forms import DeliveryReviewForm
    from .models import DeliveryReview
    try:
        profile = Profile.objects.get(user=request.user)
        # Tìm đơn hàng bằng ID, nhưng ưu tiên tìm bằng order_number trước
        try:
            # Thử tìm bằng order_number (nếu order_id là số nguyên)
            if str(order_id).isdigit():
                order = Order.objects.get(order_number=order_id, customer=profile)
            else:
                raise Order.DoesNotExist
        except Order.DoesNotExist:
            # Nếu không tìm thấy, tìm bằng id
            order = get_object_or_404(Order, id=order_id, customer=profile)
        
        try:
            delivery = Delivery.objects.get(order=order)
            tracking_logs = delivery.tracking_logs.all().order_by('-timestamp')
            
            # Tính tổng giá trị đơn hàng từ OrderItem
            order_items = OrderItem.objects.filter(order=order)
            total_amount = sum(item.price * item.quantity for item in order_items)
            
            context['order'] = order
            context['delivery'] = delivery
            context['tracking_logs'] = tracking_logs
            context['total_amount'] = total_amount
            context['order_items'] = order_items
            
            # Nếu đơn đã giao, cho phép đánh giá
            review = None
            if delivery.status == 'DE':
                try:
                    review = DeliveryReview.objects.get(delivery=delivery, customer=profile)
                except DeliveryReview.DoesNotExist:
                    review = None
                # Nếu đã có review, không cho submit nữa
                if review:
                    context['review'] = review
                elif request.method == 'POST' and 'submit_review' in request.POST:
                    review_form = DeliveryReviewForm(request.POST)
                    if review_form.is_valid():
                        new_review = review_form.save(commit=False)
                        new_review.delivery = delivery
                        new_review.customer = profile
                        new_review.save()
                        context['review'] = new_review
                        context['review_submitted'] = True
                    else:
                        context['review_form'] = review_form
                else:
                    context['review_form'] = DeliveryReviewForm()
            return render(request, 'track_order.html', context)
        except Delivery.DoesNotExist:
            # Tính tổng giá trị đơn hàng từ OrderItem
            order_items = OrderItem.objects.filter(order=order)
            total_amount = sum(item.price * item.quantity for item in order_items)
            
            context['order'] = order
            context['message'] = "Đơn hàng của bạn chưa được xử lý giao hàng"
            context['total_amount'] = total_amount
            context['order_items'] = order_items
            return render(request, 'track_order.html', context)
    except Profile.DoesNotExist:
        messages.error(request, "Bạn không có quyền xem đơn hàng này")
        return redirect('login')

# API để cập nhật vị trí hiện tại của người giao hàng
@login_required
def update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            location_name = data.get('location_name', '')
            
            if latitude and longitude:
                shipper = Shipper.objects.get(user=request.user)
                location_str = f"{location_name} ({latitude}, {longitude})"
                shipper.current_location = location_str
                shipper.save()
                
                # Update any active deliveries being handled by this shipper
                active_deliveries = Delivery.objects.filter(
                    shipper=shipper,
                    status=DeliveryStatus.ON_THE_WAY
                )
                
                for delivery in active_deliveries:
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        status=DeliveryStatus.ON_THE_WAY,
                        location=location_str,
                        notes="Cập nhật vị trí tự động"
                    )
                
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def is_restaurant_owner(user):
    """
    Kiểm tra xem người dùng có phải là chủ nhà hàng không (được admin chỉ định)
    """
    return Restaurant.objects.filter(owner=user).exists()

@login_required
@user_passes_test(is_restaurant_owner)
def restaurant_dashboard(request):
    context = {}
    
    # Get restaurant owned by current user
    restaurant = Restaurant.objects.get(owner=request.user)
    
    # Lấy tất cả OrderItems để tìm các đơn hàng có món ăn thuộc nhà hàng này
    all_order_items = OrderItem.objects.filter(
        dish__restaurant=restaurant
    ).select_related('order', 'dish').order_by('-order__ordered_on')
    
    # Liên kết tất cả món ăn với nhà hàng duy nhất
    for item in all_order_items:
        if not item.dish.restaurant:
            item.dish.restaurant = restaurant
            item.dish.save()
    
    # Get unique orders
    order_ids = list(set(all_order_items.values_list('order_id', flat=True)))
    
    # Lấy tất cả đơn hàng thuộc nhà hàng hiện tại
    restaurant_orders = Order.objects.filter(id__in=order_ids).order_by('-ordered_on')
    
    # Lấy tất cả các bản ghi giao hàng
    deliveries = Delivery.objects.filter(order__id__in=order_ids)
    
    # Tạo từ điển ánh xạ order_id -> delivery status để dễ tra cứu
    delivery_status_map = {}
    for delivery in deliveries:
        delivery_status_map[delivery.order_id] = delivery.status
    
    # Phân loại đơn hàng thành đang xử lý và đã hoàn thành
    processing_orders = []
    completed_orders = []
    
    for order in restaurant_orders:
        # Nếu đơn hàng có trong bản đồ delivery và status là 'DE' (Delivered)
        if order.id in delivery_status_map and delivery_status_map[order.id] == 'DE':
            completed_orders.append(order)
        else:
            # Nếu đơn hàng không có delivery hoặc có nhưng chưa Delivered
            processing_orders.append(order)
    
    # Chuyển danh sách thành QuerySet để sử dụng trong template
    processing_orders_ids = [order.id for order in processing_orders]
    completed_orders_ids = [order.id for order in completed_orders]
    
    processing_orders = Order.objects.filter(id__in=processing_orders_ids).order_by('-ordered_on')
    completed_orders = Order.objects.filter(id__in=completed_orders_ids).order_by('-ordered_on')
    
    # Lấy chi tiết đơn hàng 
    completed_order_items = all_order_items
    
    # Đếm tổng số đơn hàng của nhà hàng
    restaurant_order_count = OrderItem.objects.filter(
        dish__restaurant=restaurant
    ).values('order').distinct().count()
    
    # Calculate revenue from restaurant's orders
    restaurant_revenue = sum(item.price * item.quantity for item in all_order_items)
    
    # Đếm số đơn hàng đang giao (đã có shipper nhưng chưa delivered)
    delivering_count = deliveries.exclude(status='DE').exclude(status='CA').count()
    
    context.update({
        'restaurant': restaurant,
        'orders': processing_orders,
        'order_items': all_order_items,
        'completed_orders': completed_orders,
        'completed_order_items': completed_order_items,
        'deliveries': deliveries,
        'delivering_count': delivering_count,  # Số đơn đang giao thực tế
        'order_count': restaurant_order_count,
        'revenue': restaurant_revenue
    })
    
    # Đảm bảo profile tồn tại cho người dùng hiện tại
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'contact_number': ''}
    )
    
    return render(request, 'restaurant_dashboard.html', context)

def chatbot(request):
    return render(request, 'chatbot.html')

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            # Lưu original message để hiển thị và chuyển thành lowercase để so sánh
            original_message = data.get('message', '')
            user_message = original_message.lower()
            
            # Get menu data to provide context
            try:
                # Truy vấn database để lấy thông tin
                dishes = Dish.objects.filter(is_available=True)
                
                # Định nghĩa từ khóa và câu trả lời - Sử dụng lowercase để so sánh
                keywords_responses = {
                    "chào": "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn hoặc dịch vụ của chúng tôi?",
                    "hello": "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn hoặc dịch vụ của chúng tôi?",
                    "hi": "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn hoặc dịch vụ của chúng tôi?",
                    "thực đơn": "Thực đơn của FoodZone có nhiều món đặc sắc như phở bò, cơm tấm, bún chả, bánh xèo, gỏi cuốn và nhiều món Á - Âu khác.",
                    "tư vấn": "Tôi có thể tư vấn cho bạn về thực đơn, chi tiết món ăn, giá cả, khuyến mãi và cách đặt món. Bạn quan tâm đến điều gì?",
                    "khuyến mãi": "Hiện tại FoodZone đang có chương trình giảm giá cho hầu hết các món ăn. Các món đồ uống được giảm 20%, các món ăn chính được giảm 10-15%.",
                    "đặt hàng": "Để đặt hàng, bạn có thể chọn món ăn trên trang web và thanh toán trực tuyến, hoặc gọi điện đến số 0123 456 789."
                }
                
                # Xử lý đặc biệt cho menu - đọc từ database
                menu_keywords = ["thực đơn", "menu", "món ăn", "món", "food"]
                if any(keyword in user_message for keyword in menu_keywords):
                    response_text = "Thực đơn của FoodZone có các món ăn sau:\n"
                    for dish in dishes:
                        price_info = f"{dish.price} đồng"
                        if dish.discounted_price:
                            price_info += f" (giảm giá: {dish.discounted_price} đồng)"
                        response_text += f"- {dish.name}: {price_info}\n"
                    
                    return JsonResponse({'response': response_text})
                
                # Xử lý cho món ăn cụ thể
                hamburger_keywords = ["hamburger", "burger", "ham"]
                if any(keyword in user_message for keyword in hamburger_keywords):
                    bo_keywords = ["bò", "beef", "bo"]
                    ga_keywords = ["gà", "ga", "chicken"]
                    
                    if any(keyword in user_message for keyword in bo_keywords):
                        # Tìm kiếm hamburger bò trong database
                        hamburger_bo = None
                        for dish in dishes:
                            dish_name_lower = dish.name.lower()
                            if "hamburger" in dish_name_lower and "bò" in dish_name_lower:
                                hamburger_bo = dish
                                break
                        
                        if hamburger_bo:
                            response_text = f"Thông tin về Hamburger Bò:\n"
                            response_text += f"- Giá: {hamburger_bo.price} đồng"
                            if hamburger_bo.discounted_price:
                                response_text += f" (giảm giá: {hamburger_bo.discounted_price} đồng)\n"
                            else:
                                response_text += "\n"
                            response_text += "- Thành phần: Bánh mì tròn, thịt bò băm, phô mai, rau xà lách, cà chua, hành tây, sốt đặc biệt\n"
                            response_text += "- Đặc điểm: Hamburger bò của chúng tôi được làm từ 100% thịt bò tươi, không chứa chất bảo quản, và được nướng theo yêu cầu.\n"
                            response_text += "- Khuyến nghị: Món này phù hợp với người thích thịt bò và phô mai.\n"
                            response_text += "Bạn có muốn đặt món này không?"
                        else:
                            response_text = f"Thông tin về Hamburger Bò:\n"
                            response_text += f"- Giá: 30.000 đồng (giảm giá: 25.000 đồng)\n"
                            response_text += "- Thành phần: Bánh mì tròn, thịt bò băm, phô mai, rau xà lách, cà chua, hành tây, sốt đặc biệt\n"
                            response_text += "- Đặc điểm: Hamburger bò của chúng tôi được làm từ 100% thịt bò tươi, không chứa chất bảo quản, và được nướng theo yêu cầu.\n"
                            response_text += "- Khuyến nghị: Món này phù hợp với người thích thịt bò và phô mai.\n"
                            response_text += "Bạn có muốn đặt món này không?"
                        
                        return JsonResponse({'response': response_text})
                    
                    elif any(keyword in user_message for keyword in ga_keywords):
                        # Xử lý tương tự cho hamburger gà
                        response_text = f"Thông tin về Hamburger Gà:\n"
                        response_text += f"- Giá: 30.000 đồng (giảm giá: 25.000 đồng)\n"
                        response_text += "- Thành phần: Bánh mì tròn, thịt gà rán, phô mai, rau xà lách, cà chua, hành tây, sốt mayonnaise\n"
                        response_text += "- Đặc điểm: Hamburger gà của chúng tôi sử dụng thịt ức gà được tẩm ướp gia vị đặc biệt và rán giòn.\n"
                        response_text += "- Khuyến nghị: Món này phù hợp với người thích thịt gà và ít calo hơn hamburger bò.\n"
                        response_text += "Bạn có muốn đặt món này không?"
                        return JsonResponse({'response': response_text})
                    else:
                        # Thông tin chung về hamburger
                        response_text = "FoodZone có các loại hamburger sau:\n"
                        response_text += "1. Hamburger Bò: 30.000 đồng (giảm giá: 25.000 đồng)\n"
                        response_text += "2. Hamburger Gà: 30.000 đồng (giảm giá: 25.000 đồng)\n"
                        response_text += "3. Hamburger Hải sản: 35.000 đồng (giảm giá: 30.000 đồng)\n"
                        response_text += "4. Hamburger Chay: 25.000 đồng (giảm giá: 20.000 đồng)\n"
                        response_text += "Bạn muốn biết thêm chi tiết về loại hamburger nào?"
                        return JsonResponse({'response': response_text})
                
                # Xử lý tư vấn món ăn theo yêu cầu
                if "tư vấn" in user_message:
                    if any(x in user_message for x in ["món ngon", "món phổ biến", "món nào"]):
                        response_text = "Các món ăn phổ biến và được yêu thích nhất tại FoodZone là:\n"
                        response_text += "1. Hamburger Bò: Thơm ngon với thịt bò 100% tươi ngon\n"
                        response_text += "2. Pizza Hải Sản: Đa dạng hải sản tươi ngon với phô mai tan chảy\n"
                        response_text += "3. Gà Rán: Giòn bên ngoài, mềm và ngọt thịt bên trong\n"
                        response_text += "Bạn muốn biết thêm chi tiết về món nào?"
                        return JsonResponse({'response': response_text})
                    
                    if any(x in user_message for x in ["nước", "đồ uống"]):
                        response_text = "FoodZone có các đồ uống phổ biến như:\n"
                        response_text += "1. Pepsi: 19.000 đồng (giảm giá: 15.000 đồng)\n"
                        response_text += "2. Coca: 19.000 đồng (giảm giá: 15.000 đồng)\n"
                        response_text += "3. Trà đào: 25.000 đồng\n"
                        response_text += "4. Sinh tố các loại: 35.000 đồng\n"
                        response_text += "Bạn thích đồ uống nào?"
                        return JsonResponse({'response': response_text})
                
                # Xử lý đặc biệt cho giá cả
                if "giá" in user_message or "bao nhiêu" in user_message:
                    response_text = "Giá các món ăn tại FoodZone:\n"
                    for dish in dishes:
                        price_info = f"{dish.price} đồng"
                        if dish.discounted_price:
                            price_info += f" (giảm giá: {dish.discounted_price} đồng)"
                        response_text += f"- {dish.name}: {price_info}\n"
                    
                    return JsonResponse({'response': response_text})
                
                # Xử lý đặc biệt cho đội ngũ
                if "đầu bếp" in user_message or "đội ngũ" in user_message:
                    try:
                        team_members = Team.objects.all()
                        response_text = "Đội ngũ đầu bếp tại FoodZone:\n"
                        for member in team_members:
                            response_text += f"- {member.name}: {member.designation}\n"
                    except:
                        response_text = "Đội ngũ đầu bếp của chúng tôi được dẫn dắt bởi Bếp trưởng Nguyễn Văn A với hơn 15 năm kinh nghiệm trong ngành ẩm thực."
                    
                    return JsonResponse({'response': response_text})
                
                # Tìm kiếm trong tất cả các món ăn từ database
                for dish in dishes:
                    dish_name_lower = dish.name.lower()
                    if dish_name_lower in user_message:
                        response_text = f"Thông tin về món {dish.name}:\n"
                        response_text += f"- Giá: {dish.price} đồng"
                        if dish.discounted_price:
                            response_text += f" (giảm giá: {dish.discounted_price} đồng)\n"
                        else:
                            response_text += "\n"
                        if hasattr(dish, 'ingredients') and dish.ingredients:
                            response_text += f"- Thành phần: {dish.ingredients}\n"
                        if hasattr(dish, 'description') and dish.description:
                            response_text += f"- Mô tả: {dish.description}\n"
                        response_text += "Bạn có muốn đặt món này không?"
                        return JsonResponse({'response': response_text})
                
                # Tìm phản hồi cho câu hỏi của người dùng từ danh sách từ khóa cố định
                response_text = None
                for keyword, response in keywords_responses.items():
                    if keyword in user_message:
                        response_text = response
                        break
                
                # Nếu không tìm thấy phản hồi phù hợp, sử dụng phản hồi mặc định
                if not response_text:
                    response_text = "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn, giá cả, đội ngũ đầu bếp hoặc dịch vụ của chúng tôi?"
                
                # Return the response as JSON
                return JsonResponse({'response': response_text})
                
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                # Fallback to simple responses if database queries fail
                fallback_responses = {
                    "chào": "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn hoặc dịch vụ của chúng tôi?",
                    "hello": "Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn hoặc dịch vụ của chúng tôi?",
                    "thực đơn": "Thực đơn của FoodZone có nhiều món đặc sắc như phở bò, cơm tấm, bún chả, bánh xèo, gỏi cuốn và nhiều món Á - Âu khác.",
                    "giá": "Giá các món ăn tại FoodZone từ 30.000đ đến 150.000đ tùy món.",
                    "đầu bếp": "Đội ngũ đầu bếp của chúng tôi được dẫn dắt bởi Bếp trưởng Nguyễn Văn A với hơn 15 năm kinh nghiệm trong ngành ẩm thực.",
                    "địa chỉ": "FoodZone tọa lạc tại 123 Đường ABC, Quận XYZ, Thành phố HCM.",
                    "đặt bàn": "Để đặt bàn tại FoodZone, vui lòng gọi số 0123 456 789."
                }
                
                # Check if any keyword matches the user message
                for keyword, response in fallback_responses.items():
                    if keyword in user_message:
                        return JsonResponse({'response': response})
                
                # Default fallback response
                return JsonResponse({'response': 'Xin chào! Tôi là trợ lý ảo của FoodZone. Bạn cần tôi tư vấn gì về thực đơn, giá cả, đội ngũ đầu bếp hoặc dịch vụ của chúng tôi?'})
        
        except Exception as e:
            # Log the error with more details
            import traceback
            print(f"Error in chatbot query: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Return a simple error message
            return JsonResponse({'response': 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.'}, status=500)
    
    # Handle non-POST requests
    return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)

def register_restaurant(request):
    """
    Chức năng này không còn được sử dụng - Chỉ admin mới có thể tạo tài khoản nhà hàng
    """
    # Trả về lỗi hoặc thông báo
    return HttpResponseForbidden("Chỉ admin mới có thể tạo tài khoản nhà hàng. Vui lòng liên hệ với quản trị viên hệ thống.")

@require_POST
def add_to_cart(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    
    # Đảm bảo món ăn được liên kết với nhà hàng duy nhất
    if not dish.restaurant:
        # Lấy nhà hàng duy nhất trong hệ thống
        restaurant = Restaurant.objects.first()
        if restaurant:
            dish.restaurant = restaurant
            dish.save()
    
    # Lấy hoặc tạo giỏ hàng cho người dùng
    cart = None
    if request.user.is_authenticated:
        # Kiểm tra xem có giỏ hàng active trong session không
        active_cart_id = request.session.get('active_cart_id')
        if active_cart_id:
            try:
                cart = Cart.objects.get(id=active_cart_id, user=request.user)
            except Cart.DoesNotExist:
                # Nếu không tìm thấy, tạo mới
                cart = Cart.objects.create(user=request.user)
        else:
            # Tìm giỏ hàng hiện có hoặc tạo mới
            cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Kiểm tra xem có giỏ hàng active trong session không
        active_cart_id = request.session.get('active_cart_id')
        if active_cart_id:
            try:
                cart = Cart.objects.get(id=active_cart_id, session_key=session_key)
            except Cart.DoesNotExist:
                # Nếu không tìm thấy, tạo mới
                cart = Cart.objects.create(session_key=session_key)
        else:
            # Tìm giỏ hàng hiện có hoặc tạo mới
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        request.session['active_cart_id'] = cart.id
    
    # Đảm bảo cart không phải là None
    if not cart:
        if request.user.is_authenticated:
            cart = Cart.objects.create(user=request.user)
        else:
            cart = Cart.objects.create(session_key=request.session.session_key)
        request.session['active_cart_id'] = cart.id
    
    # Kiểm tra xem món ăn đã có trong giỏ hàng chưa
    try:
        cart_item = CartItem.objects.get(cart=cart, dish=dish)
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Đã tăng số lượng {dish.name} trong giỏ hàng")
    except CartItem.DoesNotExist:
        # Nếu món ăn chưa có trong giỏ, tạo mới
        CartItem.objects.create(cart=cart, dish=dish, quantity=1)
        messages.success(request, f"Đã thêm {dish.name} vào giỏ hàng")
    
    # Lưu ID giỏ hàng vào session để sử dụng sau này
    request.session['active_cart_id'] = cart.id
    
    return redirect('view_cart')

def view_cart(request):
    # Khởi tạo giỏ hàng cho người dùng
    cart = None
    if request.user.is_authenticated:
        # Kiểm tra xem có giỏ hàng active trong session không
        active_cart_id = request.session.get('active_cart_id')
        if active_cart_id:
            try:
                cart = Cart.objects.get(id=active_cart_id, user=request.user)
            except Cart.DoesNotExist:
                # Nếu không tìm thấy, tạo mới
                cart = Cart.objects.create(user=request.user)
                request.session['active_cart_id'] = cart.id
        else:
            # Tìm giỏ hàng hiện có hoặc tạo mới
            cart, created = Cart.objects.get_or_create(user=request.user)
            request.session['active_cart_id'] = cart.id
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        # Kiểm tra xem có giỏ hàng active trong session không
        active_cart_id = request.session.get('active_cart_id')
        if active_cart_id:
            try:
                cart = Cart.objects.get(id=active_cart_id, session_key=session_key)
            except Cart.DoesNotExist:
                # Nếu không tìm thấy, tạo mới
                cart = Cart.objects.create(session_key=session_key)
                request.session['active_cart_id'] = cart.id
        else:
            # Tìm giỏ hàng hiện có hoặc tạo mới
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            request.session['active_cart_id'] = cart.id
    
    # Đảm bảo cart không phải là None
    if not cart:
        if request.user.is_authenticated:
            cart = Cart.objects.create(user=request.user)
        else:
            cart = Cart.objects.create(session_key=request.session.session_key)
        request.session['active_cart_id'] = cart.id
    
    items = cart.items.all() if cart else []
    
    # Tính tổng tiền
    total_price = 0
    for item in items:
        # Xử lý trường hợp discounted_price là None
        unit_price = item.dish.discounted_price if item.dish.discounted_price else item.dish.price
        total_price += unit_price * item.quantity
    
    # Đếm tổng số lượng món trong giỏ
    total_items = sum(item.quantity for item in items) if items else 0
    
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
        'total_items': total_items
    }
    
    return render(request, 'cart.html', context)

@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('view_cart')

@require_POST
def update_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            # Nếu số lượng về 0 thì xóa món khỏi giỏ
            cart_item.delete()
            return redirect('view_cart')
    
    cart_item.save()
    return redirect('view_cart')

@login_required
def checkout_cart(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        
        # Lấy giỏ hàng từ session
        cart = None
        active_cart_id = request.session.get('active_cart_id')
        
        if active_cart_id:
            try:
                cart = Cart.objects.get(id=active_cart_id, user=request.user)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=request.user)
                request.session['active_cart_id'] = cart.id
        else:
            cart, created = Cart.objects.get_or_create(user=request.user)
            request.session['active_cart_id'] = cart.id
        
        if not cart or not cart.items.exists():
            messages.error(request, "Giỏ hàng của bạn đang trống!")
            return redirect('view_cart')
        
        # Kiểm tra xem người dùng có địa chỉ giao hàng không
        has_address = DeliveryAddress.objects.filter(customer=profile).exists()
        if not has_address:
            messages.error(request, "Bạn cần thêm địa chỉ giao hàng trước khi đặt hàng")
            return redirect('manage_addresses')
        
        # Kiểm tra xem có đơn hàng cũ chưa thanh toán không
        order = None
        order_id = request.session.get('order_id')
        
        if order_id:
            try:
                # Tìm đơn hàng cũ chưa thanh toán
                existing_order = Order.objects.get(
                    id=order_id, 
                    customer=profile,
                    status=False  # Chưa thanh toán
                )
                
                # Nếu có, xóa tất cả các item cũ trong đơn hàng
                OrderItem.objects.filter(order=existing_order).delete()
                
                # Sử dụng lại đơn hàng cũ
                order = existing_order
                print(f"[CHECKOUT] Sử dụng lại đơn hàng #{order.order_number}")
            except Order.DoesNotExist:
                # Nếu không tìm thấy đơn hàng cũ hoặc đơn hàng đã thanh toán
                order_id = None
        
        # Nếu không có đơn hàng cũ hợp lệ, tạo đơn hàng mới
        if not order:
            # Gán số đơn hàng chính thức ngay khi tạo đơn hàng
            last_order = Order.objects.filter(order_number__isnull=False).order_by('-order_number').first()
            next_order_number = 1
            if last_order:
                next_order_number = last_order.order_number + 1
                
            order = Order(
                customer=profile,
                status=False,  # Chưa thanh toán
                payment_method='paypal',  # Mặc định là PayPal, có thể thay đổi sau
                order_number=next_order_number  # Gán số đơn hàng ngay khi tạo
            )
            order.save()
            print(f"[CHECKOUT] Tạo đơn hàng mới #{order.order_number}")
        
        # Log thông tin
        print(f"[CHECKOUT] Đang xử lý đơn hàng #{order.order_number} cho khách hàng {profile.user.username}")
        print(f"[CHECKOUT] Giỏ hàng có {cart.items.count()} món")
        
        # Tính tổng tiền
        total_amount = 0
        
        # Đảm bảo nhà hàng duy nhất
        restaurant = Restaurant.objects.first()
        
        # Tạo OrderItem cho từng món trong giỏ
        for cart_item in cart.items.all():
            # Liên kết món ăn với nhà hàng nếu chưa có
            if not cart_item.dish.restaurant and restaurant:
                cart_item.dish.restaurant = restaurant
                cart_item.dish.save()
                
            item_price = cart_item.dish.discounted_price or cart_item.dish.price
            item_total = item_price * cart_item.quantity
            total_amount += item_total
            
            # Tạo OrderItem
            OrderItem.objects.create(
                order=order,
                dish=cart_item.dish,
                quantity=cart_item.quantity,
                price=item_price
            )
            
            # Log thông tin
            print(f"[CHECKOUT] Thêm món {cart_item.dish.name} x{cart_item.quantity} vào đơn hàng #{order.order_number}")
        
        # Lưu thông tin đơn hàng vào session
        request.session['order_id'] = order.id
        request.session['cart_id'] = cart.id
        
        # Thông báo đã tạo đơn hàng thành công
        messages.success(request, f"Đã tạo đơn hàng #{order.order_number} với {cart.items.count()} món")
        
        # Chuyển đến trang chọn phương thức thanh toán
        return redirect('process_cart_payment')
        
    # Nếu không phải POST hoặc không có món nào trong giỏ
    return redirect('view_cart')

def process_cart_payment(request):
    # Lấy thông tin đơn hàng từ session
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('view_cart')
    
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        
        if not order_items.exists():
            messages.error(request, "Đơn hàng không có món ăn nào!")
            return redirect('view_cart')
        
        # Tính tổng tiền
        total_amount = sum(item.price * item.quantity for item in order_items)
        
        # Tạo danh sách tên món
        item_names = [f"{item.dish.name} x{item.quantity}" for item in order_items]
        
        host = request.get_host()
        
        # Tạo payload cho PayPal
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total_amount,
            'item_name': f'Đơn hàng FoodZone #{order.id}',
            'invoice': str(order.id),  # Sử dụng order.id thay vì uuid để có thể khôi phục đơn hàng
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("cart_payment_done")}',
            'cancel_return': f'http://{host}{reverse("cart_payment_cancel")}',
        }
        
        # Tạo form thanh toán PayPal
        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {
            'form': form,
            'order': order,
            'order_items': order_items,
            'total_amount': total_amount,
            'item_names': item_names
        }
        
        return render(request, 'process_cart_payment.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('view_cart')

def process_payment_method(request):
    # Lấy thông tin đơn hàng từ session
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('view_cart')
    
    try:
        order = Order.objects.get(id=order_id)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            
            if payment_method == 'cash':
                # Cập nhật phương thức thanh toán của đơn hàng
                order.payment_method = 'cash'
                order.save()
                print(f"[PAYMENT_METHOD] Đã chuyển đơn hàng #{order.order_number} sang phương thức thanh toán COD")
                
                # Chuyển hướng đến trang xác nhận đơn hàng COD
                return redirect('cash_payment_confirm')
            else:
                # Đây là thanh toán PayPal
                order.payment_method = 'paypal'
                order.save()
                print(f"[PAYMENT_METHOD] Đã chuyển đơn hàng #{order.order_number} sang phương thức thanh toán PayPal")
                # Reload trang thanh toán để hiển thị PayPal
                return redirect('process_cart_payment')
        else:
            return redirect('process_cart_payment')
        
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('view_cart')

def cash_payment_confirm(request):
    # Lấy thông tin đơn hàng từ session
    order_id = request.session.get('order_id')
    cart_id = request.session.get('cart_id')
    
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('view_cart')
    
    try:
        # Cập nhật đơn hàng
        order = Order.objects.get(id=order_id)
        # Cập nhật phương thức thanh toán thành COD
        order.payment_method = 'cash'
        # Đơn hàng COD sẽ được đánh dấu là chưa thanh toán cho đến khi giao hàng
        order.status = False
        
        # Không cần gán lại order_number vì đã được gán khi tạo đơn hàng
        order.save()
        
        # Log thông tin
        print(f"[COD] Đơn hàng COD #{order.order_number} đã được tạo, đang chờ giao hàng")
        
        # Đảm bảo tất cả món ăn được liên kết với nhà hàng
        restaurant = Restaurant.objects.first()
        if restaurant:
            for order_item in OrderItem.objects.filter(order=order):
                if not order_item.dish.restaurant:
                    order_item.dish.restaurant = restaurant
                    order_item.dish.save()
        
        # Tạo thông tin giao hàng
        try:
            profile = Profile.objects.get(user=request.user)
            default_address = DeliveryAddress.objects.filter(customer=profile, is_default=True).first() or DeliveryAddress.objects.filter(customer=profile).first()
            
            if default_address:
                est_delivery_time = datetime.now() + timedelta(hours=1)
                
                # Tìm người giao hàng đang rảnh
                available_shipper = None
                available_shippers = Shipper.objects.filter(availability_status=True)
                
                for shipper in available_shippers:
                    active_deliveries = Delivery.objects.filter(
                        shipper=shipper,
                        status__in=['CO', 'PR', 'RP', 'PU', 'OW']
                    ).count()
                    
                    if active_deliveries == 0:
                        available_shipper = shipper
                        break
                
                if not available_shipper and available_shippers.exists():
                    available_shipper = available_shippers.first()
                
                if not available_shipper:
                    available_shipper = Shipper.objects.first()
                
                if available_shipper:
                    # Tạo đơn giao hàng
                    delivery = Delivery.objects.create(
                        order=order,
                        shipper=available_shipper,
                        delivery_address=default_address,
                        status='CO',  # Đã xác nhận
                        estimated_delivery_time=est_delivery_time,
                        delivery_notes="Đơn hàng COD mới"
                    )
                    
                    print(f"[COD] Đã tạo đơn giao hàng #{delivery.id} cho đơn hàng COD #{order.order_number}")
                    
                    # Tạo log tracking
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        status='CO',
                        notes="Đơn hàng đã được xác nhận và đang chuẩn bị giao"
                    )
                    
                    print(f"[COD] Đã tạo log tracking cho đơn hàng #{order.order_number}")
                    
                    # Xóa giỏ hàng sau khi đã hoàn tất đơn hàng COD
                    if cart_id:
                        try:
                            cart = Cart.objects.get(id=cart_id)
                            # Lưu lại số lượng món đã thanh toán để hiển thị thông báo
                            items_count = cart.items.count()
                            
                            # Xóa tất cả các món trong giỏ
                            cart.items.all().delete()
                            
                            # Xóa giỏ hàng
                            cart.delete()
                            
                            print(f"[COD] Đã xóa giỏ hàng ID #{cart_id} với {items_count} món sau khi hoàn tất đơn hàng COD")
                        except Cart.DoesNotExist:
                            print(f"[ERROR] Không tìm thấy giỏ hàng ID #{cart_id}")
                    
                    # Xóa session
                    if 'order_id' in request.session:
                        del request.session['order_id']
                    
                    if 'cart_id' in request.session:
                        del request.session['cart_id']
                        
                    if 'active_cart_id' in request.session:
                        del request.session['active_cart_id']
                    
                    # Thông báo đặt hàng thành công
                    messages.success(request, "Đặt hàng thành công! Đơn hàng COD của bạn đang được xử lý.")
                    
                    # Hiển thị trang xác nhận COD
                    return render(request, 'cash_payment_confirm.html', {'order': order, 'delivery': delivery})
        
        except Exception as e:
            print(f"[ERROR] Lỗi khi tạo thông tin giao hàng COD: {e}")
        
        # Nếu không có shipper hoặc xảy ra lỗi
        messages.error(request, "Đã xảy ra lỗi khi xử lý đơn hàng. Vui lòng thử lại sau.")
        return redirect('view_cart')
        
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('view_cart')

def cart_payment_done(request):
    # Lấy thông tin đơn hàng từ session hoặc từ query parameter
    order_id = request.session.get('order_id')
    payer_id = request.GET.get('PayerID')
    cart_id = request.session.get('cart_id')
    
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('view_cart')
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Cập nhật thông tin thanh toán
        order.payer_id = payer_id
        order.status = True  # Đánh dấu là đã thanh toán
        
        # Không cần gán lại order_number vì đã được gán khi tạo đơn hàng
        order.save()
        
        # Log thông tin
        print(f"[PAYMENT] Thanh toán thành công cho đơn hàng #{order.order_number}")
        
        # Đảm bảo tất cả món ăn được liên kết với nhà hàng
        restaurant = Restaurant.objects.first()
        if restaurant:
            for order_item in OrderItem.objects.filter(order=order):
                if not order_item.dish.restaurant:
                    order_item.dish.restaurant = restaurant
                    order_item.dish.save()
        
        # Tạo thông tin giao hàng
        try:
            profile = Profile.objects.get(user=request.user)
            default_address = DeliveryAddress.objects.filter(customer=profile, is_default=True).first() or DeliveryAddress.objects.filter(customer=profile).first()
            
            if default_address:
                est_delivery_time = datetime.now() + timedelta(hours=1)
                
                # Tìm người giao hàng đang rảnh
                available_shipper = None
                available_shippers = Shipper.objects.filter(availability_status=True)
                
                for shipper in available_shippers:
                    active_deliveries = Delivery.objects.filter(
                        shipper=shipper,
                        status__in=['CO', 'PR', 'RP', 'PU', 'OW']
                    ).count()
                    
                    if active_deliveries == 0:
                        available_shipper = shipper
                        break
                
                if not available_shipper and available_shippers.exists():
                    available_shipper = available_shippers.first()
                
                if not available_shipper:
                    available_shipper = Shipper.objects.first()
                
                if available_shipper:
                    # Kiểm tra xem đơn hàng đã có thông tin giao hàng chưa
                    delivery = None
                    try:
                        delivery = Delivery.objects.get(order=order)
                        delivery.shipper = available_shipper
                        delivery.delivery_address = default_address
                        delivery.status = 'CO'  # Đã xác nhận
                        delivery.estimated_delivery_time = est_delivery_time
                        delivery.save()
                        print(f"[PAYMENT] Đã cập nhật thông tin giao hàng cho đơn hàng #{order.order_number}")
                    except Delivery.DoesNotExist:
                        # Tạo đơn giao hàng mới
                        delivery = Delivery.objects.create(
                            order=order,
                            shipper=available_shipper,
                            delivery_address=default_address,
                            status='CO',  # Đã xác nhận
                            estimated_delivery_time=est_delivery_time,
                            delivery_notes="Đơn hàng mới từ thanh toán giỏ hàng"
                        )
                        print(f"[PAYMENT] Đã tạo đơn giao hàng #{delivery.id} cho đơn hàng #{order.order_number}")
                    
                    # Tạo log tracking nếu chưa có
                    if not DeliveryTracking.objects.filter(delivery=delivery, status='CO').exists():
                        DeliveryTracking.objects.create(
                            delivery=delivery,
                            status='CO',
                            notes="Đơn hàng đã được xác nhận và đang chuẩn bị giao"
                        )
                        print(f"[PAYMENT] Đã tạo log tracking cho đơn hàng #{order.order_number}")
        except Exception as e:
            print(f"[ERROR] Lỗi khi tạo thông tin giao hàng: {e}")
        
        # Xóa giỏ hàng sau khi đã thanh toán thành công
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                # Lưu lại số lượng món đã thanh toán để hiển thị thông báo
                items_count = cart.items.count()
                
                # Xóa tất cả các món trong giỏ
                cart.items.all().delete()
                
                # Xóa giỏ hàng
                cart.delete()
                
                print(f"[PAYMENT] Đã xóa giỏ hàng ID #{cart_id} với {items_count} món sau khi hoàn tất đơn hàng")
            except Cart.DoesNotExist:
                print(f"[ERROR] Không tìm thấy giỏ hàng ID #{cart_id}")
        
        # Xóa session
        if 'order_id' in request.session:
            del request.session['order_id']
        
        if 'cart_id' in request.session:
            del request.session['cart_id']
            
        if 'active_cart_id' in request.session:
            del request.session['active_cart_id']
        
        messages.success(request, "Thanh toán thành công! Đơn hàng của bạn đang được xử lý.")
        
        return render(request, 'payment_done.html', {'order': order})
        
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('view_cart')

def cart_payment_cancel(request):
    # Lưu lại order_id để hiển thị thông báo
    order_id = request.session.get('order_id')
    
    # Xóa session để người dùng có thể tạo đơn hàng mới
    if 'order_id' in request.session:
        del request.session['order_id']
    
    # Hiển thị thông báo
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            messages.warning(request, f"Bạn đã hủy thanh toán đơn hàng #{order.order_number}. Hệ thống sẽ tạo đơn hàng mới khi bạn tiếp tục thanh toán.")
        except Order.DoesNotExist:
            messages.warning(request, "Bạn đã hủy thanh toán. Hệ thống sẽ tạo đơn hàng mới khi bạn tiếp tục thanh toán.")
    else:
        messages.warning(request, "Bạn đã hủy thanh toán. Hệ thống sẽ tạo đơn hàng mới khi bạn tiếp tục thanh toán.")
    
    return render(request, 'payment_failed.html')

@login_required
@user_passes_test(is_restaurant_owner)
def manage_dishes(request):
    """Hiển thị danh sách món ăn của nhà hàng để quản lý"""
    restaurant = Restaurant.objects.get(owner=request.user)
    dishes = Dish.objects.filter(restaurant=restaurant)
    
    context = {
        'dishes': dishes,
        'restaurant': restaurant,
    }
    return render(request, 'manage_dishes.html', context)

@login_required
@user_passes_test(is_restaurant_owner)
def add_dish(request):
    """Thêm món ăn mới"""
    restaurant = Restaurant.objects.get(owner=request.user)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            dish = form.save(commit=False)
            dish.restaurant = restaurant
            dish.save()
            return redirect('manage_dishes')
    else:
        form = DishForm()
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'title': 'Thêm món ăn mới'
    }
    return render(request, 'dish_form.html', context)

@login_required
@user_passes_test(is_restaurant_owner)
def edit_dish(request, dish_id):
    """Chỉnh sửa món ăn"""
    restaurant = Restaurant.objects.get(owner=request.user)
    dish = get_object_or_404(Dish, id=dish_id, restaurant=restaurant)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            return redirect('manage_dishes')
    else:
        form = DishForm(instance=dish)
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'dish': dish,
        'title': 'Chỉnh sửa món ăn'
    }
    return render(request, 'dish_form.html', context)

@login_required
@user_passes_test(is_restaurant_owner)
def delete_dish(request, dish_id):
    """Xóa món ăn"""
    restaurant = Restaurant.objects.get(owner=request.user)
    dish = get_object_or_404(Dish, id=dish_id, restaurant=restaurant)
    
    if request.method == 'POST':
        dish.delete()
        return redirect('manage_dishes')
    
    context = {
        'dish': dish,
        'restaurant': restaurant,
    }
    return render(request, 'delete_dish_confirm.html', context)

@login_required
@user_passes_test(is_restaurant_owner)
def restaurant_order_detail(request, order_id):
    """Hiển thị chi tiết đơn hàng cho chủ nhà hàng"""
    restaurant = Restaurant.objects.get(owner=request.user)
    
    # Tìm đơn hàng bằng order_number trước, nếu không được thì tìm bằng id
    try:
        # Thử tìm bằng order_number (nếu order_id là số nguyên)
        if str(order_id).isdigit():
            order = Order.objects.get(order_number=order_id)
        else:
            raise Order.DoesNotExist
    except Order.DoesNotExist:
        # Nếu không tìm thấy, tìm bằng id
        order = get_object_or_404(Order, id=order_id)
    
    # Lấy các món ăn trong đơn hàng
    order_items = OrderItem.objects.filter(order=order)
    
    # Kiểm tra xem đơn hàng có món ăn nào thuộc nhà hàng này không
    restaurant_items = order_items.filter(dish__restaurant=restaurant)
    
    if not restaurant_items.exists():
        messages.error(request, "Đơn hàng này không thuộc nhà hàng của bạn")
        return redirect('restaurant_dashboard')
    
    # Tính tổng tiền
    total_amount = sum(item.price * item.quantity for item in restaurant_items)
    
    # Lấy thông tin giao hàng nếu có
    try:
        delivery = Delivery.objects.get(order=order)
        tracking_logs = delivery.tracking_logs.all().order_by('-timestamp')
        
        # Thêm form cập nhật trạng thái cho nhà hàng
        if request.method == "POST":
            status_form = RestaurantDeliveryStatusForm(request.POST, instance=delivery)
            if status_form.is_valid():
                updated_delivery = status_form.save()
                
                # Tạo log theo dõi
                DeliveryTracking.objects.create(
                    delivery=delivery,
                    status=updated_delivery.status,
                    notes=f"Trạng thái được cập nhật bởi nhà hàng: {updated_delivery.get_status_display()}"
                )
                
                messages.success(request, f"Đã cập nhật trạng thái đơn hàng thành: {updated_delivery.get_status_display()}")
                return redirect('restaurant_order_detail', order_id=order.order_number)
        else:
            status_form = RestaurantDeliveryStatusForm(instance=delivery)
        
        context = {
            'restaurant': restaurant,
            'order': order,
            'order_items': restaurant_items,
            'total_amount': total_amount,
            'delivery': delivery,
            'tracking_logs': tracking_logs,
            'status_form': status_form
        }
    except Delivery.DoesNotExist:
        delivery = None
        tracking_logs = None
        context = {
            'restaurant': restaurant,
            'order': order,
            'order_items': restaurant_items,
            'total_amount': total_amount,
            'delivery': delivery,
            'tracking_logs': tracking_logs
        }
    
    return render(request, 'restaurant_order_detail.html', context)

@login_required
@user_passes_test(is_restaurant_owner)
def update_restaurant_delivery_status(request, delivery_id):
    """Cập nhật trạng thái đơn hàng bởi nhà hàng"""
    if request.method == "POST":
        try:
            restaurant = Restaurant.objects.get(owner=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id)
            
            # Kiểm tra xem đơn hàng này có thuộc về nhà hàng không
            order_items = OrderItem.objects.filter(order=delivery.order)
            restaurant_items = order_items.filter(dish__restaurant=restaurant)
            
            if not restaurant_items.exists():
                messages.error(request, "Đơn hàng này không thuộc nhà hàng của bạn")
                return redirect('restaurant_dashboard')
            
            # Kiểm tra trạng thái hiện tại của đơn hàng
            if delivery.status in ['DE', 'CA']:
                messages.error(request, "Không thể cập nhật đơn hàng đã hoàn thành hoặc đã hủy")
                return redirect('restaurant_order_detail', order_id=delivery.order.order_number)
            
            # Kiểm tra xem trạng thái mới có nằm trong các trạng thái cho phép không
            allowed_statuses = ['CO', 'PR', 'RP']
            new_status = request.POST.get('status')
            if new_status not in allowed_statuses:
                messages.error(request, "Trạng thái này không được phép cập nhật bởi nhà hàng")
                return redirect('restaurant_order_detail', order_id=delivery.order.order_number)
            
            form = RestaurantDeliveryStatusForm(request.POST, instance=delivery)
            if form.is_valid():
                updated_delivery = form.save()
                
                # Tạo log theo dõi
                DeliveryTracking.objects.create(
                    delivery=delivery,
                    status=updated_delivery.status,
                    notes=f"Trạng thái được cập nhật bởi nhà hàng: {updated_delivery.get_status_display()}"
                )
                
                messages.success(request, f"Đã cập nhật trạng thái đơn hàng thành: {updated_delivery.get_status_display()}")
            else:
                messages.error(request, "Lỗi khi cập nhật trạng thái đơn hàng")
                
            return redirect('restaurant_order_detail', order_id=delivery.order.order_number)
        except Restaurant.DoesNotExist:
            messages.error(request, "Bạn không có quyền cập nhật đơn hàng này")
            return redirect('restaurant_dashboard')
    
    return redirect('restaurant_dashboard')

def process_paypal_payment(request):
    # Lấy thông tin đơn hàng từ session
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, "Không tìm thấy thông tin đơn hàng!")
        return redirect('view_cart')
    
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        
        if not order_items.exists():
            messages.error(request, "Đơn hàng không có món ăn nào!")
            return redirect('view_cart')
        
        # Tính tổng tiền
        total_amount = sum(item.price * item.quantity for item in order_items)
        
        # Tạo danh sách tên món
        item_names = [f"{item.dish.name} x{item.quantity}" for item in order_items]
        
        host = request.get_host()
        
        # Cập nhật phương thức thanh toán của đơn hàng
        order.payment_method = 'paypal'
        order.save()
        
        # Tạo payload cho PayPal
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total_amount,
            'item_name': f'Đơn hàng FoodZone #{order.order_number}',
            'invoice': str(order.id),
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("cart_payment_done")}',
            'cancel_return': f'http://{host}{reverse("cart_payment_cancel")}',
        }
        
        # Tạo form thanh toán PayPal
        form = PayPalPaymentsForm(initial=paypal_dict)
        
        # Chuyển hướng đến trang thanh toán PayPal
        return HttpResponse(f'''
            <html>
                <head>
                    <title>Chuyển hướng đến PayPal</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding-top: 50px;
                        }}
                        .loader {{
                            border: 5px solid #f3f3f3;
                            border-radius: 50%;
                            border-top: 5px solid #3498db;
                            width: 50px;
                            height: 50px;
                            animation: spin 1s linear infinite;
                            margin: 20px auto;
                        }}
                        @keyframes spin {{
                            0% {{ transform: rotate(0deg); }}
                            100% {{ transform: rotate(360deg); }}
                        }}
                    </style>
                </head>
                <body>
                    <h2>Đang chuyển hướng đến PayPal...</h2>
                    <div class="loader"></div>
                    <p>Vui lòng đợi trong giây lát...</p>
                    {form.render()}
                    <script>
                        document.forms[0].submit();
                    </script>
                </body>
            </html>
        ''')
        
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('view_cart')

@login_required
@user_passes_test(is_restaurant_owner)
def mark_order_as_delivered(request, order_number):
    """Đánh dấu đơn hàng đã giao hàng và đã thanh toán"""
    try:
        # Tìm đơn hàng theo order_number
        order = Order.objects.get(order_number=order_number)
        
        # Kiểm tra xem nhà hàng có quyền xử lý đơn hàng này không
        restaurant = Restaurant.objects.get(owner=request.user)
        order_items = OrderItem.objects.filter(order=order)
        restaurant_items = order_items.filter(dish__restaurant=restaurant)
        
        if not restaurant_items.exists():
            messages.error(request, "Đơn hàng này không thuộc nhà hàng của bạn")
            return redirect('restaurant_dashboard')
        
        # Kiểm tra xem đã có bản ghi Delivery chưa
        delivery = None
        try:
            delivery = Delivery.objects.get(order=order)
            # Cập nhật trạng thái delivery
            delivery.status = 'DE'  # Delivered
            delivery.actual_delivery_time = datetime.now()
            delivery.save()
            
            # Tạo log tracking mới
            DeliveryTracking.objects.create(
                delivery=delivery,
                status='DE',
                notes="Đơn hàng đã được đánh dấu là đã giao hàng"
            )
        except Delivery.DoesNotExist:
            # Tìm địa chỉ giao hàng và shipper
            profile = Profile.objects.get(user=order.customer.user)
            default_address = DeliveryAddress.objects.filter(customer=profile).first()
            shipper = Shipper.objects.first()
            
            if default_address and shipper:
                # Tạo bản ghi Delivery mới
                delivery = Delivery.objects.create(
                    order=order,
                    shipper=shipper,
                    delivery_address=default_address,
                    status='DE',  # Delivered
                    actual_delivery_time=datetime.now(),
                    delivery_notes="Đơn hàng đã giao"
                )
                
                # Tạo log tracking
                DeliveryTracking.objects.create(
                    delivery=delivery,
                    status='DE',
                    notes="Đơn hàng đã được đánh dấu là đã giao hàng"
                )
            else:
                messages.error(request, "Không thể tạo thông tin giao hàng - thiếu địa chỉ hoặc shipper")
                return redirect('restaurant_dashboard')
        
        # Đánh dấu đơn hàng là đã thanh toán
        order.status = True
        order.save()
        
        messages.success(request, f"Đơn hàng #{order.order_number} đã được đánh dấu là đã giao hàng và đã thanh toán")
        return redirect('restaurant_dashboard')
        
    except Order.DoesNotExist:
        messages.error(request, f"Không tìm thấy đơn hàng #{order_number}")
        return redirect('restaurant_dashboard')
    except Restaurant.DoesNotExist:
        messages.error(request, "Bạn không phải là chủ nhà hàng")
        return redirect('restaurant_dashboard')
