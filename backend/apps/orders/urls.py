from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart endpoints
    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/items/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    
    # Order endpoints
    path('', views.OrderListCreateView.as_view(), name='order-list'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel-order'),
    
    # Shipping and discount endpoints
    path('shipping-methods/', views.ShippingMethodListView.as_view(), name='shipping-methods'),
    path('discounts/apply/', views.apply_discount, name='apply-discount'),
    
    # Checkout endpoints
    path('checkout/calculate/', views.checkout_calculation, name='checkout-calculation'),
]
