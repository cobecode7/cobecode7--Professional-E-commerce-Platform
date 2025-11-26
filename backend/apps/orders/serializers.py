"""Serializers for orders app."""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction

from .models import (
    Cart, CartItem, Order, OrderItem, Payment,
    ShippingMethod, Discount
)
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'variant', 'quantity', 'unit_price',
            'total_price', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'unit_price', 'created_at', 'updated_at')


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    total_weight = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'items', 'total_items', 'subtotal', 'total_weight',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate(self, attrs):
        """Validate product and variant existence."""
        from apps.products.models import Product, ProductVariant
        
        try:
            product = Product.objects.get(id=attrs['product_id'], is_active=True)
            attrs['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        
        if attrs.get('variant_id'):
            try:
                variant = ProductVariant.objects.get(
                    id=attrs['variant_id'], 
                    product=product, 
                    is_active=True
                )
                attrs['variant'] = variant
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found or inactive.")
        else:
            attrs['variant'] = None
        
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product_name', 'product_sku', 'variant_name',
            'quantity', 'unit_price', 'total_price'
        )


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    
    is_successful = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = (
            'id', 'payment_method', 'amount', 'currency', 'status',
            'gateway_transaction_id', 'card_last_four', 'card_brand',
            'is_successful', 'can_be_refunded', 'refund_amount',
            'created_at', 'processed_at'
        )
        read_only_fields = (
            'id', 'gateway_transaction_id', 'created_at', 'processed_at'
        )


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    billing_address = serializers.ReadOnlyField()
    shipping_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'shipping_status', 'items', 'payments',
            'billing_first_name', 'billing_last_name', 'billing_email',
            'billing_address', 'shipping_address', 'subtotal', 'shipping_cost',
            'tax_amount', 'discount_amount', 'total_amount', 'total_items',
            'can_be_cancelled', 'is_paid', 'tracking_number', 'shipping_method',
            'estimated_delivery_date', 'customer_notes', 'created_at',
            'updated_at', 'shipped_at', 'delivered_at'
        )
        read_only_fields = (
            'id', 'order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    class Meta:
        model = Order
        fields = (
            'billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone',
            'billing_address_line_1', 'billing_address_line_2', 'billing_city',
            'billing_state', 'billing_postal_code', 'billing_country',
            'shipping_first_name', 'shipping_last_name', 'shipping_address_line_1',
            'shipping_address_line_2', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'customer_notes',
            'shipping_method'
        )
    
    @transaction.atomic
    def create(self, validated_data):
        """Create order from cart."""
        user = self.context['request'].user
        
        # Get user's cart
        try:
            cart = user.cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty.")
        
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        
        # Calculate totals
        subtotal = cart.subtotal
        shipping_cost = Decimal('9.99')  # TODO: Calculate based on shipping method
        tax_amount = subtotal * Decimal('0.08')  # TODO: Calculate based on location
        total_amount = subtotal + shipping_cost + tax_amount
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total_amount,
            **validated_data
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                variant_name=cart_item.variant.name if cart_item.variant else ''
            )
        
        # Clear cart
        cart.clear()
        
        return order


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods."""
    
    class Meta:
        model = ShippingMethod
        fields = (
            'id', 'name', 'description', 'base_cost', 'cost_per_kg',
            'min_delivery_days', 'max_delivery_days', 'min_order_amount',
            'max_weight', 'is_active'
        )


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for discounts."""
    
    class Meta:
        model = Discount
        fields = (
            'id', 'code', 'name', 'description', 'discount_type', 'value',
            'minimum_order_amount', 'maximum_discount_amount', 'valid_from',
            'valid_until', 'is_active'
        )
        read_only_fields = ('id', 'used_count')


class ApplyDiscountSerializer(serializers.Serializer):
    """Serializer for applying discount codes."""
    
    code = serializers.CharField(max_length=50)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_code(self, value):
        """Validate discount code."""
        try:
            discount = Discount.objects.get(code=value)
            if not discount.is_valid(order_total=self.initial_data.get('order_total')):
                raise serializers.ValidationError("Discount code is not valid.")
            return value
        except Discount.DoesNotExist:
            raise serializers.ValidationError("Invalid discount code.")
