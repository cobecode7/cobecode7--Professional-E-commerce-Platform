'use client';

import Link from 'next/link';
import { useAuthContext } from '../../providers';
import { useEffect, useState } from 'react';

interface OrderItem {
  id: number;
  product_name: string;
  product_sku: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

interface Order {
  id: string;
  order_number: string;
  status: string;
  items: OrderItem[];
  subtotal: number;
  shipping_cost: number;
  total_amount: number;
  total_items: number;
  created_at: string;
  shipped_at?: string;
  delivered_at?: string;
}

export default function OrdersPage() {
  const { isAuthenticated, user, isLoading } = useAuthContext();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      // Simulate loading orders
      setTimeout(() => {
        // Demo orders
        const demoOrders: Order[] = [
          {
            id: '1',
            order_number: 'ORD-2024-001',
            status: 'delivered',
            items: [
              {
                id: 1,
                product_name: 'Premium Wireless Headphones',
                product_sku: 'WH-001',
                quantity: 1,
                unit_price: 199.99,
                total_price: 199.99,
              },
              {
                id: 2,
                product_name: 'Smartphone Case',
                product_sku: 'SC-002',
                quantity: 2,
                unit_price: 29.99,
                total_price: 59.98,
              }
            ],
            subtotal: 259.97,
            shipping_cost: 9.99,
            total_amount: 269.96,
            total_items: 3,
            created_at: '2024-09-15T10:30:00Z',
            shipped_at: '2024-09-16T14:20:00Z',
            delivered_at: '2024-09-18T16:45:00Z',
          },
          {
            id: '2',
            order_number: 'ORD-2024-002',
            status: 'shipped',
            items: [
              {
                id: 3,
                product_name: 'Gaming Mouse',
                product_sku: 'GM-003',
                quantity: 1,
                unit_price: 89.99,
                total_price: 89.99,
              }
            ],
            subtotal: 89.99,
            shipping_cost: 5.99,
            total_amount: 95.98,
            total_items: 1,
            created_at: '2024-09-28T09:15:00Z',
            shipped_at: '2024-09-30T11:30:00Z',
          },
        ];
        setOrders(demoOrders);
        setLoading(false);
      }, 1000);
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'badge bg-warning',
      paid: 'badge bg-info',
      processing: 'badge bg-primary',
      shipped: 'badge bg-success',
      delivered: 'badge bg-success',
      cancelled: 'badge bg-danger',
    };
    return badges[status] || 'badge bg-secondary';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, string> = {
      pending: '⏳',
      paid: '💳',
      processing: '📦',
      shipped: '🚚',
      delivered: '✅',
      cancelled: '❌',
    };
    return icons[status] || '📋';
  };

  if (isLoading || loading) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading orders...</span>
          </div>
          <p className="mt-3">Loading your orders...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <h1 className="display-4 mb-4">📦 My Orders</h1>
          <div className="alert alert-info" role="alert">
            <h4 className="alert-heading">Please log in to view your orders</h4>
            <p>You need to be logged in to access your order history.</p>
          </div>
          <Link href="/auth/login" className="btn btn-primary btn-lg">
            Log In
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
          <li className="breadcrumb-item">
            <Link href="/dashboard" className="text-decoration-none">Dashboard</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Orders</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="display-5">📦 My Orders</h1>
          <p className="text-muted">Welcome back, {user?.first_name}! Here are your recent orders.</p>
        </div>
        <Link href="/products" className="btn btn-primary">
          Continue Shopping
        </Link>
      </div>

      {orders.length === 0 ? (
        <div className="text-center py-5">
          <div className="mb-4">
            <span className="display-1">📦</span>
          </div>
          <h3 className="mb-3">No Orders Yet</h3>
          <p className="text-muted mb-4">You haven't placed any orders yet. Start shopping to see your orders here!</p>
          <Link href="/products" className="btn btn-primary btn-lg">
            Start Shopping
          </Link>
        </div>
      ) : (
        <div className="row g-4">
          {orders.map((order) => (
            <div key={order.id} className="col-12">
              <div className="card">
                <div className="card-header">
                  <div className="row align-items-center">
                    <div className="col-md-3">
                      <h6 className="mb-0">Order #{order.order_number}</h6>
                      <small className="text-muted">Placed on {formatDate(order.created_at)}</small>
                    </div>
                    <div className="col-md-2">
                      <span className={getStatusBadge(order.status)}>
                        {getStatusIcon(order.status)} {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                      </span>
                    </div>
                    <div className="col-md-2">
                      <strong>{formatPrice(order.total_amount)}</strong>
                      <br />
                      <small className="text-muted">{order.total_items} items</small>
                    </div>
                    <div className="col-md-3">
                      {order.delivered_at && (
                        <small className="text-success">
                          ✅ Delivered on {formatDate(order.delivered_at)}
                        </small>
                      )}
                      {order.shipped_at && !order.delivered_at && (
                        <small className="text-info">
                          🚚 Shipped on {formatDate(order.shipped_at)}
                        </small>
                      )}
                    </div>
                    <div className="col-md-2 text-end">
                      <button 
                        className="btn btn-outline-primary btn-sm"
                        onClick={() => alert(`Order details for ${order.order_number} - Coming soon!`)}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
                <div className="card-body">
                  <div className="row">
                    {order.items.map((item, index) => (
                      <div key={item.id} className="col-md-6 col-lg-4 mb-2">
                        <div className="d-flex align-items-center">
                          <div 
                            className="bg-primary text-white d-flex align-items-center justify-content-center rounded me-3"
                            style={{ width: '40px', height: '40px', fontSize: '1.2rem' }}
                          >
                            📦
                          </div>
                          <div>
                            <div className="fw-semibold">{item.product_name}</div>
                            <small className="text-muted">
                              Qty: {item.quantity} × {formatPrice(item.unit_price)}
                            </small>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="row mt-3 pt-3 border-top">
                    <div className="col-md-6">
                      <div className="d-flex gap-2">
                        <button 
                          className="btn btn-outline-secondary btn-sm"
                          onClick={() => alert('Track order feature coming soon!')}
                        >
                          📍 Track Order
                        </button>
                        <button 
                          className="btn btn-outline-info btn-sm"
                          onClick={() => alert('Download invoice feature coming soon!')}
                        >
                          📄 Invoice
                        </button>
                        {order.status === 'delivered' && (
                          <button 
                            className="btn btn-outline-warning btn-sm"
                            onClick={() => alert('Write review feature coming soon!')}
                          >
                            ⭐ Review
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="col-md-6 text-end">
                      <div className="small text-muted">
                        <div>Subtotal: {formatPrice(order.subtotal)}</div>
                        <div>Shipping: {formatPrice(order.shipping_cost)}</div>
                        <div className="fw-bold text-dark">Total: {formatPrice(order.total_amount)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Demo Notice */}
      <div className="alert alert-info mt-4" role="alert">
        <small>
          <strong>Demo Mode:</strong> These are sample orders for demonstration purposes. In a real application, this data would come from your actual order history.
        </small>
      </div>
    </div>
  );
}