"""Admin configuration for orders app."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Cart, CartItem, Order, OrderItem, Payment, 
    ShippingMethod, Discount
)


class CartItemInline(admin.TabularInline):
    """Inline for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price', 'created_at')
    fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')
    
    def total_price(self, obj):
        """Show total price for item."""
        if obj.id:
            return f"${obj.total_price}"
        return "-"
    total_price.short_description = "Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model."""
    
    list_display = ('user', 'total_items_display', 'subtotal_display', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_items', 'subtotal', 'total_weight', 'created_at', 'updated_at')
    
    inlines = [CartItemInline]
    
    fieldsets = (
        (_('Cart Information'), {
            'fields': ('user', 'session_key')
        }),
        (_('Cart Summary'), {
            'fields': ('total_items', 'subtotal', 'total_weight'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_items_display(self, obj):
        """Display total items in cart."""
        return obj.total_items
    total_items_display.short_description = "Items"
    
    def subtotal_display(self, obj):
        """Display cart subtotal."""
        return f"${obj.subtotal}"
    subtotal_display.short_description = "Subtotal"


class OrderItemInline(admin.TabularInline):
    """Inline for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_sku', 'variant_name', 'total_price', 'created_at')
    fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')
    
    def total_price(self, obj):
        """Show total price for item."""
        if obj.id:
            return f"${obj.total_price}"
        return "-"
    total_price.short_description = "Total"


class PaymentInline(admin.TabularInline):
    """Inline for payments."""
    model = Payment
    extra = 0
    readonly_fields = ('id', 'status', 'amount', 'created_at', 'processed_at')
    fields = ('payment_method', 'amount', 'status', 'gateway_transaction_id')
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding payments through inline."""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""
    
    list_display = (
        'order_number', 'user', 'status_display', 'shipping_status_display',
        'total_amount_display', 'total_items_display', 'created_at'
    )
    list_filter = (
        'status', 'shipping_status', 'created_at', 'shipped_at', 'delivered_at'
    )
    search_fields = (
        'order_number', 'user__email', 'billing_email', 
        'billing_first_name', 'billing_last_name'
    )
    readonly_fields = (
        'id', 'order_number', 'total_items', 'billing_address_display',
        'shipping_address_display', 'created_at', 'updated_at'
    )
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'user', 'status', 'shipping_status')
        }),
        (_('Billing Address'), {
            'fields': (
                'billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone',
                'billing_address_line_1', 'billing_address_line_2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        (_('Shipping Address'), {
            'fields': (
                'shipping_first_name', 'shipping_last_name',
                'shipping_address_line_1', 'shipping_address_line_2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            ),
            'classes': ('collapse',)
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        (_('Shipping & Tracking'), {
            'fields': ('shipping_method', 'tracking_number', 'estimated_delivery_date')
        }),
        (_('Notes'), {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, PaymentInline]
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def status_display(self, obj):
        """Display order status with color coding."""
        color_map = {
            'pending': '#f39c12',
            'paid': '#2ecc71', 
            'processing': '#3498db',
            'shipped': '#9b59b6',
            'delivered': '#27ae60',
            'cancelled': '#e74c3c',
            'refunded': '#95a5a6'
        }
        color = color_map.get(obj.status, '#34495e')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = "Status"
    
    def shipping_status_display(self, obj):
        """Display shipping status with color coding."""
        color_map = {
            'pending': '#f39c12',
            'preparing': '#3498db',
            'shipped': '#9b59b6',
            'in_transit': '#8e44ad',
            'delivered': '#27ae60',
            'returned': '#e74c3c'
        }
        color = color_map.get(obj.shipping_status, '#34495e')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_shipping_status_display()
        )
    shipping_status_display.short_description = "Shipping"
    
    def total_amount_display(self, obj):
        """Display total amount."""
        return f"${obj.total_amount}"
    total_amount_display.short_description = "Total"
    
    def total_items_display(self, obj):
        """Display total items."""
        return obj.total_items
    total_items_display.short_description = "Items"
    
    def billing_address_display(self, obj):
        """Display formatted billing address."""
        return format_html('<pre>{}</pre>', obj.billing_address)
    billing_address_display.short_description = "Billing Address"
    
    def shipping_address_display(self, obj):
        """Display formatted shipping address."""
        return format_html('<pre>{}</pre>', obj.shipping_address)
    shipping_address_display.short_description = "Shipping Address"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing."""
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark as processing"
    
    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped."""
        from django.utils import timezone
        queryset.update(status='shipped', shipping_status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = "Mark as shipped"
    
    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered."""
        from django.utils import timezone
        queryset.update(
            status='delivered', 
            shipping_status='delivered', 
            delivered_at=timezone.now()
        )
    mark_as_delivered.short_description = "Mark as delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model."""
    
    list_display = ('order', 'product_name', 'variant_name', 'quantity', 'unit_price', 'total_price_display')
    list_filter = ('created_at', 'product')
    search_fields = ('order__order_number', 'product_name', 'product_sku')
    readonly_fields = ('total_price', 'created_at')
    
    def total_price_display(self, obj):
        """Display total price."""
        return f"${obj.total_price}"
    total_price_display.short_description = "Total"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    
    list_display = (
        'order', 'payment_method', 'amount_display', 'status_display', 
        'created_at', 'processed_at'
    )
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('order__order_number', 'gateway_transaction_id')
    readonly_fields = (
        'id', 'created_at', 'processed_at', 'is_successful', 'can_be_refunded'
    )
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('order', 'payment_method', 'amount', 'currency', 'status')
        }),
        (_('Gateway Information'), {
            'fields': ('gateway_transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        (_('Card Information'), {
            'fields': ('card_last_four', 'card_brand'),
            'classes': ('collapse',)
        }),
        (_('Refund Information'), {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        """Display payment amount."""
        return f"${obj.amount}"
    amount_display.short_description = "Amount"
    
    def status_display(self, obj):
        """Display payment status with color coding."""
        color_map = {
            'pending': '#f39c12',
            'processing': '#3498db',
            'completed': '#27ae60',
            'failed': '#e74c3c',
            'cancelled': '#95a5a6',
            'refunded': '#e67e22',
            'partially_refunded': '#d35400'
        }
        color = color_map.get(obj.status, '#34495e')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = "Status"


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Admin for ShippingMethod model."""
    
    list_display = (
        'name', 'base_cost_display', 'delivery_time_display', 
        'is_active', 'min_order_amount'
    )
    list_filter = ('is_active', 'min_delivery_days', 'max_delivery_days')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Pricing'), {
            'fields': ('base_cost', 'cost_per_kg', 'min_order_amount')
        }),
        (_('Delivery'), {
            'fields': ('min_delivery_days', 'max_delivery_days', 'max_weight')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def base_cost_display(self, obj):
        """Display base cost."""
        return f"${obj.base_cost}"
    base_cost_display.short_description = "Base Cost"
    
    def delivery_time_display(self, obj):
        """Display delivery timeframe."""
        if obj.min_delivery_days == obj.max_delivery_days:
            return f"{obj.min_delivery_days} day{'s' if obj.min_delivery_days > 1 else ''}"
        return f"{obj.min_delivery_days}-{obj.max_delivery_days} days"
    delivery_time_display.short_description = "Delivery Time"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Admin for Discount model."""
    
    list_display = (
        'code', 'name', 'discount_type', 'value_display', 
        'used_count', 'is_active', 'valid_until'
    )
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'description', 'is_active')
        }),
        (_('Discount Configuration'), {
            'fields': ('discount_type', 'value', 'maximum_discount_amount')
        }),
        (_('Usage Limits'), {
            'fields': ('usage_limit', 'usage_limit_per_customer', 'used_count')
        }),
        (_('Conditions'), {
            'fields': ('minimum_order_amount',)
        }),
        (_('Validity Period'), {
            'fields': ('valid_from', 'valid_until')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_display(self, obj):
        """Display discount value."""
        if obj.discount_type == 'percentage':
            return f"{obj.value}%"
        elif obj.discount_type == 'fixed_amount':
            return f"${obj.value}"
        else:
            return "Free Shipping"
    value_display.short_description = "Value"