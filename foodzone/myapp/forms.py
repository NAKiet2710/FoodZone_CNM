from django import forms
from django.contrib.auth.models import User
from .models import Shipper, DeliveryAddress, Delivery, DeliveryStatus, Restaurant, DeliveryReview, Dish, Category

class ShipperRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    vehicle_type = forms.CharField(initial='Xe máy', required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Shipper
        fields = ['vehicle_number', 'license_number']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")
        
        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp")
        
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng")
        
        # Đảm bảo vehicle_type luôn là "Xe máy"
        cleaned_data['vehicle_type'] = 'Xe máy'
        
        return cleaned_data

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'is_default']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ dòng 1'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ dòng 2 (tùy chọn)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Thành phố'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tỉnh/Thành phố'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã bưu điện'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UpdateDeliveryStatusForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['status', 'delivery_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'delivery_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RestrictedDeliveryStatusForm(forms.ModelForm):
    # Chỉ cho phép các trạng thái: đã lấy hàng, đang giao hàng, đã giao hàng và đã hủy
    RESTRICTED_CHOICES = [
        ('PU', 'Đã lấy hàng'),
        ('OW', 'Đang giao hàng'),
        ('DE', 'Đã giao hàng'),
        ('CA', 'Đã hủy')
    ]
    
    status = forms.ChoiceField(choices=RESTRICTED_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Delivery
        fields = ['status', 'delivery_notes']
        widgets = {
            'delivery_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RestaurantDeliveryStatusForm(forms.ModelForm):
    # Chỉ cho phép các trạng thái mà nhà hàng có thể cập nhật: đã xác nhận, đang chuẩn bị, sẵn sàng lấy hàng
    RESTAURANT_CHOICES = [
        ('CO', 'Đã xác nhận'),
        ('PR', 'Đang chuẩn bị'),
        ('RP', 'Sẵn sàng lấy hàng')
    ]
    
    status = forms.ChoiceField(choices=RESTAURANT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Delivery
        fields = ['status', 'delivery_notes']
        widgets = {
            'delivery_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class DeliveryTrackingForm(forms.Form):
    # Sử dụng các trạng thái giới hạn giống như RestrictedDeliveryStatusForm
    RESTRICTED_CHOICES = [
        ('PU', 'Đã lấy hàng'),
        ('OW', 'Đang giao hàng'),
        ('DE', 'Đã giao hàng'),
        ('CA', 'Đã hủy')
    ]
    
    status = forms.ChoiceField(choices=RESTRICTED_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

class ShipperAvailabilityForm(forms.ModelForm):
    class Meta:
        model = Shipper
        fields = ['availability_status', 'current_location']
        widgets = {
            'availability_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control'})
        }

class RestaurantRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'phone', 'email', 'description', 'open_time', 'close_time']
        widgets = {
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")
        
        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp")
        
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng")
        
        return cleaned_data

class DeliveryReviewForm(forms.ModelForm):
    class Meta:
        model = DeliveryReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'image', 'ingredients', 'details', 'category', 'price', 'discounted_price', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 