"""Tests for products models."""
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from .models import (
    Category, Product, ProductImage, ProductVariant,
    Inventory, ProductTag, ProductTagAssignment
)


class CategoryModelTest(TestCase):
    """Test cases for Category model."""

    def test_create_category(self) -> None:
        """Test creating a category."""
        category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and gadgets"
        )
        
        self.assertEqual(category.name, "Electronics")
        self.assertEqual(category.slug, "electronics")
        self.assertTrue(category.is_active)
        self.assertEqual(category.sort_order, 0)

    def test_category_hierarchy(self) -> None:
        """Test category hierarchical structure."""
        parent = Category.objects.create(name="Electronics")
        child = Category.objects.create(name="Smartphones", parent=parent)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
        self.assertEqual(str(child), "Electronics > Smartphones")

    def test_category_full_path(self) -> None:
        """Test category full path property."""
        electronics = Category.objects.create(name="Electronics")
        phones = Category.objects.create(name="Phones", parent=electronics)
        smartphones = Category.objects.create(name="Smartphones", parent=phones)
        
        self.assertEqual(smartphones.full_path, "Electronics > Phones > Smartphones")

    def test_slug_auto_generation(self) -> None:
        """Test automatic slug generation."""
        category = Category.objects.create(name="Home & Garden")
        self.assertEqual(category.slug, "home-garden")

    def test_unique_name_constraint(self) -> None:
        """Test that category names must be unique."""
        Category.objects.create(name="Electronics")
        
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Electronics")


class ProductModelTest(TestCase):
    """Test cases for Product model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.category = Category.objects.create(name="Electronics")
        self.product_data = {
            'name': 'Wireless Headphones',
            'sku': 'WH001',
            'description': 'High-quality wireless headphones',
            'category': self.category,
            'price': Decimal('199.99'),
            'stock_quantity': 25
        }

    def test_create_product(self) -> None:
        """Test creating a product."""
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.name, 'Wireless Headphones')
        self.assertEqual(product.sku, 'WH001')
        self.assertEqual(product.slug, 'wireless-headphones')
        self.assertEqual(product.price, Decimal('199.99'))
        self.assertEqual(product.category, self.category)
        self.assertTrue(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(product.stock_status, 'in_stock')

    def test_current_price_property(self) -> None:
        """Test current_price property with and without sale price."""
        product = Product.objects.create(**self.product_data)
        
        # Without sale price
        self.assertEqual(product.current_price, Decimal('199.99'))
        
        # With sale price
        product.sale_price = Decimal('149.99')
        product.save()
        self.assertEqual(product.current_price, Decimal('149.99'))

    def test_discount_percentage(self) -> None:
        """Test discount percentage calculation."""
        product = Product.objects.create(**self.product_data)
        
        # No discount
        self.assertEqual(product.discount_percentage, 0)
        
        # With discount
        product.sale_price = Decimal('149.99')
        product.save()
        self.assertEqual(product.discount_percentage, 25)  # 25% discount

    def test_stock_management(self) -> None:
        """Test stock management properties."""
        product = Product.objects.create(**self.product_data)
        
        # In stock
        self.assertTrue(product.is_in_stock)
        self.assertFalse(product.is_low_stock)
        
        # Low stock
        product.stock_quantity = 3
        product.low_stock_threshold = 5
        product.save()
        self.assertTrue(product.is_low_stock)
        
        # Out of stock
        product.stock_quantity = 0
        product.save()
        self.assertFalse(product.is_in_stock)

    def test_unique_sku_constraint(self) -> None:
        """Test that SKU must be unique."""
        Product.objects.create(**self.product_data)
        
        duplicate_data = self.product_data.copy()
        duplicate_data['name'] = 'Different Product'
        
        with self.assertRaises(IntegrityError):
            Product.objects.create(**duplicate_data)

    def test_product_string_representation(self) -> None:
        """Test product __str__ method."""
        product = Product.objects.create(**self.product_data)
        expected = "Wireless Headphones (SKU: WH001)"
        self.assertEqual(str(product), expected)


class ProductImageModelTest(TestCase):
    """Test cases for ProductImage model."""

    def setUp(self) -> None:
        """Set up test data."""
        category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name='Test Product',
            sku='TP001',
            description='Test product',
            category=category,
            price=Decimal('99.99')
        )

    def test_create_product_image(self) -> None:
        """Test creating a product image."""
        image = ProductImage.objects.create(
            product=self.product,
            alt_text="Test product image",
            is_primary=True,
            sort_order=1
        )
        
        self.assertEqual(image.product, self.product)
        self.assertEqual(image.alt_text, "Test product image")
        self.assertTrue(image.is_primary)
        self.assertEqual(image.sort_order, 1)

    def test_primary_image_constraint(self) -> None:
        """Test that only one primary image per product is allowed."""
        ProductImage.objects.create(
            product=self.product,
            is_primary=True
        )
        
        with self.assertRaises(IntegrityError):
            ProductImage.objects.create(
                product=self.product,
                is_primary=True
            )

    def test_image_ordering(self) -> None:
        """Test image ordering by sort_order."""
        image1 = ProductImage.objects.create(
            product=self.product, 
            sort_order=2,
            is_primary=False
        )
        image2 = ProductImage.objects.create(
            product=self.product, 
            sort_order=1,
            is_primary=False
        )
        
        images = list(self.product.images.all())
        self.assertEqual(images[0], image2)  # Lower sort_order comes first
        self.assertEqual(images[1], image1)


class ProductVariantModelTest(TestCase):
    """Test cases for ProductVariant model."""

    def setUp(self) -> None:
        """Set up test data."""
        category = Category.objects.create(name="Clothing")
        self.product = Product.objects.create(
            name='T-Shirt',
            sku='TS001',
            description='Basic t-shirt',
            category=category,
            price=Decimal('29.99'),
            product_type='variable'
        )

    def test_create_variant(self) -> None:
        """Test creating a product variant."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name="Large Blue",
            sku="TS001-LB",
            size="L",
            color="Blue",
            stock_quantity=10
        )
        
        self.assertEqual(variant.product, self.product)
        self.assertEqual(variant.name, "Large Blue")
        self.assertEqual(variant.size, "L")
        self.assertEqual(variant.color, "Blue")
        self.assertTrue(variant.is_active)

    def test_variant_pricing(self) -> None:
        """Test variant pricing logic."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name="Medium Red",
            sku="TS001-MR",
            size="M",
            color="Red",
            price=Decimal('35.00'),
            sale_price=Decimal('25.00')
        )
        
        # Variant has its own pricing
        self.assertEqual(variant.current_price, Decimal('25.00'))
        
        # Variant without pricing uses product price
        variant_no_price = ProductVariant.objects.create(
            product=self.product,
            name="Small Green",
            sku="TS001-SG",
            size="S",
            color="Green"
        )
        self.assertEqual(variant_no_price.current_price, self.product.price)

    def test_variant_unique_constraint(self) -> None:
        """Test unique constraint for size/color/material combination."""
        ProductVariant.objects.create(
            product=self.product,
            name="Large Blue",
            sku="TS001-LB1",
            size="L",
            color="Blue"
        )
        
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product=self.product,
                name="Large Blue Duplicate",
                sku="TS001-LB2",
                size="L",
                color="Blue"  # Same combination
            )

    def test_variant_stock_status(self) -> None:
        """Test variant stock status."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name="Test Variant",
            sku="TV001",
            stock_quantity=5
        )
        
        self.assertTrue(variant.is_in_stock)
        
        variant.stock_quantity = 0
        variant.save()
        self.assertFalse(variant.is_in_stock)
        
        variant.stock_quantity = 10
        variant.is_active = False
        variant.save()
        self.assertFalse(variant.is_in_stock)


