#!/bin/bash

# Directus Quick Setup Script
# This script sets up Directus CMS for Website Factory

set -e  # Exit on error

echo "🚀 Starting Directus Setup for Website Factory"
echo "============================================"

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then 
   echo "This script must be run as root or with sudo" 
   exit 1
fi

# 1. Create directory structure
echo "📁 Creating directory structure..."
mkdir -p /opt/directus/{uploads,extensions,data}
cd /opt/directus

# 2. Generate secure keys
echo "🔐 Generating secure keys..."
KEY=$(openssl rand -hex 32)
SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
ADMIN_PASSWORD=$(openssl rand -hex 12)

echo "Generated credentials:"
echo "  Directus Admin Email: admin@websitefactory.com"
echo "  Directus Admin Password: $ADMIN_PASSWORD"
echo "  (Save these credentials!)"
echo ""

# 3. Create docker-compose.yml
echo "📝 Creating docker-compose.yml..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  directus:
    image: directus/directus:latest
    container_name: directus
    restart: unless-stopped
    ports:
      - "8055:8055"
    environment:
      KEY: '$KEY'
      SECRET: '$SECRET'
      DB_CLIENT: 'pg'
      DB_HOST: 'directus-db'
      DB_PORT: '5432'
      DB_DATABASE: 'directus'
      DB_USER: 'directus'
      DB_PASSWORD: '$DB_PASSWORD'
      ADMIN_EMAIL: 'admin@websitefactory.com'
      ADMIN_PASSWORD: '$ADMIN_PASSWORD'
      # Multi-tenant configuration
      CORS_ENABLED: 'true'
      CORS_ORIGIN: '*'
      PUBLIC_URL: 'http://localhost:8055'
      # Webhook for deployment triggers
      FLOWS_EXEC_ALLOWED_MODULES: 'axios'
    volumes:
      - ./uploads:/directus/uploads
      - ./extensions:/directus/extensions
    depends_on:
      - directus-db

  directus-db:
    image: postgres:14-alpine
    container_name: directus-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: 'directus'
      POSTGRES_PASSWORD: '$DB_PASSWORD'
      POSTGRES_DB: 'directus'
    volumes:
      - ./data:/var/lib/postgresql/data
EOF

# 4. Create .env file for reference
echo "📝 Creating .env file..."
cat > .env << EOF
# Directus Configuration
DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_EMAIL=admin@websitefactory.com
DIRECTUS_ADMIN_PASSWORD=$ADMIN_PASSWORD
DIRECTUS_KEY=$KEY
DIRECTUS_SECRET=$SECRET
DIRECTUS_DB_PASSWORD=$DB_PASSWORD
EOF

# 5. Start Directus
echo "🚀 Starting Directus containers..."
docker compose up -d

# 6. Wait for Directus to be ready
echo "⏳ Waiting for Directus to start (this may take a minute)..."
sleep 30

# Check if Directus is running
if docker ps | grep -q directus; then
    echo "✅ Directus is running!"
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo "Directus URL: http://YOUR-SERVER-IP:8055"
    echo "Admin Email: admin@websitefactory.com"
    echo "Admin Password: $ADMIN_PASSWORD"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Open http://YOUR-SERVER-IP:8055 in your browser"
    echo "2. Log in with the admin credentials above"
    echo "3. Configure collections for multi-tenant websites"
    echo ""
    echo "💾 Credentials saved in: /opt/directus/.env"
else
    echo "❌ Error: Directus failed to start"
    echo "Check logs with: docker compose logs -f"
    exit 1
fi