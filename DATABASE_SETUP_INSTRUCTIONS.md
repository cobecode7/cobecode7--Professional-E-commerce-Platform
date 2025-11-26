# 🐘 PostgreSQL Database Setup Instructions

## 🎯 Quick Setup (For Your Debian System with PostgreSQL 17)

### 1. Create Database and User
```bash
# Method 1: Using sudo (if postgres user has sudo access)
sudo -u postgres createdb ecommerce_dev
sudo -u postgres psql -c "CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_dev123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ecommerce_dev TO ecommerce_user;"
sudo -u postgres psql -c "ALTER USER ecommerce_user CREATEDB;"

# Method 2: Direct psql connection (if you know postgres password)
psql -h localhost -U postgres -c "CREATE DATABASE ecommerce_dev;"
psql -h localhost -U postgres -c "CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_dev123';"
psql -h localhost -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ecommerce_dev TO ecommerce_user;"
psql -h localhost -U postgres -c "ALTER USER ecommerce_user CREATEDB;"
```

### 2. Test Database Connection
```bash
# Test the connection with our new user
psql -h localhost -U ecommerce_user -d ecommerce_dev -c "SELECT version();"
```

### 3. Run Django Migrations
```bash
cd /home/saleh/projects/copilot2/1/backend
source .venv/bin/activate

# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Test the server
python manage.py runserver
```

## 🔧 Configuration Details

### Current Settings:
- **Database:** ecommerce_dev
- **User:** ecommerce_user  
- **Password:** ecommerce_dev123
- **Host:** localhost
- **Port:** 5432

### Environment Variables (Already Configured):
```bash
DATABASE_URL=postgresql://ecommerce_user:ecommerce_dev123@localhost:5432/ecommerce_dev
DB_NAME=ecommerce_dev
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_dev123
DB_HOST=localhost
DB_PORT=5432
```

## 🚨 Production Setup (When Deploying)

### 1. Strong Credentials:
```bash
# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Generated password: $DB_PASSWORD"
```

### 2. SSL Configuration:
```bash
# Enable SSL in PostgreSQL (postgresql.conf)
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

### 3. Production Environment Variables:
```bash
DATABASE_URL=postgresql://prod_user:${SECURE_PASSWORD}@hostname:5432/ecommerce_prod
DB_NAME=ecommerce_prod
DB_USER=prod_user
DB_PASSWORD=${SECURE_PASSWORD}
DB_HOST=your-db-hostname
DB_PORT=5432
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. Permission Denied:
```bash
# Fix: Ensure PostgreSQL service is running
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. Connection Refused:
```bash
# Fix: Check if PostgreSQL is listening
sudo netstat -plunt | grep 5432
```

#### 3. Authentication Failed:
```bash
# Fix: Update pg_hba.conf for local development
sudo nano /etc/postgresql/17/main/pg_hba.conf
# Change: local all all peer
# To:     local all all md5
sudo systemctl restart postgresql
```

#### 4. Database Does Not Exist:
```bash
# Fix: Create database manually
sudo -u postgres createdb ecommerce_dev
```

## ✅ Verification Commands

### Check PostgreSQL Version:
```bash
psql --version
```

### Check Service Status:
```bash
sudo systemctl status postgresql
```

### Test Connection:
```bash
pg_isready -h localhost -p 5432
```

### List Databases:
```bash
sudo -u postgres psql -l
```

---

**🎉 Once setup is complete, your project will be fully migrated to PostgreSQL 17!**