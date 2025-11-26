#!/bin/bash

# Professional E-commerce Project Initialization Script
# This script sets up a professional development environment with all required tools

set -e

echo "🚀 Initializing Professional E-commerce Platform..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v uv &> /dev/null; then
        echo "❌ uv not found. Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    echo "✅ All requirements satisfied"
}

# Create project structure
create_structure() {
    echo "📁 Creating project structure..."
    
    # Main directories
    mkdir -p backend/{apps/{accounts,products,orders,reviews,core},config/settings,static,media,locale,templates,fixtures}
    mkdir -p frontend/{src/{app,components/{ui,forms,layouts,features,common},lib,hooks,stores,styles,types},public/{images,icons},__tests__,e2e,docs}
    mkdir -p docs scripts .github/{workflows,ISSUE_TEMPLATE}
    
    # Backend app subdirectories
    for app in accounts products orders reviews; do
        mkdir -p backend/apps/$app/tests
        touch backend/apps/$app/{__init__.py,models.py,views.py,serializers.py,urls.py,tests/__init__.py}
    done
    
    # Core app additional files
    touch backend/apps/core/{__init__.py,permissions.py,pagination.py,exceptions.py,utils.py}
    
    # Config files
    touch backend/config/{__init__.py,urls.py,wsgi.py,asgi.py}
    touch backend/config/settings/{__init__.py,base.py,development.py,production.py,testing.py}
    
    echo "✅ Project structure created"
}

