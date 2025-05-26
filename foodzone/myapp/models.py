from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Contact Table"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/%Y/%m/%d")
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='dishes/%Y/%m/%d')
    ingredients = models.TextField()
    details = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField()
    discounted_price = models.FloatField(blank=True)
    is_available = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 

    class Meta:
        verbose_name_plural ="Dish Table"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profiles/%Y/%m/%d', null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(blank=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name_plural="Profile Table"

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('cash', 'Tiền mặt khi nhận hàng (COD)'),
    )
    
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    invoice_id = models.CharField(max_length=100, blank=True)
    payer_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='paypal')
    ordered_on = models.DateTimeField(auto_now_add=True)
    order_number = models.PositiveIntegerField(null=True, blank=True)  # Số đơn hàng chỉ được gán khi thanh toán thành công

    def __str__(self):
        if self.order_number:
            return f"Đơn hàng #{self.order_number} - {self.customer.user.first_name}"
        return f"Đơn hàng tạm #{self.id} - {self.customer.user.first_name}"

    class Meta:
        verbose_name_plural = "Order Table"

# Mô hình cho Shipper (Người giao hàng)
class Shipper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    availability_status = models.BooleanField(default=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=5.0)
    total_deliveries = models.IntegerField(default=0)
    joined_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.first_name
    
    class Meta:
        verbose_name_plural = "Shipper Table"

# Mô hình cho trạng thái giao hàng
class DeliveryStatus(models.TextChoices):
    PENDING = 'PE', 'Chờ xử lý'
    CONFIRMED = 'CO', 'Đã xác nhận'
    PREPARING = 'PR', 'Đang chuẩn bị'
    READY_FOR_PICKUP = 'RP', 'Sẵn sàng lấy hàng'
    PICKED_UP = 'PU', 'Đã lấy hàng'
    ON_THE_WAY = 'OW', 'Đang giao hàng'
    DELIVERED = 'DE', 'Đã giao hàng'
    CANCELLED = 'CA', 'Đã hủy'

# Mô hình cho địa chỉ giao hàng
class DeliveryAddress(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}"
    
    class Meta:
        verbose_name_plural = "Delivery Address Table"

# Mô hình cho đơn giao hàng
class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Delivery for Order #{self.order.id}"
    
    class Meta:
        verbose_name_plural = "Delivery Table"

# Mô hình cho tracking log
class DeliveryTracking(models.Model):
    delivery = models.ForeignKey(Delivery, related_name='tracking_logs', on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=DeliveryStatus.choices)
    location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tracking for Delivery #{self.delivery.id}: {self.get_status_display()}"
    
    class Meta:
        verbose_name_plural = "Delivery Tracking Table"
        ordering = ['-timestamp']

# Trạng thái đơn hàng
class OrderStatus(models.TextChoices):
    PENDING = 'PE', 'Chờ xử lý'
    CONFIRMED = 'CO', 'Đã xác nhận'
    PREPARING = 'PR', 'Đang chuẩn bị'
    READY = 'RE', 'Sẵn sàng giao'
    PICKED_UP = 'PU', 'Đã lấy hàng'
    ON_THE_WAY = 'OW', 'Đang giao hàng'
    DELIVERED = 'DE', 'Đã giao hàng'
    CANCELLED = 'CA', 'Đã hủy'

# Mô hình cho nhà hàng
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Restaurant Table"

class DeliveryReview(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE)
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Delivery #{self.delivery.id} by {self.customer.user.first_name}"

    class Meta:
        verbose_name_plural = "Delivery Review Table"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart (session: {self.session_key})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField()  # Lưu giá tại thời điểm đặt hàng
    
    def __str__(self):
        return f"{self.dish.name} x {self.quantity} in Order #{self.order.id}"
        
    class Meta:
        verbose_name_plural = "Order Item Table"