class InventoryModelTest(TestCase):
    """Test cases for Inventory model."""

    def setUp(self) -> None:
        """Set up test data."""
        category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name='Test Product',
            sku='TP001',
            description='Test product',
            category=category,
            price=Decimal('99.99'),
            stock_quantity=10
        )

    def test_create_inventory_log(self) -> None:
        """Test creating an inventory log."""
        log = Inventory.objects.create(
            product=self.product,
            transaction_type='restock',
            quantity_change=50,
            previous_quantity=10,
            new_quantity=60,
            reference='PO-001',
            notes='Initial restock'
        )
        
        self.assertEqual(log.product, self.product)
        self.assertEqual(log.transaction_type, 'restock')
        self.assertEqual(log.quantity_change, 50)
        self.assertEqual(log.previous_quantity, 10)
        self.assertEqual(log.new_quantity, 60)

    def test_inventory_log_string_representation(self) -> None:
        """Test inventory log __str__ method."""
        log = Inventory.objects.create(
            product=self.product,
            transaction_type='sale',
            quantity_change=-2,
            previous_quantity=10,
            new_quantity=8
        )
        
        expected = "Test Product: sale (-2)"
        self.assertEqual(str(log), expected)


class ProductTagModelTest(TestCase):
    """Test cases for ProductTag model."""

    def test_create_tag(self) -> None:
        """Test creating a product tag."""
        tag = ProductTag.objects.create(name="Wireless")
        
        self.assertEqual(tag.name, "Wireless")
        self.assertEqual(tag.slug, "wireless")

    def test_tag_slug_generation(self) -> None:
        """Test automatic slug generation for tags."""
        tag = ProductTag.objects.create(name="Noise Cancelling")
        self.assertEqual(tag.slug, "noise-cancelling")

    def test_unique_tag_name(self) -> None:
        """Test that tag names must be unique."""
        ProductTag.objects.create(name="Wireless")
        
        with self.assertRaises(IntegrityError):
            ProductTag.objects.create(name="Wireless")

    def test_product_tag_assignment(self) -> None:
        """Test assigning tags to products."""
        category = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            name='Headphones',
            sku='HP001',
            description='Test headphones',
            category=category,
            price=Decimal('99.99')
        )
        
        tag1 = ProductTag.objects.create(name="Wireless")
        tag2 = ProductTag.objects.create(name="Bluetooth")
        
        product.tags.add(tag1, tag2)
        
        self.assertEqual(product.tags.count(), 2)
        self.assertIn(tag1, product.tags.all())
        self.assertIn(tag2, product.tags.all())
        
        # Test reverse relationship
        self.assertIn(product, tag1.products.all())