# Initialize backend with uv
init_backend() {
    echo "🐍 Initializing Django backend with uv..."
    
    cd backend
    
    # Initialize uv project
    uv init --name "ecommerce-backend" --python "3.11"
    
    # Add production dependencies
    uv add django djangorestframework psycopg2-binary redis celery pillow stripe python-decouple django-cors-headers drf-spectacular
    
    # Add development dependencies
    uv add --dev ruff mypy pytest pytest-django pytest-cov pre-commit black commitizen django-debug-toolbar factory-boy
    
    # Create configuration files
    cat > pyproject.toml << EOF
[project]
name = "ecommerce-backend"
version = "1.0.0"
description = "Professional E-commerce Backend API"
requires-python = ">=3.11"
dependencies = [
    "django>=4.2.0",
    "djangorestframework>=3.14.0",
    "psycopg2-binary>=2.9.0",
    "redis>=4.5.0",
    "celery>=5.3.0",
    "pillow>=10.0.0",
    "stripe>=5.5.0",
    "python-decouple>=3.8",
    "django-cors-headers>=4.2.0",
    "drf-spectacular>=0.26.0",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pytest>=7.4.0",
    "pytest-django>=4.5.0",
    "pytest-cov>=4.1.0",
    "pre-commit>=3.3.0",
    "black>=23.7.0",
    "commitizen>=3.6.0",
    "django-debug-toolbar>=4.2.0",
    "factory-boy>=3.3.0",
]

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "PIE", "T20"]
ignore = ["E501", "N806", "N803"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"**/migrations/*" = ["E501", "F401"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
exclude = ["migrations/"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.testing"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
testpaths = ["apps/"]
addopts = "--cov=apps --cov-report=html --cov-report=term-missing --reuse-db"

[tool.commitizen]
name = "cz_conventional_commits"
version = "1.0.0"
tag_format = "v\$version"
EOF

    # Create ruff.toml for additional configuration
    cat > ruff.toml << EOF
# Ruff configuration
target-version = "py311"
line-length = 88
indent-width = 4

[lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "PIE", "T20"]
ignore = ["E501", "N806", "N803"]

[lint.per-file-ignores]
"__init__.py" = ["F401"]
"**/migrations/*" = ["E501", "F401"]

[format]
quote-style = "double"
indent-style = "space"
EOF

    cd ..
    echo "✅ Backend initialized with uv and professional tools"
}

# Initialize frontend
init_frontend() {
    echo "⚛️ Initializing Next.js frontend..."
    
    cd frontend
    
    # Create Next.js app with TypeScript
    npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
    
    # Install additional dependencies
    npm install @radix-ui/react-icons @radix-ui/react-slot @radix-ui/react-dialog lucide-react class-variance-authority clsx tailwind-merge
    npm install -D @types/jest jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom prettier @playwright/test husky lint-staged
    
    # Initialize shadcn/ui
    npx shadcn-ui@latest init -d
    
    cd ..
    echo "✅ Frontend initialized with Next.js and TypeScript"
}

# Setup Docker configuration
setup_docker() {
    echo "🐳 Setting up Docker configuration..."
    
    # Docker Compose for development
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ecommerce_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: python manage.py runserver 0.0.0.0:8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
EOF

    # Backend Dockerfile
    cat > backend/Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

    # Frontend Dockerfile
    cat > frontend/Dockerfile << EOF
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOF

    echo "✅ Docker configuration created"
}

# Setup Git configuration
setup_git() {
    echo "📝 Setting up Git configuration..."
    
    # .gitignore
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
.uv/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
htmlcov/
.coverage
.pytest_cache/

# Build outputs
dist/
build/
.next/
out/

# Docker
.dockerignore

# Media files
media/
staticfiles/
EOF

    # Pre-commit configuration
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        files: ^backend/
        additional_dependencies: [django-stubs, djangorestframework-stubs]
EOF

    # GitHub workflows
    mkdir -p .github/workflows
    
    cat > .github/workflows/ci.yml << EOF
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: "latest"
    
    - name: Set up Python
      run: uv python install 3.11
    
    - name: Install dependencies
      run: |
        cd backend
        uv sync
    
    - name: Run linting
      run: |
        cd backend
        uv run ruff check .
        uv run mypy .
    
    - name: Run tests
      run: |
        cd backend
        uv run pytest --cov=apps --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linting
      run: |
        cd frontend
        npm run lint
        npm run type-check
    
    - name: Run tests
      run: |
        cd frontend
        npm run test
EOF

    echo "✅ Git configuration and workflows created"
}

# Create documentation
create_docs() {
    echo "📚 Creating documentation..."
    
    cat > README.md << EOF
# Professional E-commerce Platform

A modern, scalable e-commerce platform built with Django REST Framework and Next.js.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Development Setup

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd ecommerce-platform
\`\`\`

2. Run the initialization script:
\`\`\`bash
chmod +x init_project.sh
./init_project.sh
\`\`\`

3. Start development servers:
\`\`\`bash
docker-compose up -d
\`\`\`

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

See \`agent.md\` for detailed project architecture and implementation plan.

## 🔧 Development

### Backend Development
\`\`\`bash
cd backend
uv run python manage.py runserver
\`\`\`

### Frontend Development
\`\`\`bash
cd frontend
npm run dev
\`\`\`

### Running Tests
\`\`\`bash
# Backend tests
cd backend && uv run pytest

# Frontend tests
cd frontend && npm run test
\`\`\`

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🤝 Contributing

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
EOF

    # Create basic documentation files
    cat > docs/CONTRIBUTING.md << EOF
# Contributing Guidelines

## Code Style

- Use ruff for Python code formatting
- Use ESLint + Prettier for TypeScript/JavaScript
- Follow conventional commits for commit messages

## Testing

- Write tests for all new features
- Maintain >80% code coverage
- Run tests locally before submitting PRs

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request with clear description
EOF

    echo "✅ Documentation created"
}

# Main execution
main() {
    echo "🎯 Starting professional e-commerce project setup..."
    
    check_requirements
    create_structure
    init_backend
    init_frontend
    setup_docker
    setup_git
    create_docs
    
    echo ""
    echo "🎉 Professional e-commerce project initialized successfully!"
    echo ""
    echo "Next steps:"
    echo "1. cd into your project directory"
    echo "2. Run 'git init' and set up your repository"
    echo "3. Run 'docker-compose up -d' to start development servers"
    echo "4. Visit http://localhost:3000 for frontend and http://localhost:8000 for backend API"
    echo ""
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"