# ============================================================================================================================================
from django.contrib import admin
from django.urls import path, include
from myapp import views 
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('contact/',views.contact_us,name="contact"),
    path('about/',views.about,name="about"),
    path('team/',views.about,name="team"),
    path('dishes/',views.all_dishes,name="all_dishes"),
    path('register/',views.register,name="register"),
    path('check_user_exists/',views.check_user_exists,name="check_user_exist"),
    path('login/', views.signin, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('dish/<int:id>/', views.single_dish, name='dish'),

    # Chatbot URLs
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/query/', views.chatbot_query, name='chatbot_query'),

    # Chức năng người giao hàng
    path('register_shipper/', views.register_shipper, name='register_shipper'),
    path('shipper_dashboard/', views.shipper_dashboard, name='shipper_dashboard'),
    path('update_delivery_status/<int:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('delivery_detail/<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    path('update_location/', views.update_location, name='update_location'),
    
    # Chức năng nhà hàng - Hiện đã thêm lại URL nhưng trỏ đến hàm đã được sửa đổi
    path('register_restaurant/', views.register_restaurant, name='register_restaurant'),
    path('restaurant_dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant/order/<order_id>/', views.restaurant_order_detail, name='restaurant_order_detail'),
    path('restaurant/mark_delivered/<order_number>/', views.mark_order_as_delivered, name='mark_order_as_delivered'),
    path('restaurant/update_delivery_status/<int:delivery_id>/', views.update_restaurant_delivery_status, name='update_restaurant_delivery_status'),
    
    # Thêm URL quản lý món ăn
    path('restaurant/dishes/', views.manage_dishes, name='manage_dishes'),
    path('restaurant/dishes/add/', views.add_dish, name='add_dish'),
    path('restaurant/dishes/edit/<int:dish_id>/', views.edit_dish, name='edit_dish'),
    path('restaurant/dishes/delete/<int:dish_id>/', views.delete_dish, name='delete_dish'),
    
    # Chức năng địa chỉ giao hàng
    path('manage_addresses/', views.manage_addresses, name='manage_addresses'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('set_default_address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    
    # Theo dõi đơn hàng
    path('track_order/<order_id>/', views.track_order, name='track_order'),

    path('paypal/',include('paypal.standard.ipn.urls')),
    path('payment_done/', views.payment_done, name='payment_done'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Payment URL
    
    path('', include('myapp.urls')),

    # Giỏ hàng
    path('cart/add/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('cart/payment/', views.process_cart_payment, name='process_cart_payment'),
    path('cart/payment/method/', views.process_payment_method, name='process_payment_method'),
    path('cart/payment/cash/', views.cash_payment_confirm, name='cash_payment_confirm'),
    path('cart/payment/done/', views.cart_payment_done, name='cart_payment_done'),
    path('cart/payment/cancel/', views.cart_payment_cancel, name='cart_payment_cancel'),
    path('cart/payment/paypal/', views.process_paypal_payment, name='process_paypal_payment'),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)