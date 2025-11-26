import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="container mt-4">
      {/* Navigation Breadcrumb */}
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link href="/" className="text-decoration-none">Home</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">About</li>
        </ol>
      </nav>

      {/* Hero Section */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="bg-primary text-white p-5 rounded" style={{
            background: 'linear-gradient(135deg, #007bff 0%, #6f42c1 100%) !important'
          }}>
            <h1 className="display-4 fw-bold mb-3">About Our Platform</h1>
            <p className="lead">
              A professional full-stack e-commerce solution built with modern technologies
            </p>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="row mb-5">
        <div className="col-12">
          <h2 className="mb-4">Technology Stack</h2>
          <div className="row g-4">
            {/* Backend */}
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header bg-primary text-white">
                  <h5 className="mb-0">🐍 Backend Technologies</h5>
                </div>
                <div className="card-body">
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <strong>Django 5.2.6</strong> - Web framework
                    </li>
                    <li className="mb-2">
                      <strong>Django REST Framework</strong> - API development
                    </li>
                    <li className="mb-2">
                      <strong>SQLite/PostgreSQL</strong> - Database
                    </li>
                    <li className="mb-2">
                      <strong>uv & Ruff</strong> - Package management & linting
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Frontend */}
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header bg-success text-white">
                  <h5 className="mb-0">⚛️ Frontend Technologies</h5>
                </div>
                <div className="card-body">
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <strong>Next.js 15.5.4</strong> - React framework
                    </li>
                    <li className="mb-2">
                      <strong>TypeScript</strong> - Type-safe JavaScript
                    </li>
                    <li className="mb-2">
                      <strong>Bootstrap 5</strong> - CSS framework
                    </li>
                    <li className="mb-2">
                      <strong>React 19.1.1</strong> - UI library
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API Documentation */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h3 className="card-title">API Documentation & Testing</h3>
              <p className="card-text">
                The platform provides comprehensive API documentation through interactive Swagger UI.
              </p>
              <div className="d-flex gap-3">
                <a 
                  href="http://localhost:8000/api/docs/" 
                  className="btn btn-primary"
                  target="_blank"
                >
                  📚 View API Documentation
                </a>
                <a 
                  href="http://localhost:8000/admin/" 
                  className="btn btn-outline-secondary"
                  target="_blank"
                >
                  ⚙️ Admin Interface
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}