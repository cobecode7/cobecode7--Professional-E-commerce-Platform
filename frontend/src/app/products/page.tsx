'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthContext } from '../../providers';
import { useCartStore } from '../../stores/cartStore';

interface Product {
  id: number;
  name: string;
  price: string;
  sale_price: string | null;
  current_price: number;
  category_name: string;
  sku: string;
  is_in_stock: boolean;
  is_featured: boolean;
  short_description: string;
  discount_percentage: number;
}

interface Category {
  id: number;
  name: string;
  slug: string;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  
  const { isAuthenticated } = useAuthContext();
  const { addToCart } = useCartStore();

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/products/');
      const data = await response.json();
      const productList = data.results || [];
      
      setAllProducts(productList);
      setProducts(productList);
      
      // Extract categories from products - SAFE IMPLEMENTATION
      const uniqueCategories = Array.from(
        new Set(productList.map((product: Product) => product.category_name))
      ).map((name, index) => ({
        id: index + 1,
        name: name as string,
        slug: (name as string).toLowerCase().replace(/\s+/g, '-')
      }));
      
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error fetching products:', error);
      // ALWAYS set fallback data to prevent undefined errors
      setCategories([
        { id: 1, name: 'Electronics', slug: 'electronics' },
        { id: 2, name: 'Clothing', slug: 'clothing' },
        { id: 3, name: 'Books', slug: 'books' }
      ]);
      setProducts([]);
      setAllProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const filterProducts = (category: string, search: string) => {
    let filtered = [...allProducts]; // Create copy to avoid mutations

    if (category) {
      filtered = filtered.filter(product => 
        product.category_name.toLowerCase() === category.toLowerCase()
      );
    }

    if (search) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(search.toLowerCase()) ||
        product.category_name.toLowerCase().includes(search.toLowerCase()) ||
        product.sku.toLowerCase().includes(search.toLowerCase())
      );
    }

    setProducts(filtered);
  };

  const handleCategoryChange = (categoryName: string) => {
    setSelectedCategory(categoryName);
    filterProducts(categoryName, searchTerm);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    filterProducts(selectedCategory, searchTerm);
  };

  const handleAddToCart = (product: Product) => {
    if (!isAuthenticated) {
      alert('Please login to add items to your cart!');
      return;
    }

    const cartProduct = {
      id: product.id,
      name: product.name,
      price: product.current_price || parseFloat(product.price),
      category_name: product.category_name,
      sku: product.sku
    };

    addToCart(cartProduct, 1);
    alert(`Added "${product.name}" to cart!`);
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading products...</span>
          </div>
          <p className="mt-3">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      {/* Navigation Breadcrumb */}
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link href="/" className="text-decoration-none">Home</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Products</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="row mb-4">
        <div className="col-md-6">
          <h1 className="display-6">Our Products</h1>
          <p className="text-muted">
            Discover our collection of {allProducts.length} products
          </p>
        </div>
        <div className="col-md-6 text-end">
          <Link href="/" className="btn btn-outline-secondary">
            ← Back to Home
          </Link>
        </div>
      </div>

      {/* Authentication Notice */}
      {!isAuthenticated && (
        <div className="alert alert-info" role="alert">
          <strong>Note:</strong> Please <Link href="/auth/login" className="alert-link">login</Link> to add items to your cart and access full functionality.
        </div>
      )}

      {/* Filters */}
      <div className="row mb-4">
        <div className="col-md-8">
          <form onSubmit={handleSearch} className="d-flex">
            <input
              type="text"
              className="form-control me-2"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button className="btn btn-primary" type="submit">
              Search
            </button>
          </form>
        </div>
        <div className="col-md-4">
          <select
            className="form-select"
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
          >
            <option value="">All Categories ({allProducts.length})</option>
            {Array.isArray(categories) && categories.length > 0 && categories.map((category) => (
              <option key={category.id} value={category.name}>
                {category.name} ({allProducts.filter(p => p.category_name === category.name).length})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Products Grid */}
      <div className="row g-4">
        {Array.isArray(products) && products.length > 0 ? (
          products.map((product) => (
            <div key={product.id} className="col-lg-4 col-md-6">
              <div className="card h-100 shadow-sm">
                {/* Product Image */}
                <div 
                  className="card-img-top d-flex align-items-center justify-content-center text-white position-relative"
                  style={{
                    height: '200px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  }}
                >
                  <span className="fs-5 fw-semibold">📦</span>
                  {product.discount_percentage > 0 && (
                    <span className="position-absolute top-0 end-0 badge bg-danger m-2">
                      -{product.discount_percentage}%
                    </span>
                  )}
                  {product.is_featured && (
                    <span className="position-absolute top-0 start-0 badge bg-warning m-2">
                      Featured
                    </span>
                  )}
                </div>

                {/* Product Info */}
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">{product.name}</h5>
                  <p className="card-text text-muted flex-grow-1">
                    {product.short_description || 'Premium quality product with excellent features.'}
                  </p>
                  
                  {/* Category and SKU */}
                  <div className="mb-2">
                    <small className="text-muted">
                      <span className="badge bg-light text-dark me-2">{product.category_name}</span>
                      SKU: {product.sku}
                    </small>
                  </div>

                  {/* Price and Actions */}
                  <div className="mt-auto">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <div>
                        {product.sale_price ? (
                          <>
                            <span className="h5 text-success mb-0">${product.sale_price}</span>
                            <small className="text-muted text-decoration-line-through ms-2">
                              ${product.price}
                            </small>
                          </>
                        ) : (
                          <span className="h5 text-primary mb-0">${product.price}</span>
                        )}
                      </div>
                      <div>
                        {product.is_in_stock ? (
                          <small className="text-success">✅ In Stock</small>
                        ) : (
                          <small className="text-danger">❌ Out of Stock</small>
                        )}
                      </div>
                    </div>

                    <div className="d-grid gap-2">
                      <button
                        className={`btn ${isAuthenticated ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => handleAddToCart(product)}
                        disabled={!product.is_in_stock}
                      >
                        {!product.is_in_stock 
                          ? 'Out of Stock' 
                          : isAuthenticated 
                            ? '🛒 Add to Cart'
                            : '🛒 Login to Add to Cart'
                        }
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-12">
            <div className="text-center py-5">
              <div className="mb-3">
                <span className="fs-1">🔍</span>
              </div>
              <h4>No products found</h4>
              <p className="text-muted">
                {searchTerm || selectedCategory 
                  ? 'Try adjusting your search or filter criteria' 
                  : 'Loading products or no products available'
                }
              </p>
              {(searchTerm || selectedCategory) && (
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setSelectedCategory('');
                    setSearchTerm('');
                    setProducts([...allProducts]);
                  }}
                >
                  Show All Products
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Results Summary */}
      <div className="text-center mt-5 mb-4">
        <p className="text-muted">
          Showing {Array.isArray(products) ? products.length : 0} of {Array.isArray(allProducts) ? allProducts.length : 0} products
          {selectedCategory && ` in ${selectedCategory}`}
          {searchTerm && ` matching "${searchTerm}"`}
        </p>
      </div>
    </div>
  );
}
