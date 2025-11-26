'use client';

import Link from 'next/link';
import { useAuthContext } from '../../providers';
import { useCartStore } from '../../stores/cartStore';
import { useState } from 'react';

export default function CheckoutPage() {
  const { isAuthenticated, user } = useAuthContext();
  const { cart, clearCart } = useCartStore();
  const [step, setStep] = useState(1); // 1: Shipping, 2: Payment, 3: Review
  const [orderPlaced, setOrderPlaced] = useState(false);

  const [shippingInfo, setShippingInfo] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    email: user?.email || '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    phone: user?.phone_number || '',
  });

  const [paymentInfo, setPaymentInfo] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    nameOnCard: '',
  });

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const handlePlaceOrder = () => {
    // Simulate order placement
    setTimeout(() => {
      setOrderPlaced(true);
      clearCart();
    }, 2000);
  };

  if (!isAuthenticated) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <h1 className="display-4 mb-4">🛒 Checkout</h1>
          <div className="alert alert-info" role="alert">
            <h4 className="alert-heading">Please log in to continue</h4>
            <p>You need to be logged in to complete your purchase.</p>
          </div>
          <Link href="/auth/login" className="btn btn-primary btn-lg">
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
          <h1 className="display-4 mb-4">🛒 Checkout</h1>
          <div className="mb-4">
            <span className="display-1">🛍️</span>
          </div>
          <h3 className="mb-3">Your Cart is Empty</h3>
          <p className="text-muted mb-4">Add some items to your cart before checking out.</p>
          <Link href="/products" className="btn btn-primary btn-lg">
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  if (orderPlaced) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="mb-4">
            <span className="display-1 text-success">✅</span>
          </div>
          <h1 className="display-4 mb-4">Order Placed Successfully!</h1>
          <div className="alert alert-success" role="alert">
            <h4 className="alert-heading">Thank you for your order!</h4>
            <p>Your order has been placed successfully. You will receive a confirmation email shortly.</p>
            <hr />
            <p className="mb-0">Order Number: <strong>ORD-2024-{Date.now().toString().slice(-6)}</strong></p>
          </div>
          
          <div className="d-flex gap-3 justify-content-center">
            <Link href="/orders" className="btn btn-primary">
              View Orders
            </Link>
            <Link href="/products" className="btn btn-outline-primary">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const shippingCost = 9.99;
  const tax = cart.subtotal * 0.08; // 8% tax
  const total = cart.subtotal + shippingCost + tax;

  return (
    <div className="container py-4">
      {/* Navigation Breadcrumb */}
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link href="/" className="text-decoration-none">Home</Link>
          </li>
          <li className="breadcrumb-item">
            <Link href="/cart" className="text-decoration-none">Cart</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Checkout</li>
        </ol>
      </nav>

      {/* Header */}
      <h1 className="display-5 mb-4">🛒 Checkout</h1>

      {/* Progress Steps */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex justify-content-center">
            <div className="d-flex align-items-center">
              <div className={`rounded-circle d-flex align-items-center justify-content-center ${step >= 1 ? 'bg-primary text-white' : 'bg-light'}`} style={{ width: '40px', height: '40px' }}>
                {step > 1 ? '✓' : '1'}
              </div>
              <div className="px-3">Shipping</div>
              <div className={`border-bottom ${step > 1 ? 'border-primary' : 'border-light'}`} style={{ width: '100px' }}></div>
              
              <div className={`rounded-circle d-flex align-items-center justify-content-center ${step >= 2 ? 'bg-primary text-white' : 'bg-light'}`} style={{ width: '40px', height: '40px' }}>
                {step > 2 ? '✓' : '2'}
              </div>
              <div className="px-3">Payment</div>
              <div className={`border-bottom ${step > 2 ? 'border-primary' : 'border-light'}`} style={{ width: '100px' }}></div>
              
              <div className={`rounded-circle d-flex align-items-center justify-content-center ${step >= 3 ? 'bg-primary text-white' : 'bg-light'}`} style={{ width: '40px', height: '40px' }}>
                3
              </div>
              <div className="px-3">Review</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        {/* Main Content */}
        <div className="col-lg-8">
          <div className="card">
            <div className="card-body">
              {/* Step 1: Shipping Information */}
              {step === 1 && (
                <div>
                  <h4 className="mb-4">📍 Shipping Information</h4>
                  <form>
                    <div className="row g-3">
                      <div className="col-md-6">
                        <label className="form-label">First Name *</label>
                        <input
                          type="text"
                          className="form-control"
                          value={shippingInfo.firstName}
                          onChange={(e) => setShippingInfo({...shippingInfo, firstName: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Last Name *</label>
                        <input
                          type="text"
                          className="form-control"
                          value={shippingInfo.lastName}
                          onChange={(e) => setShippingInfo({...shippingInfo, lastName: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-12">
                        <label className="form-label">Email Address *</label>
                        <input
                          type="email"
                          className="form-control"
                          value={shippingInfo.email}
                          onChange={(e) => setShippingInfo({...shippingInfo, email: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-12">
                        <label className="form-label">Address *</label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Street address"
                          value={shippingInfo.address}
                          onChange={(e) => setShippingInfo({...shippingInfo, address: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">City *</label>
                        <input
                          type="text"
                          className="form-control"
                          value={shippingInfo.city}
                          onChange={(e) => setShippingInfo({...shippingInfo, city: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-md-3">
                        <label className="form-label">State *</label>
                        <select 
                          className="form-select"
                          value={shippingInfo.state}
                          onChange={(e) => setShippingInfo({...shippingInfo, state: e.target.value})}
                          required
                        >
                          <option value="">Select State</option>
                          <option value="CA">California</option>
                          <option value="NY">New York</option>
                          <option value="TX">Texas</option>
                          <option value="FL">Florida</option>
                        </select>
                      </div>
                      <div className="col-md-3">
                        <label className="form-label">ZIP Code *</label>
                        <input
                          type="text"
                          className="form-control"
                          value={shippingInfo.zipCode}
                          onChange={(e) => setShippingInfo({...shippingInfo, zipCode: e.target.value})}
                          required
                        />
                      </div>
                      <div className="col-12">
                        <label className="form-label">Phone Number</label>
                        <input
                          type="tel"
                          className="form-control"
                          value={shippingInfo.phone}
                          onChange={(e) => setShippingInfo({...shippingInfo, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="mt-4">
                      <button type="button" className="btn btn-primary" onClick={() => setStep(2)}>
                        Continue to Payment
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Step 2: Payment Information */}
              {step === 2 && (
                <div>
                  <h4 className="mb-4">💳 Payment Information</h4>
                  <form>
                    <div className="row g-3">
                      <div className="col-12">
                        <label className="form-label">Card Number *</label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="1234 5678 9012 3456"
                          value={paymentInfo.cardNumber}
                          onChange={(e) => setPaymentInfo({...paymentInfo, cardNumber: e.target.value})}
                        />
                      </div>
                      <div className="col-12">
                        <label className="form-label">Name on Card *</label>
                        <input
                          type="text"
                          className="form-control"
                          value={paymentInfo.nameOnCard}
                          onChange={(e) => setPaymentInfo({...paymentInfo, nameOnCard: e.target.value})}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Expiry Date *</label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="MM/YY"
                          value={paymentInfo.expiryDate}
                          onChange={(e) => setPaymentInfo({...paymentInfo, expiryDate: e.target.value})}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">CVV *</label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="123"
                          value={paymentInfo.cvv}
                          onChange={(e) => setPaymentInfo({...paymentInfo, cvv: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="mt-4 d-flex gap-2">
                      <button type="button" className="btn btn-outline-secondary" onClick={() => setStep(1)}>
                        Back to Shipping
                      </button>
                      <button type="button" className="btn btn-primary" onClick={() => setStep(3)}>
                        Review Order
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Step 3: Order Review */}
              {step === 3 && (
                <div>
                  <h4 className="mb-4">📋 Review Your Order</h4>
                  
                  {/* Order Items */}
                  <div className="mb-4">
                    <h6>Order Items</h6>
                    {cart.items.map((item) => (
                      <div key={item.id} className="d-flex align-items-center py-2 border-bottom">
                        <div className="bg-primary text-white rounded me-3 d-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                          📦
                        </div>
                        <div className="flex-grow-1">
                          <div className="fw-semibold">{item.product.name}</div>
                          <small className="text-muted">Qty: {item.quantity}</small>
                        </div>
                        <div className="text-end">
                          <div className="fw-bold">{formatPrice(item.total_price)}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Shipping Info */}
                  <div className="mb-4">
                    <h6>Shipping Address</h6>
                    <div className="bg-light p-3 rounded">
                      <div>{shippingInfo.firstName} {shippingInfo.lastName}</div>
                      <div>{shippingInfo.address}</div>
                      <div>{shippingInfo.city}, {shippingInfo.state} {shippingInfo.zipCode}</div>
                      {shippingInfo.phone && <div>{shippingInfo.phone}</div>}
                    </div>
                  </div>

                  {/* Payment Info */}
                  <div className="mb-4">
                    <h6>Payment Method</h6>
                    <div className="bg-light p-3 rounded">
                      <div>💳 **** **** **** {paymentInfo.cardNumber.slice(-4)}</div>
                      <div>{paymentInfo.nameOnCard}</div>
                    </div>
                  </div>

                  <div className="d-flex gap-2">
                    <button type="button" className="btn btn-outline-secondary" onClick={() => setStep(2)}>
                      Back to Payment
                    </button>
                    <button type="button" className="btn btn-success" onClick={handlePlaceOrder}>
                      🛒 Place Order
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Order Summary Sidebar */}
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Order Summary</h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal ({cart.total_items} items)</span>
                <span>{formatPrice(cart.subtotal)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping</span>
                <span>{formatPrice(shippingCost)}</span>
              </div>
              <div className="d-flex justify-content-between mb-3">
                <span>Tax</span>
                <span>{formatPrice(tax)}</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <span className="h6">Total</span>
                <span className="h6 text-primary">{formatPrice(total)}</span>
              </div>
              
              <div className="text-center">
                <small className="text-muted">🔒 Secure checkout with SSL encryption</small>
              </div>
            </div>
          </div>

          {/* Demo Notice */}
          <div className="alert alert-warning mt-3" role="alert">
            <small>
              <strong>Demo Mode:</strong> No actual payment will be processed. This is for demonstration purposes only.
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}