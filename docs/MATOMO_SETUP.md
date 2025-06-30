# Matomo Analytics Setup Guide for Website Factory

This guide walks you through installing Matomo Analytics on your Vultr server using Docker. Matomo will track visitor analytics for all 200+ websites managed by the Website Factory system.

## Prerequisites

- Vultr server with Ubuntu 22.04
- Docker and Docker Compose installed
- Root or sudo access
- CloudPanel already installed (using port 8080)
- Directus already installed (using port 8055)

## Step 1: Create Matomo Directory

```bash
# SSH into your Vultr server
ssh root@YOUR_SERVER_IP

# Create directory for Matomo
mkdir -p /opt/matomo
cd /opt/matomo
```

## Step 2: Create Docker Compose Configuration

Create a `docker-compose.yml` file:

```bash
nano docker-compose.yml
```

Add the following configuration:

```yaml
version: '3.8'

services:
  matomo:
    image: matomo:latest
    container_name: matomo
    restart: unless-stopped
    ports:
      - "8056:80"  # Using port 8056 to avoid conflicts
    environment:
      MATOMO_DATABASE_HOST: matomo-db
      MATOMO_DATABASE_ADAPTER: mysql
      MATOMO_DATABASE_TABLES_PREFIX: matomo_
      MATOMO_DATABASE_USERNAME: matomo
      MATOMO_DATABASE_PASSWORD: 'SecurePassword123!'  # CHANGE THIS!
      MATOMO_DATABASE_DBNAME: matomo
      PHP_MEMORY_LIMIT: 256M
    volumes:
      - ./config:/var/www/html/config
      - ./logs:/var/www/html/logs
      - ./plugins:/var/www/html/plugins
    depends_on:
      - matomo-db

  matomo-db:
    image: mariadb:10.11
    container_name: matomo-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: 'RootPassword123!'  # CHANGE THIS!
      MYSQL_DATABASE: matomo
      MYSQL_USER: matomo
      MYSQL_PASSWORD: 'SecurePassword123!'  # CHANGE THIS!
    volumes:
      - ./db-data:/var/lib/mysql
    command: --max-allowed-packet=64MB
```

## Step 3: Generate Secure Passwords

```bash
# Generate secure passwords
echo "DB Password: $(openssl rand -base64 32)"
echo "Root Password: $(openssl rand -base64 32)"

# Update the docker-compose.yml with these passwords
```

## Step 4: Start Matomo

```bash
# Start the containers
docker compose up -d

# Check if containers are running
docker compose ps

# View logs to ensure everything started correctly
docker compose logs -f
# Press Ctrl+C to exit logs
```

## Step 5: Configure Firewall

```bash
# Open port 8056 for Matomo
ufw allow 8056/tcp
ufw reload
```

## Step 6: Complete Web Setup

1. Open your browser and navigate to: `http://YOUR_SERVER_IP:8056`
2. You'll see the Matomo installation wizard

### Installation Steps:

1. **Welcome Screen**: Click "Next"

2. **System Check**: 
   - Ensure all checks pass
   - Click "Next"

3. **Database Setup**:
   - Database Server: `matomo-db`
   - Username: `matomo`
   - Password: (the password you set in docker-compose.yml)
   - Database Name: `matomo`
   - Table Prefix: `matomo_` (leave as default)
   - Click "Next"

4. **Create Tables**: Click "Next" to create database tables

5. **Super User**:
   - Username: `admin`
   - Password: (create a strong password - save this!)
   - Email: `admin@yourdomain.com`
   - Click "Next"

6. **First Website**:
   - Website name: `Test Site` (you'll add real sites programmatically)
   - Website URL: `https://test.example.com`
   - Website time zone: (your timezone)
   - Click "Next"

7. **Tracking Code**: Skip this (we'll handle it programmatically)

8. **Finish**: Complete the installation

## Step 7: Configure API Access

1. Log into Matomo with your admin credentials
2. Go to **Settings** (gear icon) → **Personal** → **Security**
3. Scroll down to **Auth Tokens**
4. Click **Create new token**
5. Description: `Website Factory API`
6. Click **Create new token**
7. **IMPORTANT**: Copy the token immediately (you won't see it again!)

## Step 8: Add Matomo Credentials to Supabase

```sql
-- In your Supabase SQL editor
INSERT INTO infrastructure_credentials (
  service,
  url,
  username,
  password,
  api_token,
  metadata
) VALUES (
  'matomo',
  'http://YOUR_SERVER_IP:8056',
  'admin',
  'your-admin-password',
  'your-api-token-here',
  '{"notes": "Main Matomo instance for Website Factory"}'::jsonb
);
```

## Step 9: Test API Connection

```bash
# Test the API connection
curl -X POST "http://YOUR_SERVER_IP:8056/index.php" \
  -d "module=API" \
  -d "method=SitesManager.getAllSites" \
  -d "format=JSON" \
  -d "token_auth=YOUR_API_TOKEN"

# Should return: []  (empty array since no sites yet)
```

## Step 10: Configure for Production (Optional but Recommended)

### Enable HTTPS with Nginx Reverse Proxy

```bash
# Install Nginx if not already installed
apt install nginx -y

# Create Nginx configuration
nano /etc/nginx/sites-available/matomo
```

Add configuration:

```nginx
server {
    listen 80;
    server_name analytics.yourdomain.com;

    location / {
        proxy_pass http://localhost:8056;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
ln -s /etc/nginx/sites-available/matomo /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Install SSL Certificate

```bash
# Install Certbot
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

# Get SSL certificate
certbot --nginx -d analytics.yourdomain.com
```

## Maintenance Commands

```bash
# Stop Matomo
cd /opt/matomo
docker compose down

# Start Matomo
docker compose up -d

# View logs
docker compose logs -f matomo

# Update Matomo
docker compose pull
docker compose up -d

# Backup database
docker exec matomo-db mysqldump -u root -p matomo > matomo-backup-$(date +%Y%m%d).sql

# Access Matomo container
docker exec -it matomo bash
```

## Troubleshooting

### Issue: Cannot connect to database
```bash
# Check if database container is running
docker compose ps

# Check database logs
docker compose logs matomo-db
```

### Issue: Matomo is slow
```bash
# Increase PHP memory limit in docker-compose.yml
PHP_MEMORY_LIMIT: 512M

# Restart containers
docker compose down
docker compose up -d
```

### Issue: Disk space filling up
```bash
# Check disk usage
df -h

# Clean up old logs
docker exec matomo bash -c "find /var/www/html/logs -name '*.log' -mtime +30 -delete"
```

## Integration with Website Factory

The Hosting Automator will automatically:
1. Create new sites in Matomo when provisioning hosting
2. Retrieve the site ID for tracking code insertion
3. Handle failures gracefully (Matomo being down won't block site creation)

## Security Notes

1. **Change all default passwords** in the docker-compose.yml
2. **Restrict API token permissions** if possible
3. **Use HTTPS** in production
4. **Regular backups** of the database
5. **Keep Matomo updated** for security patches

## Next Steps

1. ✅ Matomo is now installed and ready
2. ✅ API token is stored in Supabase
3. ✅ Hosting Automator can now create tracking sites
4. 🔄 Deploy and test the Hosting Automator module