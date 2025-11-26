/**
 * Shopping Cart Page
 * Displays cart items and checkout functionality
 */

'use client';

import Link from 'next/link';
import { useAuthContext } from '../../providers';
import { useCartStore } from '../../stores/cartStore';

export default function CartPage() {
  const { isAuthenticated } = useAuthContext();
  const { cart, removeFromCart, updateCartItem, clearCart } = useCartStore();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  if (!isAuthenticated) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <h1 className="display-4 mb-4">🛒 Shopping Cart</h1>
          <div className="alert alert-info" role="alert">
            <h4 className="alert-heading">Please log in to view your cart</h4>
            <p>You need to be logged in to access your shopping cart and make purchases.</p>
          </div>
          <Link
            href="/auth/login"
            className="btn btn-primary btn-lg"
          >
            Log In
          </Link>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <h1 className="display-4 mb-4">🛒 Shopping Cart</h1>
          <div className="mb-4">
            <span className="display-1">🛍️</span>
          </div>
          <h3 className="mb-3">Your Cart is Empty</h3>
          <p className="text-muted mb-4">Looks like you haven't added anything to your cart yet.</p>
          <Link
            href="/products"
            className="btn btn-primary btn-lg"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      {/* Navigation Breadcrumb */}
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link href="/" className="text-decoration-none">Home</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Cart</li>
        </ol>
      </nav>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="display-5">🛒 Shopping Cart</h1>
        <button
          onClick={() => clearCart()}
          className="btn btn-outline-danger"
        >
          Clear Cart
        </button>
      </div>

      <div className="row g-4">
        {/* Cart Items */}
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                Cart Items ({cart.total_items} {cart.total_items === 1 ? 'item' : 'items'})
              </h5>
            </div>
            <div className="card-body">
              {cart.items.map((item) => (
                <div key={item.id} className="row align-items-center border-bottom py-3">
                  {/* Product Image Placeholder */}
                  <div className="col-md-2">
                    <div 
                      className="bg-primary text-white d-flex align-items-center justify-content-center rounded"
                      style={{ height: '80px', width: '80px' }}
                    >
                      <span className="fs-4">📦</span>
                    </div>
                  </div>
                  
                  {/* Product Details */}
                  <div className="col-md-4">
                    <h6 className="mb-1">{item.product.name}</h6>
                    <small className="text-muted">
                      <span className="badge bg-light text-dark me-2">{item.product.category_name}</span>
                      SKU: {item.product.sku}
                    </small>
                  </div>
                  
                  {/* Quantity Controls */}
                  <div className="col-md-2">
                    <div className="input-group input-group-sm">
                      <button 
                        className="btn btn-outline-secondary"
                        onClick={() => updateCartItem(item.id, item.quantity - 1)}
                        disabled={item.quantity <= 1}
                      >
                        -
                      </button>
                      <input 
                        type="number" 
                        className="form-control text-center"
                        value={item.quantity}
                        onChange={(e) => {
                          const newQuantity = parseInt(e.target.value) || 1;
                          updateCartItem(item.id, newQuantity);
                        }}
                        min="1"
                        style={{ maxWidth: '60px' }}
                      />
                      <button 
                        className="btn btn-outline-secondary"
                        onClick={() => updateCartItem(item.id, item.quantity + 1)}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  
                  {/* Price */}
                  <div className="col-md-2">
                    <div className="text-center">
                      <div className="fw-bold text-primary">{formatPrice(item.total_price)}</div>
                      <small className="text-muted">{formatPrice(item.unit_price)} each</small>
                    </div>
                  </div>
                  
                  {/* Remove Button */}
                  <div className="col-md-2">
                    <button 
                      className="btn btn-outline-danger btn-sm"
                      onClick={() => removeFromCart(item.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Order Summary</h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-3">
                <span>Subtotal ({cart.total_items} items)</span>
                <span className="fw-bold">{formatPrice(cart.subtotal)}</span>
              </div>
              
              <div className="d-flex justify-content-between mb-3">
                <span className="text-muted">Shipping</span>
                <span className="text-muted">Calculated at checkout</span>
              </div>
              
              <div className="d-flex justify-content-between mb-3">
                <span className="text-muted">Tax</span>
                <span className="text-muted">Calculated at checkout</span>
              </div>
              
              <hr />
              
              <div className="d-flex justify-content-between mb-4">
                <span className="h5">Total</span>
                <span className="h5 text-primary">{formatPrice(cart.subtotal)}</span>
              </div>

              <div className="d-grid gap-2">
                <Link
                  href="/checkout"
                  className="btn btn-primary btn-lg text-decoration-none"
                >
                  Proceed to Checkout
                </Link>
                
                <Link
                  href="/products"
                  className="btn btn-outline-secondary"
                >
                  Continue Shopping
                </Link>
              </div>
              
              <div className="mt-3 text-center">
                <small className="text-muted">
                  🔒 Secure checkout with SSL encryption
                </small>
              </div>
            </div>
          </div>
          
          {/* Security Notice */}
          <div className="alert alert-info mt-3" role="alert">
            <small>
              <strong>Demo Mode:</strong> This is a demonstration cart. No actual purchases will be made.
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}
