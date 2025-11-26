# Professional E-commerce Platform

A modern, scalable e-commerce platform built with Django REST Framework and Next.js.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (local installation)
- Redis (local installation)
- Git

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ecommerce-platform
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Install Python dependencies:
```bash
cd backend
uv sync
```

4. Install Node.js dependencies:
```bash
cd ../frontend
npm install
```

5. Set up the database:
```bash
cd ../backend
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

6. Start development servers:
```bash
# Backend (in one terminal)
cd backend
uv run python manage.py runserver

# Frontend (in another terminal)
cd frontend
npm run dev
```

### Tech Stack

**Backend:**
- Django 4.2+ with Django REST Framework
- PostgreSQL database
- Redis for caching and sessions
- Celery for background tasks

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS + shadcn/ui
- React Query for state management

**Development Tools:**
- uv for Python package management
- ruff for linting and formatting
- mypy for type checking
- pytest for testing
- pre-commit hooks for code quality

## 📁 Project Structure

See `agent.md` for detailed project architecture and implementation plan.

## 🔧 Development

### Backend Development
```bash
cd backend
uv run python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend && uv run pytest

# Frontend tests
cd frontend && npm run test
```

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🤝 Contributing

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
