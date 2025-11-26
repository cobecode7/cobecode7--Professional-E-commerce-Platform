'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Product {
  id: number;
  name: string;
  price: string;
  sale_price: string | null;
  current_price: number;
  category_name: string;
  sku: string;
  is_featured: boolean;
  discount_percentage: number;
}

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'loading'>('loading');

  useEffect(() => {
    fetchFeaturedProducts();
  }, []);

  const fetchFeaturedProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/products/?is_featured=true');
      const data = await response.json();
      setFeaturedProducts(data.results || []);
      setApiStatus('connected');
    } catch (error) {
      console.error('Error fetching featured products:', error);
      setApiStatus('disconnected');
    }
  };

  return (
    <div>
      {/* Hero Section - Remove navbar since it's in layout now */}
      <div className="bg-primary text-white py-5" style={{
        background: 'linear-gradient(135deg, #007bff 0%, #6f42c1 100%) !important'
      }}>
        <div className="container text-center">
          <h1 className="display-4 fw-bold mb-4">
            Professional E-Commerce Platform
          </h1>
          <p className="lead mb-4">
            Modern full-stack e-commerce built with Django REST Framework and Next.js
          </p>
          <div className="d-flex justify-content-center gap-3">
            <Link href="/products" className="btn btn-light btn-lg">
              🛍️ Browse Products
            </Link>
            <a href="http://localhost:8000/api/docs/" className="btn btn-outline-light btn-lg" target="_blank">
              📚 View API Docs
            </a>
          </div>
        </div>
      </div>

      <div className="container mt-5">
        {/* API Status */}
        <div className="row mb-4">
          <div className="col-12">
            <div className={`alert ${apiStatus === 'connected' ? 'alert-success' : apiStatus === 'disconnected' ? 'alert-danger' : 'alert-info'} d-flex align-items-center`}>
              <strong className="me-2">API Status:</strong>
              <span className={`badge ${apiStatus === 'connected' ? 'bg-success' : apiStatus === 'disconnected' ? 'bg-danger' : 'bg-warning'}`}>
                {apiStatus === 'loading' ? 'Checking...' : apiStatus}
              </span>
              <small className="ms-auto text-muted">
                Backend: http://localhost:8000
              </small>
            </div>
          </div>
        </div>

        {/* Featured Products */}
        {apiStatus === 'connected' && featuredProducts.length > 0 && (
          <div className="row mb-5">
            <div className="col-12">
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h2>Featured Products</h2>
                <Link href="/products" className="btn btn-outline-primary">
                  View All Products
                </Link>
              </div>
              <div className="row g-4">
                {featuredProducts.slice(0, 3).map((product) => (
                  <div key={product.id} className="col-md-4">
                    <div className="card h-100 shadow-sm">
                      <div 
                        className="card-img-top d-flex align-items-center justify-content-center text-white position-relative"
                        style={{
                          height: '200px',
                          background: 'linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%)'
                        }}
                      >
                        <span className="fs-5 fw-semibold">📦</span>
                        {product.discount_percentage > 0 && (
                          <span className="position-absolute top-0 end-0 badge bg-danger m-2">
                            -{product.discount_percentage}%
                          </span>
                        )}
                        <span className="position-absolute top-0 start-0 badge bg-warning m-2">
                          Featured
                        </span>
                      </div>
                      <div className="card-body d-flex flex-column">
                        <h5 className="card-title">{product.name}</h5>
                        <p className="card-text text-muted flex-grow-1">
                          <span className="badge bg-light text-dark me-2">{product.category_name}</span>
                          SKU: {product.sku}
                        </p>
                        <div className="mt-auto">
                          <div className="d-flex justify-content-between align-items-center">
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
                            <Link href="/products" className="btn btn-primary btn-sm">
                              View Details
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Features */}
        <div className="row mb-5">
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">🛍️ Product Catalog</h5>
                <p className="card-text">
                  Complete product management with categories, variants, and inventory tracking.
                </p>
                <div className="d-flex gap-2">
                  <Link href="/products" className="btn btn-primary btn-sm">
                    Browse Products
                  </Link>
                  <a href="http://localhost:8000/api/products/" className="btn btn-outline-secondary btn-sm" target="_blank">
                    View API
                  </a>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">🛒 Shopping Cart</h5>
                <p className="card-text">
                  Cart management, order processing, and checkout functionality.
                </p>
                <div className="d-flex gap-2">
                  <Link href="/cart" className="btn btn-primary btn-sm">
                    View Cart
                  </Link>
                  <a href="http://localhost:8000/api/orders/" className="btn btn-outline-secondary btn-sm" target="_blank">
                    View API
                  </a>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">👥 User Management</h5>
                <p className="card-text">
                  Authentication, user profiles, and address management system.
                </p>
                <div className="d-flex gap-2">
                  <Link href="/auth/login" className="btn btn-primary btn-sm">
                    Login
                  </Link>
                  <a href="http://localhost:8000/api/accounts/" className="btn btn-outline-secondary btn-sm" target="_blank">
                    View API
                  </a>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">📚 API Documentation</h5>
                <p className="card-text">
                  Interactive Swagger UI with all endpoints documented and testable.
                </p>
                <div className="d-flex gap-2">
                  <a href="http://localhost:8000/api/docs/" className="btn btn-success btn-sm" target="_blank">
                    Open Swagger UI
                  </a>
                  <a href="http://localhost:8000/admin/" className="btn btn-outline-secondary btn-sm" target="_blank">
                    Admin Panel
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="row text-center mb-5">
          <div className="col-md-3 mb-3">
            <div className="card border-0 bg-transparent">
              <div className="card-body">
                <div className="text-primary fs-1 mb-3">📦</div>
                <h5 className="card-title">{featuredProducts.length > 0 ? '12+' : '0'}</h5>
                <p className="card-text text-muted">Products Available</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card border-0 bg-transparent">
              <div className="card-body">
                <div className="text-success fs-1 mb-3">📊</div>
                <h5 className="card-title">32+</h5>
                <p className="card-text text-muted">API Endpoints</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card border-0 bg-transparent">
              <div className="card-body">
                <div className="text-info fs-1 mb-3">🔒</div>
                <h5 className="card-title">100%</h5>
                <p className="card-text text-muted">Secure</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card border-0 bg-transparent">
              <div className="card-body">
                <div className="text-warning fs-1 mb-3">⚡</div>
                <h5 className="card-title">Fast</h5>
                <p className="card-text text-muted">Performance</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-dark text-white py-4 mt-5">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <h6>Professional E-Commerce Platform</h6>
              <p className="mb-0 text-light">
                Built with Django 5.2, Next.js 15, TypeScript, and Bootstrap 5
              </p>
            </div>
            <div className="col-md-6 text-end">
              <a href="http://localhost:8000/api/docs/" className="btn btn-outline-light btn-sm me-2" target="_blank">
                API Docs
              </a>
              <a href="http://localhost:8000/admin/" className="btn btn-outline-light btn-sm" target="_blank">
                Admin
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
