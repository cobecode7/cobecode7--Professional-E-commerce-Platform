"""Product models for the ecommerce platform."""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal


class Category(models.Model):
    """Product categories with hierarchical structure."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status and ordering
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']
        app_label = "products"
        
    def __str__(self) -> str:
        """Return string representation of category."""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        """Override save to auto-generate slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def full_path(self) -> str:
        """Return full category path."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)


class Product(models.Model):
    """Main product model."""
    
    PRODUCT_TYPES = [
        ('simple', 'Simple Product'),
        ('variable', 'Variable Product'),
        ('digital', 'Digital Product'),
    ]
    
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('on_backorder', 'On Backorder'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    short_description = models.TextField(max_length=500, blank=True)
    
    # Product Type and Category
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='simple')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Stock Management
    stock_status = models.CharField(max_length=15, choices=STOCK_STATUS, default='in_stock')
    manage_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Physical Properties
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status and Features
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
        
    def __str__(self) -> str:
        """Return string representation of product."""
        return f"{self.name} (SKU: {self.sku})"
    
    def save(self, *args, **kwargs) -> None:
        """Override save to auto-generate slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def current_price(self) -> Decimal:
        """Return current selling price (sale price if available, otherwise regular price)."""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def discount_percentage(self) -> int:
        """Calculate discount percentage if sale price is set."""
        if self.sale_price and self.sale_price < self.price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        if not self.manage_stock:
            return self.stock_status == 'in_stock'
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low in stock."""
        if not self.manage_stock:
            return False
        return 0 < self.stock_quantity <= self.low_stock_threshold


class ProductImage(models.Model):
    """Product images with ordering."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_primary=True),
                name='unique_primary_image_per_product'
            )
        ]
        
    def __str__(self) -> str:
        """Return string representation of product image."""
        primary_text = " (Primary)" if self.is_primary else ""
        return f"{self.product.name} - Image {self.sort_order}{primary_text}"


class ProductVariant(models.Model):
    """Product variants for size, color, etc."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Large Red"
    sku = models.CharField(max_length=50, unique=True)
    
    # Variant Attributes
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=30, blank=True)
    material = models.CharField(max_length=50, blank=True)
    
    # Pricing (can override product pricing)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Stock for this variant
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Images specific to this variant
    image = models.ImageField(upload_to='variants/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        unique_together = [['product', 'size', 'color', 'material']]
        
    def __str__(self) -> str:
        """Return string representation of variant."""
        return f"{self.product.name} - {self.name}"
    
    @property
    def current_price(self) -> Decimal:
        """Return current price for this variant."""
        if self.sale_price:
            return self.sale_price
        if self.price:
            return self.price
        return self.product.current_price
    
    @property
    def is_in_stock(self) -> bool:
        """Check if variant is in stock."""
        return self.stock_quantity > 0 and self.is_active


class Inventory(models.Model):
    """Inventory tracking and history."""
    
    TRANSACTION_TYPES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Inventory Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage/Loss'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name='inventory_logs',
        blank=True,
        null=True
    )
    
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    quantity_change = models.IntegerField()  # Can be negative
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    
    reference = models.CharField(max_length=100, blank=True)  # Order ID, etc.
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inventory Log"
        verbose_name_plural = "Inventory Logs"
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        """Return string representation of inventory log."""
        item = self.variant.name if self.variant else self.product.name
        return f"{item}: {self.transaction_type} ({self.quantity_change:+d})"


class ProductTag(models.Model):
    """Tags for products (for search and filtering)."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        verbose_name = "Product Tag"
        verbose_name_plural = "Product Tags"
        ordering = ['name']
        
    def __str__(self) -> str:
        """Return string representation of tag."""
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        """Override save to auto-generate slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Many-to-Many relationship for Product-Tag
class ProductTagAssignment(models.Model):
    """Assignment of tags to products."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(ProductTag, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = [['product', 'tag']]
        verbose_name = "Product Tag Assignment"
        verbose_name_plural = "Product Tag Assignments"

# Add tags to Product model via related field
Product.add_to_class(
    'tags', 
    models.ManyToManyField(
        ProductTag, 
        through=ProductTagAssignment, 
        related_name='products',
        blank=True
    )
)
