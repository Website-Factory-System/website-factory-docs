# Complete Infrastructure Setup Guide for Website Factory

This guide covers EVERY piece of infrastructure needed to run the complete Website Factory system for 200+ websites.

## 📊 Overview of Required Infrastructure

1. **Vultr Cloud Server** - Main hosting server
2. **CloudPanel** - Server management panel
3. **Docker & Docker Compose** - Container orchestration
4. **Supabase Account** - Central database (already have)
5. **Cloudflare Accounts** (~25) - DNS management
6. **Namecheap API** - Domain nameserver control
7. **Directus CMS** - Content management
8. **Matomo Analytics** - Traffic tracking
9. **Google Accounts** (~5) - Search Console access
10. **AI API Keys** - Content generation
11. **Domain Names** - For testing

## 🖥️ Step 1: Vultr Server Setup

### 1.1 Create Vultr Account
1. Go to [vultr.com](https://vultr.com)
2. Sign up for an account
3. Add payment method

### 1.2 Deploy Server
1. Click "Deploy New Server"
2. Choose:
   - **Type**: Cloud Compute - Shared CPU
   - **Location**: Choose nearest to you
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: At least 4GB RAM, 2 CPU (for 200+ sites, recommend 8GB/4CPU)
   - **Label**: "website-factory-main"
3. Deploy and wait for server to be ready
4. Note your server IP address

### 1.3 Initial Server Configuration
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git nano ufw fail2ban

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8080/tcp  # CloudPanel
ufw --force enable

# Set up fail2ban for security
systemctl enable fail2ban
systemctl start fail2ban
```

## 🎛️ Step 2: CloudPanel Installation

CloudPanel provides GUI management for websites, SSL certificates, and databases.

```bash
# Download and run CloudPanel installer
curl -sS https://installer.cloudpanel.io/ce/v2/install.sh | sudo bash

# The installer will:
# - Install required packages
# - Set up MariaDB/MySQL
# - Configure Nginx
# - Install PHP versions
# - Set up the CloudPanel interface

# After installation, access CloudPanel at:
# https://YOUR_SERVER_IP:8080

# First login credentials will be shown in terminal
```

### 2.1 CloudPanel Initial Setup
1. Log into CloudPanel
2. Change default password
3. Set up admin email
4. Configure timezone

## 🐳 Step 3: Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Add current user to docker group (optional)
usermod -aG docker $USER
```

## 📊 Step 4: Directus CMS Setup

### 4.1 Create Directus Directory
```bash
mkdir -p /opt/directus
cd /opt/directus
```

### 4.2 Create docker-compose.yml
```yaml
# /opt/directus/docker-compose.yml
version: '3.8'

services:
  directus:
    image: directus/directus:latest
    container_name: directus
    restart: unless-stopped
    ports:
      - "8055:8055"
    environment:
      KEY: 'your-random-key-here'  # Generate with: openssl rand -hex 32
      SECRET: 'your-random-secret-here'  # Generate with: openssl rand -hex 32
      DB_CLIENT: 'pg'
      DB_HOST: 'directus-db'
      DB_PORT: '5432'
      DB_DATABASE: 'directus'
      DB_USER: 'directus'
      DB_PASSWORD: 'your-secure-password'
      ADMIN_EMAIL: 'admin@websitefactory.com'
      ADMIN_PASSWORD: 'your-admin-password'
    volumes:
      - ./uploads:/directus/uploads
      - ./extensions:/directus/extensions

  directus-db:
    image: postgres:14-alpine
    container_name: directus-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: 'directus'
      POSTGRES_PASSWORD: 'your-secure-password'
      POSTGRES_DB: 'directus'
    volumes:
      - ./data:/var/lib/postgresql/data
```

### 4.3 Start Directus
```bash
# Generate secure keys
echo "KEY: $(openssl rand -hex 32)"
echo "SECRET: $(openssl rand -hex 32)"

# Update docker-compose.yml with generated keys

# Start Directus
docker compose up -d

# Check logs
docker compose logs -f

# Access Directus at http://YOUR_SERVER_IP:8055
```

## 📈 Step 5: Matomo Analytics Setup

### 5.1 Create Matomo Directory
```bash
mkdir -p /opt/matomo
cd /opt/matomo
```

### 5.2 Create docker-compose.yml
```yaml
# /opt/matomo/docker-compose.yml
version: '3.8'

services:
  matomo:
    image: matomo:latest
    container_name: matomo
    restart: unless-stopped
    ports:
      - "8056:80"
    environment:
      MATOMO_DATABASE_HOST: matomo-db
      MATOMO_DATABASE_ADAPTER: mysql
      MATOMO_DATABASE_TABLES_PREFIX: matomo_
      MATOMO_DATABASE_USERNAME: matomo
      MATOMO_DATABASE_PASSWORD: 'your-secure-password'
      MATOMO_DATABASE_DBNAME: matomo
    volumes:
      - ./config:/var/www/html/config
      - ./logs:/var/www/html/logs

  matomo-db:
    image: mariadb:10.6
    container_name: matomo-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: 'root-password'
      MYSQL_DATABASE: matomo
      MYSQL_USER: matomo
      MYSQL_PASSWORD: 'your-secure-password'
    volumes:
      - ./db:/var/lib/mysql
```

### 5.3 Start Matomo
```bash
# Start Matomo
docker compose up -d

# Access Matomo at http://YOUR_SERVER_IP:8056
# Complete the web-based setup wizard
```

## ☁️ Step 6: Cloudflare Accounts Setup

You need ~25 Cloudflare accounts for DNS distribution.

### 6.1 Create Cloudflare Accounts
1. Use different email addresses (can use Gmail + trick: yourname+cf1@gmail.com)
2. For each account:
   - Sign up at [cloudflare.com](https://cloudflare.com)
   - Verify email
   - Skip adding a domain initially

### 6.2 Generate API Tokens
For each Cloudflare account:
1. Go to My Profile → API Tokens
2. Click "Create Token"
3. Use "Custom token" template with permissions:
   - Zone:DNS:Edit
   - Zone:Zone:Read
   - Account:Cloudflare Pages:Edit (optional)
4. Save the token securely

### 6.3 Add to Database
```sql
-- In Supabase SQL Editor
-- Add each Cloudflare account
INSERT INTO cloudflare_accounts (email, account_nickname, api_token) VALUES
('yourname+cf1@gmail.com', 'CF_Batch_1', 'your-api-token-here'),
('yourname+cf2@gmail.com', 'CF_Batch_2', 'your-api-token-here'),
-- ... repeat for all 25 accounts
```

## 🌐 Step 7: Namecheap API Setup

### 7.1 Enable API Access
1. Log into Namecheap account
2. Go to Profile → Tools → API Access
3. Enable API Access (may require whitelisting your server IP)

### 7.2 Get API Credentials
- Note your API Key
- Set up API User (usually same as username)
- Whitelist your Vultr server IP

### 7.3 Store in Environment
```bash
# Add to your .env file
NAMECHEAP_API_USER=your-username
NAMECHEAP_API_KEY=your-api-key
NAMECHEAP_CLIENT_IP=YOUR_SERVER_IP
```

## 🔍 Step 8: Google Search Console Setup

### 8.1 Create Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: "Website Factory"
3. Enable APIs:
   - Search Console API
   - Site Verification API

### 8.2 Create Service Account
1. Go to IAM & Admin → Service Accounts
2. Create service account
3. Download JSON key file
4. Store securely in Supabase

### 8.3 Set up OAuth for Search Console
1. Go to APIs & Services → Credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URIs
4. Download credentials

## 🤖 Step 9: AI API Keys

### 9.1 OpenAI
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Go to API Keys
3. Create new secret key
4. Add billing/credits

### 9.2 Google Gemini
1. Go to [makersuite.google.com](https://makersuite.google.com)
2. Get API key
3. Enable billing if needed

### 9.3 Other APIs (Optional)
- Perplexity API for research
- Brave Search API for data
- Anthropic Claude API

## 🔐 Step 10: Environment Configuration

### 10.1 Create Master .env File
```bash
# /opt/website-factory/.env

# Database
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# APIs
NAMECHEAP_API_USER=your-username
NAMECHEAP_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key

# Server
SERVER_IP=YOUR_VULTR_IP
CLOUDPANEL_URL=https://YOUR_IP:8080
DIRECTUS_URL=http://YOUR_IP:8055
MATOMO_URL=http://YOUR_IP:8056

# Security
JWT_SECRET_KEY=your-generated-jwt-secret
ADMIN_PASSWORD=your-secure-admin-password
```

## 📦 Step 11: Install Website Factory Modules

```bash
# Create main directory
mkdir -p /opt/website-factory
cd /opt/website-factory

# Clone repositories (when ready)
git clone https://github.com/your-org/management-hub-api.git
git clone https://github.com/your-org/management-hub-ui.git
git clone https://github.com/your-org/dns-automator.git
# ... etc

# Install Python dependencies
cd management-hub-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🧪 Step 12: Testing Domains

For testing, you'll need:
1. A few test domains (buy cheap .com domains)
2. Point them to Namecheap nameservers
3. Have Namecheap API access for them

## 🚀 Step 13: Final Deployment

### 13.1 Set up systemd services
```bash
# Create service file for Management Hub API
cat > /etc/systemd/system/management-hub-api.service << EOF
[Unit]
Description=Management Hub API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/website-factory/management-hub-api
ExecStart=/opt/website-factory/management-hub-api/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable management-hub-api
systemctl start management-hub-api
```

### 13.2 Set up Nginx reverse proxy
```nginx
# /etc/nginx/sites-available/website-factory
server {
    listen 80;
    server_name hub.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;  # UI
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;  # API
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## ✅ Verification Checklist

- [ ] Vultr server accessible via SSH
- [ ] CloudPanel accessible and working
- [ ] Docker and Docker Compose installed
- [ ] Directus running and accessible
- [ ] Matomo running and accessible
- [ ] 25 Cloudflare accounts created with API tokens
- [ ] Cloudflare accounts added to Supabase
- [ ] Namecheap API enabled and tested
- [ ] Google Cloud project with APIs enabled
- [ ] AI API keys obtained and funded
- [ ] All credentials stored securely
- [ ] Test domains available

## 🎯 Total Setup Time Estimate

- Server setup: 1-2 hours
- Service installation: 2-3 hours
- Account creation (25 Cloudflare): 3-4 hours
- API setup and testing: 2-3 hours
- **Total: 8-12 hours**

This is the COMPLETE infrastructure needed for the Website Factory system!