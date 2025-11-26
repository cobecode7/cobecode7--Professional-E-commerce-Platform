'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthContext } from '../providers';
import { useCartStore } from '../stores/cartStore';

export default function Navigation() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, isLoading } = useAuthContext();
  const { cart } = useCartStore();
  const cartCount = cart?.total_items || 0;

  const isActive = (path: string) => {
    return pathname === path ? 'active' : '';
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div className="container">
        {/* Brand */}
        <Link href="/" className="navbar-brand fw-bold fs-4">
          🛒 E-Commerce Platform
        </Link>

        {/* Mobile Toggle */}
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Navigation Links */}
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link href="/" className={`nav-link ${isActive('/')}`}>
                Home
              </Link>
            </li>
            <li className="nav-item">
              <Link href="/products" className={`nav-link ${isActive('/products')}`}>
                Products
              </Link>
            </li>
            <li className="nav-item dropdown">
              <a 
                className="nav-link dropdown-toggle" 
                href="#" 
                id="categoriesDropdown" 
                role="button" 
                data-bs-toggle="dropdown"
              >
                Categories
              </a>
              <ul className="dropdown-menu">
                <li><a className="dropdown-item" href="/products?category=electronics">Electronics</a></li>
                <li><a className="dropdown-item" href="/products?category=clothing">Clothing</a></li>
                <li><a className="dropdown-item" href="/products?category=books">Books</a></li>
                <li><hr className="dropdown-divider" /></li>
                <li><Link href="/products" className="dropdown-item">All Categories</Link></li>
              </ul>
            </li>
            <li className="nav-item">
              <Link href="/about" className={`nav-link ${isActive('/about')}`}>
                About
              </Link>
            </li>
          </ul>

          {/* Right Side Navigation */}
          <ul className="navbar-nav">
            {/* Search */}
            <li className="nav-item me-2">
              <form className="d-flex" role="search">
                <input 
                  className="form-control form-control-sm" 
                  type="search" 
                  placeholder="Search..." 
                  aria-label="Search"
                  style={{ width: '200px' }}
                />
              </form>
            </li>

            {/* Cart */}
            <li className="nav-item">
              <Link href="/cart" className={`nav-link position-relative ${isActive('/cart')}`}>
                🛒 Cart
                {cartCount > 0 && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                    {cartCount}
                  </span>
                )}
              </Link>
            </li>

            {/* User Menu - Dynamic based on authentication */}
            <li className="nav-item dropdown">
              <a 
                className="nav-link dropdown-toggle" 
                href="#" 
                id="userDropdown" 
                role="button" 
                data-bs-toggle="dropdown"
              >
                {isAuthenticated ? `👋 ${user?.first_name || 'Account'}` : 'Account'}
              </a>
              <ul className="dropdown-menu dropdown-menu-end">
                {!isAuthenticated ? (
                  // Not logged in menu
                  <>
                    <li><Link href="/auth/login" className="dropdown-item">Login</Link></li>
                    <li><Link href="/auth/register" className="dropdown-item">Register</Link></li>
                  </>
                ) : (
                  // Logged in menu
                  <>
                    <li>
                      <Link href="/dashboard" className="dropdown-item">
                        🏠 Dashboard
                      </Link>
                    </li>
                    <li><hr className="dropdown-divider" /></li>
                    <li><Link href="/profile" className="dropdown-item">👤 My Profile</Link></li>
                    <li><Link href="/orders" className="dropdown-item">📦 My Orders</Link></li>
                    <li><hr className="dropdown-divider" /></li>
                    <li>
                      <button 
                        className="dropdown-item" 
                        onClick={handleLogout}
                        disabled={isLoading}
                        style={{ 
                          border: 'none', 
                          background: 'transparent',
                          width: '100%',
                          textAlign: 'left',
                          cursor: isLoading ? 'wait' : 'pointer'
                        }}
                      >
                        {isLoading ? '⏳ Logging out...' : '🚪 Logout'}
                      </button>
                    </li>
                  </>
                )}
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <a 
                    className="dropdown-item" 
                    href="http://localhost:8000/admin/" 
                    target="_blank"
                  >
                    ⚙️ Admin Panel
                  </a>
                </li>
              </ul>
            </li>

            {/* API Links */}
            <li className="nav-item dropdown">
              <a 
                className="nav-link dropdown-toggle" 
                href="#" 
                id="apiDropdown" 
                role="button" 
                data-bs-toggle="dropdown"
              >
                API
              </a>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <a 
                    className="dropdown-item" 
                    href="http://localhost:8000/api/docs/" 
                    target="_blank"
                  >
                    📚 API Documentation
                  </a>
                </li>
                <li>
                  <a 
                    className="dropdown-item" 
                    href="http://localhost:8000/api/products/" 
                    target="_blank"
                  >
                    📦 Products API
                  </a>
                </li>
                <li>
                  <a 
                    className="dropdown-item" 
                    href="http://localhost:8000/api/schema/" 
                    target="_blank"
                  >
                    📋 API Schema
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}