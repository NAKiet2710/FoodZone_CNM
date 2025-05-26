from django.urls import path
from .views import add_to_cart, view_cart, remove_from_cart, update_quantity, checkout_cart, process_cart_payment, cart_payment_done, cart_payment_cancel, process_payment_method, cash_payment_confirm, process_paypal_payment

urlpatterns = [
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:dish_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/<str:action>/', update_quantity, name='update_quantity'),
    path('cart/checkout/', checkout_cart, name='checkout_cart'),
    path('cart/payment/', process_cart_payment, name='process_cart_payment'),
    path('cart/payment/method/', process_payment_method, name='process_payment_method'),
    path('cart/payment/cash/confirm/', cash_payment_confirm, name='cash_payment_confirm'),
    path('cart/payment/paypal/', process_paypal_payment, name='process_paypal_payment'),
    path('cart/payment/done/', cart_payment_done, name='cart_payment_done'),
    path('cart/payment/cancel/', cart_payment_cancel, name='cart_payment_cancel'),
] 