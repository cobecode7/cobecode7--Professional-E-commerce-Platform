"""Admin configuration for products app."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Category, Product, ProductImage, ProductVariant, 
    Inventory, ProductTag, ProductTagAssignment
)


class ProductImageInline(admin.TabularInline):
    """Inline for product images."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """Show image preview in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


class ProductVariantInline(admin.TabularInline):
    """Inline for product variants."""
    model = ProductVariant
    extra = 0
    fields = ('name', 'sku', 'size', 'color', 'price', 'stock_quantity', 'is_active')
    readonly_fields = ('created_at',)


class InventoryInline(admin.TabularInline):
    """Inline for inventory logs."""
    model = Inventory
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding inventory logs through inline."""
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    
    list_display = ('name', 'parent', 'product_count', 'is_active', 'sort_order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        (_('Media'), {
            'fields': ('image',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'sort_order')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Show number of products in category."""
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model."""
    
    list_display = (
        'name', 'sku', 'category', 'current_price_display', 
        'stock_status_display', 'is_active', 'is_featured'
    )
    list_filter = (
        'product_type', 'category', 'stock_status', 'is_active', 
        'is_featured', 'is_digital', 'created_at'
    )
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'discount_percentage')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        (_('Product Type & Category'), {
            'fields': ('product_type', 'category')
        }),
        (_('Pricing'), {
            'fields': ('price', 'sale_price', 'cost_price', 'discount_percentage')
        }),
        (_('Stock Management'), {
            'fields': ('stock_status', 'manage_stock', 'stock_quantity', 'low_stock_threshold')
        }),
        (_('Physical Properties'), {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'is_featured', 'is_digital')
        }),
        (_('Analytics'), {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline, InventoryInline]
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_active', 'mark_as_inactive']
    
    def current_price_display(self, obj):
        """Display current price with discount info."""
        if obj.sale_price:
            return format_html(
                '<span style="color: red;">${}</span> <del style="color: gray;">${}</del>',
                obj.sale_price, obj.price
            )
        return f"${obj.price}"
    current_price_display.short_description = "Price"
    
    def stock_status_display(self, obj):
        """Display stock status with color coding."""
        color_map = {
            'in_stock': 'green',
            'out_of_stock': 'red',
            'on_backorder': 'orange'
        }
        color = color_map.get(obj.stock_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_stock_status_display()
        )
    stock_status_display.short_description = "Stock Status"
    
    def mark_as_featured(self, request, queryset):
        """Mark selected products as featured."""
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark as featured"
    
    def mark_as_not_featured(self, request, queryset):
        """Mark selected products as not featured."""
        queryset.update(is_featured=False)
    mark_as_not_featured.short_description = "Remove from featured"
    
    def mark_as_active(self, request, queryset):
        """Mark selected products as active."""
        queryset.update(is_active=True)
    mark_as_active.short_description = "Mark as active"
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected products as inactive."""
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Mark as inactive"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for ProductImage model."""
    
    list_display = ('product', 'image_preview', 'alt_text', 'is_primary', 'sort_order')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    readonly_fields = ('image_preview', 'created_at')
    
    def image_preview(self, obj):
        """Show image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin for ProductVariant model."""
    
    list_display = ('product', 'name', 'sku', 'size', 'color', 'current_price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'size', 'color', 'product__category')
    search_fields = ('product__name', 'name', 'sku')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('product', 'name', 'sku')
        }),
        (_('Variant Attributes'), {
            'fields': ('size', 'color', 'material')
        }),
        (_('Pricing'), {
            'fields': ('price', 'sale_price')
        }),
        (_('Stock & Status'), {
            'fields': ('stock_quantity', 'is_active')
        }),
        (_('Media'), {
            'fields': ('image',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin for Inventory model."""
    
    list_display = ('product', 'variant', 'transaction_type', 'quantity_change', 'new_quantity', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('product__name', 'variant__name', 'reference', 'notes')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product', 'variant')
        }),
        (_('Transaction Details'), {
            'fields': ('transaction_type', 'quantity_change', 'previous_quantity', 'new_quantity')
        }),
        (_('Reference & Notes'), {
            'fields': ('reference', 'notes')
        }),
        (_('Timestamp'), {
            'fields': ('created_at',)
        }),
    )


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Admin for ProductTag model."""
    
    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        """Show number of products with this tag."""
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(ProductTagAssignment)
class ProductTagAssignmentAdmin(admin.ModelAdmin):
    """Admin for ProductTagAssignment model."""
    
    list_display = ('product', 'tag')
    list_filter = ('tag',)
    search_fields = ('product__name', 'tag__name')