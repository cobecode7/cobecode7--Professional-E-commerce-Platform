"""API views for orders app."""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema

from .models import Cart, CartItem, Order, ShippingMethod, Discount
from apps.products.models import Product, ProductVariant
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    OrderSerializer, OrderCreateSerializer, ShippingMethodSerializer,
    DiscountSerializer, ApplyDiscountSerializer
)


class CartView(generics.RetrieveAPIView):
    """Get user's shopping cart."""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user's cart."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


@extend_schema(
    request=AddToCartSerializer,
    responses={200: CartItemSerializer, 400: 'Bad Request'},
    description="Add item to shopping cart"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """Add item to shopping cart."""
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Check if item already exists in cart
    existing_item = CartItem.objects.filter(
        cart=cart,
        product=data['product'],
        variant=data.get('variant')
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += data['quantity']
        existing_item.save()
        cart_item = existing_item
    else:
        # Create new cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=data['product'],
            variant=data.get('variant'),
            quantity=data['quantity']
        )
    
    serializer = CartItemSerializer(cart_item, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    responses={204: 'Item removed'},
    description="Remove item from cart"
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from shopping cart."""
    try:
        cart = request.user.cart
        cart_item = cart.items.get(id=item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    request={'quantity': 'integer'},
    responses={200: CartItemSerializer, 400: 'Bad Request'},
    description="Update cart item quantity"
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    try:
        cart = request.user.cart
        cart_item = cart.items.get(id=item_id)
        
        quantity = request.data.get('quantity')
        if not quantity or quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response(serializer.data)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={200: 'Cart cleared'},
    description="Clear all items from cart"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart."""
    try:
        cart = request.user.cart
        cart.clear()
        return Response({'message': 'Cart cleared successfully'})
    except Cart.DoesNotExist:
        return Response({'message': 'Cart is already empty'})


class OrderListCreateView(generics.ListCreateAPIView):
    """List user orders and create new orders."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Get orders for current user."""
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items', 'payments').order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders for current user."""
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items', 'payments')


@extend_schema(
    responses={200: 'Order cancelled', 400: 'Cannot cancel order'},
    description="Cancel an order"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_number):
    """Cancel an order."""
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        user=request.user
    )
    
    if not order.can_be_cancelled:
        return Response(
            {'error': 'Order cannot be cancelled'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.status = 'cancelled'
    order.save()
    
    return Response({'message': 'Order cancelled successfully'})


class ShippingMethodListView(generics.ListAPIView):
    """List available shipping methods."""
    
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active shipping methods."""
        return ShippingMethod.objects.filter(is_active=True).order_by('base_cost')


@extend_schema(
    request=ApplyDiscountSerializer,
    responses={200: 'Discount applied', 400: 'Invalid discount'},
    description="Apply discount code"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def apply_discount(request):
    """Apply discount code and get discount amount."""
    serializer = ApplyDiscountSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    code = serializer.validated_data['code']
    order_total = serializer.validated_data['order_total']
    
    try:
        discount = Discount.objects.get(code=code)
        if not discount.is_valid(order_total=order_total):
            return Response(
                {'error': 'Discount code is not valid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discount_amount = discount.calculate_discount(order_total)
        
        return Response({
            'discount': DiscountSerializer(discount).data,
            'discount_amount': discount_amount,
            'new_total': order_total - discount_amount
        })
        
    except Discount.DoesNotExist:
        return Response(
            {'error': 'Invalid discount code'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    responses={200: 'Checkout calculation'},
    description="Calculate checkout totals"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def checkout_calculation(request):
    """Calculate checkout totals including shipping and tax."""
    try:
        cart = request.user.cart
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        subtotal = cart.subtotal
        shipping_cost = request.query_params.get('shipping_cost', '9.99')
        shipping_cost = float(shipping_cost)
        
        # Calculate tax (8% - in real app, this would be based on location)
        tax_rate = 0.08
        tax_amount = subtotal * tax_rate
        
        # Apply discount if provided
        discount_amount = 0
        discount_code = request.query_params.get('discount_code')
        if discount_code:
            try:
                discount = Discount.objects.get(code=discount_code)
                if discount.is_valid(order_total=subtotal):
                    discount_amount = discount.calculate_discount(subtotal)
            except Discount.DoesNotExist:
                pass
        
        total = subtotal + shipping_cost + tax_amount - discount_amount
        
        return Response({
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'total': total,
            'cart_items': cart.total_items
        })
        
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
