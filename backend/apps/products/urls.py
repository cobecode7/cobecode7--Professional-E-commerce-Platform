from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/tree/', views.category_tree, name='category-tree'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Product endpoints
    path('', views.ProductListView.as_view(), name='product-list'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('search/', views.product_search, name='product-search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:product_id>/recommendations/', views.product_recommendations, name='product-recommendations'),
    
    # Tag endpoints
    path('tags/', views.ProductTagListView.as_view(), name='tag-list'),
    
    # Inventory endpoints
    path('inventory/', views.InventoryListView.as_view(), name='inventory-list'),
]
