"""Orders and shopping cart models for the ecommerce platform."""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.products.models import Product, ProductVariant

User = get_user_model()


class Cart(models.Model):
    """Shopping cart for users."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(max_length=40, blank=True, null=True)  # For anonymous users
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
        app_label = "orders"
        
    def __str__(self) -> str:
        """Return string representation of cart."""
        return f"Cart for {self.user.email if self.user else 'Anonymous'}"
    
    @property
    def total_items(self) -> int:
        """Return total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate cart subtotal (before tax and shipping)."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_weight(self) -> Decimal:
        """Calculate total weight for shipping calculations."""
        total = Decimal('0.00')
        for item in self.items.all():
            weight = item.variant.product.weight if item.variant else item.product.weight
            if weight:
                total += weight * item.quantity
        return total
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.all().delete()
        self.updated_at = timezone.now()
        self.save()


class CartItem(models.Model):
    """Individual items in a shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of adding
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = [['cart', 'product', 'variant']]  # Prevent duplicate items
        
    def __str__(self) -> str:
        """Return string representation of cart item."""
        item_name = f"{self.product.name}"
        if self.variant:
            item_name += f" - {self.variant.name}"
        return f"{item_name} (x{self.quantity})"
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this cart item."""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs) -> None:
        """Override save to set unit price."""
        if not self.unit_price:
            self.unit_price = self.variant.current_price if self.variant else self.product.current_price
        super().save(*args, **kwargs)


class Order(models.Model):
    """Customer orders."""
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Payment Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    SHIPPING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing for Shipment'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]
    
    # Order Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # Customer Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Billing Information
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address_line_1 = models.CharField(max_length=255)
    billing_address_line_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    
    # Shipping Information
    shipping_first_name = models.CharField(max_length=50)
    shipping_last_name = models.CharField(max_length=50)
    shipping_address_line_1 = models.CharField(max_length=255)
    shipping_address_line_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and Tracking
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_status = models.CharField(max_length=15, choices=SHIPPING_STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Shipping Method
    shipping_method = models.CharField(max_length=100, blank=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    
    # Order Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self) -> str:
        """Return string representation of order."""
        return f"Order {self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs) -> None:
        """Override save to generate order number."""
        if not self.order_number:
            from django.utils import timezone
            import random
            now = timezone.now()
            random_suffix = random.randint(1000, 9999)
            self.order_number = f"ORD-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}-{random_suffix}"
        super().save(*args, **kwargs)
    
    @property
    def billing_address(self) -> str:
        """Return formatted billing address."""
        lines = [
            f"{self.billing_first_name} {self.billing_last_name}",
            self.billing_address_line_1,
            self.billing_address_line_2 if self.billing_address_line_2 else None,
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ]
        return '\n'.join(line for line in lines if line)
    
    @property
    def shipping_address(self) -> str:
        """Return formatted shipping address."""
        lines = [
            f"{self.shipping_first_name} {self.shipping_last_name}",
            self.shipping_address_line_1,
            self.shipping_address_line_2 if self.shipping_address_line_2 else None,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ]
        return '\n'.join(line for line in lines if line)
    
    @property
    def total_items(self) -> int:
        """Return total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in ['pending', 'paid'] and self.shipping_status == 'pending'
    
    @property
    def is_paid(self) -> bool:
        """Check if order has been paid."""
        return self.status not in ['pending', 'cancelled']


class OrderItem(models.Model):
    """Individual items in an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    # Product details at time of order (for historical record)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        
    def __str__(self) -> str:
        """Return string representation of order item."""
        item_name = self.product_name
        if self.variant_name:
            item_name += f" - {self.variant_name}"
        return f"{item_name} (x{self.quantity})"
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this order item."""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs) -> None:
        """Override save to store product details."""
        if not self.product_name:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            if self.variant:
                self.variant_name = self.variant.name
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment tracking for orders."""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # External Payment Gateway Information
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # Card Information (last 4 digits for security)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # Visa, MasterCard, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Refund Information
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        """Return string representation of payment."""
        return f"Payment {self.id} - {self.order.order_number} - ${self.amount}"
    
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == 'completed'
    
    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == 'completed' and self.refund_amount < self.amount


class ShippingMethod(models.Model):
    """Available shipping methods."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Delivery timeframes
    min_delivery_days = models.PositiveIntegerField(default=1)
    max_delivery_days = models.PositiveIntegerField(default=7)
    
    # Availability
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shipping Method"
        verbose_name_plural = "Shipping Methods"
        ordering = ['base_cost']
        
    def __str__(self) -> str:
        """Return string representation of shipping method."""
        return f"{self.name} - ${self.base_cost}"
    
    def calculate_cost(self, weight: Decimal = None, order_total: Decimal = None) -> Decimal:
        """Calculate shipping cost based on weight and order total."""
        cost = self.base_cost
        
        if weight and self.cost_per_kg > 0:
            cost += weight * self.cost_per_kg
            
        return cost
    
    def is_available_for_order(self, weight: Decimal = None, order_total: Decimal = None) -> bool:
        """Check if shipping method is available for given order."""
        if not self.is_active:
            return False
            
        if order_total and order_total < self.min_order_amount:
            return False
            
        if weight and self.max_weight and weight > self.max_weight:
            return False
            
        return True


class Discount(models.Model):
    """Discount codes and promotions."""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)  # Percentage or fixed amount
    
    # Usage Limits
    usage_limit = models.PositiveIntegerField(blank=True, null=True)  # Total uses allowed
    usage_limit_per_customer = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    
    # Conditions
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        
    def __str__(self) -> str:
        """Return string representation of discount."""
        return f"{self.code} - {self.name}"
    
    def is_valid(self, user=None, order_total: Decimal = None) -> bool:
        """Check if discount is valid."""
        from django.utils import timezone
        
        if not self.is_active:
            return False
            
        now = timezone.now()
        if self.valid_from > now:
            return False
            
        if self.valid_until and self.valid_until < now:
            return False
            
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
            
        if order_total and order_total < self.minimum_order_amount:
            return False
            
        return True
    
    def calculate_discount(self, order_total: Decimal) -> Decimal:
        """Calculate discount amount for given order total."""
        if self.discount_type == 'percentage':
            discount = order_total * (self.value / 100)
        elif self.discount_type == 'fixed_amount':
            discount = self.value
        else:  # free_shipping
            discount = Decimal('0.00')  # Handled separately
            
        if self.maximum_discount_amount:
            discount = min(discount, self.maximum_discount_amount)
            
        return discount
