'use client';

import Link from 'next/link';
import { useAuthContext } from '../../providers';
import { useState, useEffect } from 'react';

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const [activeTab, setActiveTab] = useState('profile');
  const [editMode, setEditMode] = useState(false);
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    username: '',
    phone_number: '',
    date_of_birth: '',
  });

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        username: user.username || '',
        phone_number: user.phone_number || '',
        date_of_birth: user.date_of_birth || '',
      });
    }
  }, [user]);

  const handleSaveProfile = () => {
    // In a real app, this would make an API call
    alert('Profile updated successfully! (Demo mode)');
    setEditMode(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value,
    });
  };

  if (isLoading) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading profile...</span>
          </div>
          <p className="mt-3">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <h1 className="display-4 mb-4">👤 My Profile</h1>
          <div className="alert alert-info" role="alert">
            <h4 className="alert-heading">Please log in to view your profile</h4>
            <p>You need to be logged in to access your profile settings.</p>
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
          <li className="breadcrumb-item active" aria-current="page">Profile</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex align-items-center">
            <div 
              className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-4"
              style={{ width: '80px', height: '80px', fontSize: '2rem' }}
            >
              👤
            </div>
            <div>
              <h1 className="display-6 mb-1">My Profile</h1>
              <p className="text-muted mb-0">Manage your account settings and preferences</p>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Sidebar Navigation */}
        <div className="col-md-3">
          <div className="card">
            <div className="card-body p-0">
              <nav className="nav flex-column">
                <button
                  className={`nav-link border-0 text-start ${activeTab === 'profile' ? 'active bg-primary text-white' : 'text-dark'}`}
                  onClick={() => setActiveTab('profile')}
                >
                  👤 Profile Information
                </button>
                <button
                  className={`nav-link border-0 text-start ${activeTab === 'security' ? 'active bg-primary text-white' : 'text-dark'}`}
                  onClick={() => setActiveTab('security')}
                >
                  🔒 Security Settings
                </button>
                <button
                  className={`nav-link border-0 text-start ${activeTab === 'addresses' ? 'active bg-primary text-white' : 'text-dark'}`}
                  onClick={() => setActiveTab('addresses')}
                >
                  📍 Addresses
                </button>
                <button
                  className={`nav-link border-0 text-start ${activeTab === 'preferences' ? 'active bg-primary text-white' : 'text-dark'}`}
                  onClick={() => setActiveTab('preferences')}
                >
                  ⚙️ Preferences
                </button>
              </nav>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="col-md-9">
          <div className="card">
            <div className="card-body">
              {/* Profile Information Tab */}
              {activeTab === 'profile' && (
                <div>
                  <div className="d-flex justify-content-between align-items-center mb-4">
                    <h4>Profile Information</h4>
                    <button
                      className={`btn ${editMode ? 'btn-success' : 'btn-outline-primary'}`}
                      onClick={editMode ? handleSaveProfile : () => setEditMode(true)}
                    >
                      {editMode ? '💾 Save Changes' : '✏️ Edit Profile'}
                    </button>
                  </div>

                  <form>
                    <div className="row g-3">
                      <div className="col-md-6">
                        <label className="form-label">First Name</label>
                        <input
                          type="text"
                          className="form-control"
                          name="first_name"
                          value={profileData.first_name}
                          onChange={handleChange}
                          disabled={!editMode}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Last Name</label>
                        <input
                          type="text"
                          className="form-control"
                          name="last_name"
                          value={profileData.last_name}
                          onChange={handleChange}
                          disabled={!editMode}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Username</label>
                        <input
                          type="text"
                          className="form-control"
                          name="username"
                          value={profileData.username}
                          onChange={handleChange}
                          disabled={!editMode}
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Email Address</label>
                        <input
                          type="email"
                          className="form-control"
                          name="email"
                          value={profileData.email}
                          onChange={handleChange}
                          disabled={!editMode}
                        />
                        <div className="form-text">
                          {user?.is_email_verified ? (
                            <span className="text-success">✅ Email verified</span>
                          ) : (
                            <span className="text-warning">⚠️ Email not verified</span>
                          )}
                        </div>
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Phone Number</label>
                        <input
                          type="tel"
                          className="form-control"
                          name="phone_number"
                          value={profileData.phone_number}
                          onChange={handleChange}
                          disabled={!editMode}
                          placeholder="(Optional)"
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Date of Birth</label>
                        <input
                          type="date"
                          className="form-control"
                          name="date_of_birth"
                          value={profileData.date_of_birth}
                          onChange={handleChange}
                          disabled={!editMode}
                        />
                      </div>
                    </div>

                    {editMode && (
                      <div className="mt-4">
                        <button
                          type="button"
                          className="btn btn-secondary me-2"
                          onClick={() => {
                            setEditMode(false);
                            // Reset form data
                            if (user) {
                              setProfileData({
                                first_name: user.first_name || '',
                                last_name: user.last_name || '',
                                email: user.email || '',
                                username: user.username || '',
                                phone_number: user.phone_number || '',
                                date_of_birth: user.date_of_birth || '',
                              });
                            }
                          }}
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={handleSaveProfile}
                        >
                          Save Changes
                        </button>
                      </div>
                    )}
                  </form>
                </div>
              )}

              {/* Security Settings Tab */}
              {activeTab === 'security' && (
                <div>
                  <h4 className="mb-4">Security Settings</h4>
                  
                  <div className="card bg-light mb-4">
                    <div className="card-body">
                      <h6>Password Security</h6>
                      <p className="mb-3">Keep your account secure by using a strong password.</p>
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => alert('Change password feature coming soon!')}
                      >
                        🔑 Change Password
                      </button>
                    </div>
                  </div>

                  <div className="card bg-light mb-4">
                    <div className="card-body">
                      <h6>Two-Factor Authentication</h6>
                      <p className="mb-3">Add an extra layer of security to your account.</p>
                      <button 
                        className="btn btn-outline-success"
                        onClick={() => alert('2FA setup coming soon!')}
                      >
                        🛡️ Enable 2FA
                      </button>
                    </div>
                  </div>

                  <div className="card bg-light">
                    <div className="card-body">
                      <h6>Login History</h6>
                      <p className="mb-3">Review recent login activity on your account.</p>
                      <div className="small text-muted">
                        <div className="mb-1">✅ Current session - {new Date().toLocaleString()}</div>
                        <div>📍 Location: Unknown • Device: Browser</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Addresses Tab */}
              {activeTab === 'addresses' && (
                <div>
                  <div className="d-flex justify-content-between align-items-center mb-4">
                    <h4>Saved Addresses</h4>
                    <button 
                      className="btn btn-primary"
                      onClick={() => alert('Add address feature coming soon!')}
                    >
                      ➕ Add New Address
                    </button>
                  </div>

                  <div className="text-center py-5">
                    <span className="display-1">📍</span>
                    <h5 className="mt-3 mb-3">No Addresses Saved</h5>
                    <p className="text-muted mb-4">Save your shipping and billing addresses for faster checkout.</p>
                    <button 
                      className="btn btn-primary"
                      onClick={() => alert('Add address feature coming soon!')}
                    >
                      Add Your First Address
                    </button>
                  </div>
                </div>
              )}

              {/* Preferences Tab */}
              {activeTab === 'preferences' && (
                <div>
                  <h4 className="mb-4">Preferences</h4>

                  <div className="row g-4">
                    <div className="col-12">
                      <div className="card bg-light">
                        <div className="card-body">
                          <h6>Communication Preferences</h6>
                          <div className="form-check">
                            <input className="form-check-input" type="checkbox" id="emailMarketing" defaultChecked />
                            <label className="form-check-label" htmlFor="emailMarketing">
                              📧 Receive marketing emails
                            </label>
                          </div>
                          <div className="form-check">
                            <input className="form-check-input" type="checkbox" id="smsNotifications" />
                            <label className="form-check-label" htmlFor="smsNotifications">
                              📱 SMS notifications for orders
                            </label>
                          </div>
                          <div className="form-check">
                            <input className="form-check-input" type="checkbox" id="pushNotifications" defaultChecked />
                            <label className="form-check-label" htmlFor="pushNotifications">
                              🔔 Push notifications
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="col-12">
                      <div className="card bg-light">
                        <div className="card-body">
                          <h6>Display Preferences</h6>
                          <div className="mb-3">
                            <label className="form-label">Language</label>
                            <select className="form-select">
                              <option value="en">English</option>
                              <option value="es">Spanish</option>
                              <option value="fr">French</option>
                            </select>
                          </div>
                          <div className="mb-3">
                            <label className="form-label">Currency</label>
                            <select className="form-select">
                              <option value="USD">USD ($)</option>
                              <option value="EUR">EUR (€)</option>
                              <option value="GBP">GBP (£)</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <button 
                      className="btn btn-primary"
                      onClick={() => alert('Preferences saved! (Demo mode)')}
                    >
                      Save Preferences
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Demo Notice */}
      <div className="alert alert-info mt-4" role="alert">
        <small>
          <strong>Demo Mode:</strong> Profile changes are not persisted in this demo. In a real application, changes would be saved to your account.
        </small>
      </div>
    </div>
  );
}