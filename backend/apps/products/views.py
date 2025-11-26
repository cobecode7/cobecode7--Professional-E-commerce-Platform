"""API views for products app."""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Category, Product, ProductTag, Inventory
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductTagSerializer, InventorySerializer,
    ProductSearchSerializer
)


class CategoryListView(generics.ListCreateAPIView):
    """List and create categories."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get active categories with no parent (top level)."""
        return Category.objects.filter(is_active=True, parent=None).order_by('sort_order', 'name')


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a category."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active categories."""
        return Category.objects.filter(is_active=True)


class ProductListView(generics.ListCreateAPIView):
    """List and create products."""
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'view_count', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Get filtered products."""
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(manage_stock=False, stock_status='in_stock') |
                Q(manage_stock=True, stock_quantity__gt=0)
            )
        
        # Filter by featured products
        is_featured = self.request.query_params.get('is_featured')
        if is_featured and is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter by tags
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()
        
        return queryset.prefetch_related('images', 'tags')
    
    @extend_schema(
        parameters=[
            OpenApiParameter('category', OpenApiTypes.INT, description='Category ID'),
            OpenApiParameter('min_price', OpenApiTypes.NUMBER, description='Minimum price'),
            OpenApiParameter('max_price', OpenApiTypes.NUMBER, description='Maximum price'),
            OpenApiParameter('in_stock', OpenApiTypes.BOOL, description='Filter by stock availability'),
            OpenApiParameter('is_featured', OpenApiTypes.BOOL, description='Filter featured products'),
            OpenApiParameter('tags', OpenApiTypes.STR, description='Filter by tag names (comma-separated)'),
        ]
    )
    def get(self, request, *args, **kwargs):
        """Get filtered product list."""
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product."""
    
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active products."""
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related(
            'images', 'variants', 'tags'
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve product and increment view count."""
        instance = self.get_object()
        
        # Increment view count
        Product.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedProductsView(generics.ListAPIView):
    """Get featured products."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get featured products."""
        return Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category').prefetch_related('images', 'tags')[:10]


class ProductTagListView(generics.ListCreateAPIView):
    """List and create product tags."""
    
    serializer_class = ProductTagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get all tags ordered by name."""
        return ProductTag.objects.all().order_by('name')


@extend_schema(
    request=ProductSearchSerializer,
    responses=ProductListSerializer(many=True),
    description="Advanced product search"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def product_search(request):
    """Advanced product search."""
    serializer = ProductSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = Product.objects.filter(is_active=True)
    
    # Text search
    if 'q' in data:
        query = data['q']
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Category filter
    if 'category' in data:
        queryset = queryset.filter(category_id=data['category'])
    
    # Price range
    if 'min_price' in data:
        queryset = queryset.filter(price__gte=data['min_price'])
    if 'max_price' in data:
        queryset = queryset.filter(price__lte=data['max_price'])
    
    # Stock filter
    if 'in_stock' in data and data['in_stock']:
        queryset = queryset.filter(
            Q(manage_stock=False, stock_status='in_stock') |
            Q(manage_stock=True, stock_quantity__gt=0)
        )
    
    # Featured filter
    if 'is_featured' in data:
        queryset = queryset.filter(is_featured=data['is_featured'])
    
    # Tags filter
    if 'tags' in data:
        queryset = queryset.filter(tags__name__in=data['tags']).distinct()
    
    # Ordering
    ordering = data.get('ordering', '-created_at')
    queryset = queryset.order_by(ordering)
    
    # Select related and prefetch for performance
    queryset = queryset.select_related('category').prefetch_related('images', 'tags')
    
    # Paginate results
    page = request.query_params.get('page', 1)
    page_size = min(int(request.query_params.get('page_size', 20)), 100)
    
    start = (int(page) - 1) * page_size
    end = start + page_size
    
    products = queryset[start:end]
    total_count = queryset.count()
    
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': int(page),
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    })


@extend_schema(
    responses=CategorySerializer(many=True),
    description="Get category tree structure"
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def category_tree(request):
    """Get complete category tree."""
    categories = Category.objects.filter(
        is_active=True
    ).select_related('parent').order_by('sort_order', 'name')
    
    serializer = CategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)


class InventoryListView(generics.ListCreateAPIView):
    """List and create inventory logs."""
    
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get inventory logs with optional product filter."""
        queryset = Inventory.objects.select_related('product', 'variant')
        
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.order_by('-created_at')


@extend_schema(
    responses={200: 'Product recommendations'},
    description="Get product recommendations"
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_recommendations(request, product_id):
    """Get product recommendations based on category and tags."""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get products from same category
    recommendations = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)
    
    # Get products with similar tags
    product_tags = product.tags.all()
    if product_tags.exists():
        similar_products = Product.objects.filter(
            tags__in=product_tags,
            is_active=True
        ).exclude(id=product.id).distinct()
        
        # Combine and deduplicate
        recommendations = recommendations.union(similar_products)
    
    # Limit to 10 recommendations
    recommendations = recommendations.select_related('category').prefetch_related('images', 'tags')[:10]
    
    serializer = ProductListSerializer(recommendations, many=True, context={'request': request})
    return Response(serializer.data)
