'use client';

import { useAuthContext } from '../../providers';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div style={{
        minHeight: '50vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #2563eb',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <p style={{ color: '#666' }}>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-12">
          <div className="bg-white p-4 rounded shadow-sm border">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1 className="h3 mb-0">Dashboard</h1>
              <span className="badge bg-success">Welcome back!</span>
            </div>

            <div className="row mb-4">
              <div className="col-md-8">
                <div className="card border-primary">
                  <div className="card-header bg-primary text-white">
                    <h5 className="card-title mb-0">👋 Welcome, {user?.first_name}!</h5>
                  </div>
                  <div className="card-body">
                    <p className="card-text">
                      Thank you for joining our e-commerce platform. Your account has been successfully created.
                    </p>
                    <div className="row">
                      <div className="col-sm-6">
                        <strong>Email:</strong> {user?.email}
                      </div>
                      <div className="col-sm-6">
                        <strong>Username:</strong> {user?.username}
                      </div>
                      <div className="col-sm-6 mt-2">
                        <strong>Full Name:</strong> {user?.full_name}
                      </div>
                      <div className="col-sm-6 mt-2">
                        <strong>Member Since:</strong> {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card border-info">
                  <div className="card-header bg-info text-white">
                    <h6 className="card-title mb-0">Account Status</h6>
                  </div>
                  <div className="card-body">
                    <div className="d-flex align-items-center mb-2">
                      <span className={`badge ${user?.is_email_verified ? 'bg-success' : 'bg-warning'} me-2`}>
                        {user?.is_email_verified ? '✓ Verified' : '⚠ Unverified'}
                      </span>
                      <small className="text-muted">Email</small>
                    </div>
                    {!user?.is_email_verified && (
                      <small className="text-muted">
                        Please verify your email address to access all features.
                      </small>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="row g-3">
              <div className="col-md-3">
                <div className="card text-center h-100">
                  <div className="card-body">
                    <div className="display-6 text-primary mb-2">🛒</div>
                    <h6 className="card-title">Shop Products</h6>
                    <p className="card-text small text-muted">Browse our extensive catalog</p>
                    <a href="/products" className="btn btn-outline-primary btn-sm">Browse</a>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center h-100">
                  <div className="card-body">
                    <div className="display-6 text-success mb-2">📦</div>
                    <h6 className="card-title">My Orders</h6>
                    <p className="card-text small text-muted">Track your order history</p>
                    <a href="/orders" className="btn btn-outline-success btn-sm">View Orders</a>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center h-100">
                  <div className="card-body">
                    <div className="display-6 text-info mb-2">👤</div>
                    <h6 className="card-title">Profile</h6>
                    <p className="card-text small text-muted">Manage your account settings</p>
                    <a href="/profile" className="btn btn-outline-info btn-sm">Edit Profile</a>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center h-100">
                  <div className="card-body">
                    <div className="display-6 text-warning mb-2">🛍️</div>
                    <h6 className="card-title">Shopping Cart</h6>
                    <p className="card-text small text-muted">Review items in your cart</p>
                    <a href="/cart" className="btn btn-outline-warning btn-sm">View Cart</a>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <div className="alert alert-info" role="alert">
                <h6 className="alert-heading">🎉 Getting Started</h6>
                <p className="mb-0">
                  Your account is ready! Start by browsing our products or updating your profile information.
                  If you have any questions, don't hesitate to contact our support team.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}