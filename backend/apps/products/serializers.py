"""Serializers for products app."""
from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, ProductVariant, 
    Inventory, ProductTag
)


class ProductTagSerializer(serializers.ModelSerializer):
    """Serializer for product tags."""
    
    class Meta:
        model = ProductTag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('slug',)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'sort_order')


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""
    
    current_price = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = (
            'id', 'name', 'sku', 'size', 'color', 'material',
            'price', 'sale_price', 'current_price', 'stock_quantity',
            'is_active', 'is_in_stock', 'image'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    full_path = serializers.ReadOnlyField()
    product_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image', 'parent',
            'full_path', 'product_count', 'children', 'meta_title',
            'meta_description', 'is_active', 'sort_order'
        )
        read_only_fields = ('slug',)
    
    def get_product_count(self, obj):
        """Get product count for category."""
        return obj.products.filter(is_active=True).count()
    
    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return CategorySerializer(children, many=True, context=self.context).data


class CategoryTreeSerializer(CategorySerializer):
    """Serializer for category tree (without children to avoid recursion)."""
    
    class Meta(CategorySerializer.Meta):
        fields = (
            'id', 'name', 'slug', 'description', 'image', 'parent',
            'full_path', 'product_count', 'is_active', 'sort_order'
        )


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view."""
    
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'short_description',
            'price', 'sale_price', 'current_price', 'discount_percentage',
            'is_in_stock', 'is_featured', 'category_name', 'primary_image',
            'tags', 'view_count', 'created_at'
        )
    
    def get_primary_image(self, obj):
        """Get primary product image."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image, context=self.context).data
        
        # Fallback to first image
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image, context=self.context).data
        
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view."""
    
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    category = CategoryTreeSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'description', 'short_description',
            'product_type', 'category', 'price', 'sale_price', 'current_price',
            'discount_percentage', 'stock_status', 'manage_stock', 'stock_quantity',
            'low_stock_threshold', 'is_in_stock', 'is_low_stock', 'weight',
            'length', 'width', 'height', 'meta_title', 'meta_description',
            'is_active', 'is_featured', 'is_digital', 'view_count',
            'images', 'variants', 'tags', 'created_at', 'updated_at'
        )


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products."""
    
    class Meta:
        model = Product
        fields = (
            'name', 'sku', 'description', 'short_description', 'product_type',
            'category', 'price', 'sale_price', 'cost_price', 'stock_status',
            'manage_stock', 'stock_quantity', 'low_stock_threshold', 'weight',
            'length', 'width', 'height', 'meta_title', 'meta_description',
            'is_active', 'is_featured', 'is_digital'
        )
    
    def validate_sku(self, value):
        """Validate SKU uniqueness."""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product with this SKU already exists.")
        return value


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for inventory logs."""
    
    class Meta:
        model = Inventory
        fields = (
            'id', 'product', 'variant', 'transaction_type', 'quantity_change',
            'previous_quantity', 'new_quantity', 'reference', 'notes', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters."""
    
    q = serializers.CharField(required=False, help_text="Search query")
    category = serializers.IntegerField(required=False, help_text="Category ID")
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    in_stock = serializers.BooleanField(required=False, help_text="Filter by stock availability")
    is_featured = serializers.BooleanField(required=False, help_text="Filter featured products")
    tags = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        help_text="Filter by tag names"
    )
    ordering = serializers.ChoiceField(
        choices=[
            'name', '-name', 'price', '-price', 'created_at', '-created_at',
            'view_count', '-view_count', 'stock_quantity', '-stock_quantity'
        ],
        required=False,
        default='-created_at'
    )
