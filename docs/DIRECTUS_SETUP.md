# Directus Multi-Tenant Setup for Website Factory

This guide helps you configure Directus CMS for managing content across 200+ websites.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/Website-Factory-System/website-factory-docs/main/setup-scripts/setup-directus.sh
chmod +x setup-directus.sh
sudo ./setup-directus.sh
```

### Option 2: Manual Setup

1. **Create directory**:
```bash
sudo mkdir -p /opt/directus
cd /opt/directus
```

2. **Create docker-compose.yml**:
```yaml
version: '3.8'

services:
  directus:
    image: directus/directus:latest
    container_name: directus
    restart: unless-stopped
    ports:
      - "8055:8055"
    environment:
      KEY: 'generate-with-openssl-rand-hex-32'
      SECRET: 'generate-with-openssl-rand-hex-32'
      DB_CLIENT: 'pg'
      DB_HOST: 'directus-db'
      DB_PORT: '5432'
      DB_DATABASE: 'directus'
      DB_USER: 'directus'
      DB_PASSWORD: 'secure-password'
      ADMIN_EMAIL: 'admin@websitefactory.com'
      ADMIN_PASSWORD: 'secure-admin-password'
      CORS_ENABLED: 'true'
      CORS_ORIGIN: '*'
    volumes:
      - ./uploads:/directus/uploads
      - ./extensions:/directus/extensions

  directus-db:
    image: postgres:14-alpine
    container_name: directus-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: 'directus'
      POSTGRES_PASSWORD: 'secure-password'
      POSTGRES_DB: 'directus'
    volumes:
      - ./data:/var/lib/postgresql/data
```

3. **Start Directus**:
```bash
docker compose up -d
```

## 📊 Multi-Tenant Schema Configuration

After Directus is running, configure these collections:

### 1. Sites Collection
```json
{
  "collection": "sites",
  "fields": [
    {
      "field": "id",
      "type": "uuid",
      "meta": { "interface": "input", "hidden": true }
    },
    {
      "field": "domain",
      "type": "string",
      "meta": { "interface": "input", "required": true }
    },
    {
      "field": "brand_name",
      "type": "string",
      "meta": { "interface": "input", "required": true }
    },
    {
      "field": "status",
      "type": "string",
      "meta": { 
        "interface": "select-dropdown",
        "choices": [
          { "text": "Active", "value": "active" },
          { "text": "Draft", "value": "draft" },
          { "text": "Archived", "value": "archived" }
        ]
      }
    }
  ]
}
```

### 2. Pages Collection
```json
{
  "collection": "pages",
  "fields": [
    {
      "field": "id",
      "type": "uuid"
    },
    {
      "field": "site_id",
      "type": "uuid",
      "meta": { 
        "interface": "select-dropdown-m2o",
        "special": ["m2o"],
        "required": true
      }
    },
    {
      "field": "title",
      "type": "string",
      "meta": { "interface": "input", "required": true }
    },
    {
      "field": "slug",
      "type": "string",
      "meta": { "interface": "input", "required": true }
    },
    {
      "field": "content",
      "type": "text",
      "meta": { "interface": "input-rich-text-html" }
    },
    {
      "field": "meta_title",
      "type": "string"
    },
    {
      "field": "meta_description",
      "type": "text"
    },
    {
      "field": "status",
      "type": "string",
      "meta": { 
        "interface": "select-dropdown",
        "choices": [
          { "text": "Published", "value": "published" },
          { "text": "Draft", "value": "draft" }
        ]
      }
    }
  ]
}
```

### 3. Blog Posts Collection
```json
{
  "collection": "blog_posts",
  "fields": [
    {
      "field": "id",
      "type": "uuid"
    },
    {
      "field": "site_id",
      "type": "uuid",
      "meta": { "interface": "select-dropdown-m2o", "required": true }
    },
    {
      "field": "title",
      "type": "string",
      "meta": { "required": true }
    },
    {
      "field": "slug",
      "type": "string",
      "meta": { "required": true }
    },
    {
      "field": "content",
      "type": "text",
      "meta": { "interface": "input-rich-text-html" }
    },
    {
      "field": "featured_image",
      "type": "uuid",
      "meta": { "interface": "file" }
    },
    {
      "field": "author",
      "type": "string"
    },
    {
      "field": "published_at",
      "type": "datetime"
    },
    {
      "field": "status",
      "type": "string"
    }
  ]
}
```

### 4. Media/Assets Collection
```json
{
  "collection": "site_assets",
  "fields": [
    {
      "field": "id",
      "type": "uuid"
    },
    {
      "field": "site_id",
      "type": "uuid",
      "meta": { "required": true }
    },
    {
      "field": "file",
      "type": "uuid",
      "meta": { "interface": "file" }
    },
    {
      "field": "alt_text",
      "type": "string"
    },
    {
      "field": "category",
      "type": "string",
      "meta": { 
        "interface": "select-dropdown",
        "choices": [
          { "text": "Logo", "value": "logo" },
          { "text": "Hero", "value": "hero" },
          { "text": "Gallery", "value": "gallery" },
          { "text": "Blog", "value": "blog" }
        ]
      }
    }
  ]
}
```

## 🔧 API Configuration

### 1. Create API Access Token
1. Go to Settings → Access Tokens
2. Create new token with permissions:
   - Read: All collections
   - Write: All collections
   - Delete: Limited to drafts

### 2. Configure Webhooks
Set up webhooks to trigger deployments:

1. Go to Settings → Webhooks
2. Create webhook:
   - Name: "Deploy on Publish"
   - URL: `http://YOUR-API:8000/webhooks/directus-publish`
   - Triggers: `items.create`, `items.update`
   - Collections: pages, blog_posts

### 3. Environment Variables
Add to your Management Hub API `.env`:
```env
DIRECTUS_URL=http://YOUR-SERVER-IP:8055
DIRECTUS_TOKEN=your-api-token
DIRECTUS_ADMIN_EMAIL=admin@websitefactory.com
```

## 🎨 Roles and Permissions

### 1. Content Editor Role
- Can edit content for assigned sites only
- Cannot delete sites
- Cannot change site settings

### 2. Site Admin Role
- Full access to assigned sites
- Can manage content, settings, media
- Cannot create new sites

### 3. Super Admin Role
- Full access to all sites
- Can create/delete sites
- System configuration access

## 🔌 Integration with Website Factory

### 1. Content Engine Integration
The Content Engine will:
- Create draft content in Directus
- Organize by site_id
- Set proper metadata

### 2. Deployment Integration
When content is published:
- Webhook triggers deployment
- Astro fetches content via API
- Static site is generated

### 3. Multi-tenant Queries
Example API queries for multi-tenant content:

```javascript
// Get all pages for a specific site
GET /items/pages?filter[site_id][_eq]=SITE_ID

// Get published blog posts for a site
GET /items/blog_posts?filter[site_id][_eq]=SITE_ID&filter[status][_eq]=published

// Get site-specific assets
GET /items/site_assets?filter[site_id][_eq]=SITE_ID
```

## 🚨 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs -f directus

# Common issues:
# - Port 8055 already in use
# - Database connection failed
# - Invalid environment variables
```

### Can't access Directus
```bash
# Check if container is running
docker ps | grep directus

# Check firewall
sudo ufw allow 8055/tcp

# Test locally
curl http://localhost:8055
```

### Database issues
```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

## 📚 Next Steps

1. **Configure Collections**: Create the multi-tenant schema
2. **Set up Roles**: Configure permissions for different user types
3. **Create Sample Content**: Add test content for development
4. **Test API Access**: Verify token works from Management Hub
5. **Configure Webhooks**: Set up deployment triggers

## 🔗 Useful Links

- [Directus Docs](https://docs.directus.io)
- [API Reference](https://docs.directus.io/reference/api/)
- [Webhooks Guide](https://docs.directus.io/guides/webhooks/)
- [Multi-tenant Patterns](https://docs.directus.io/guides/headless-cms/multi-tenant/)

---

**Need help?** Check the logs first: `docker compose logs -f directus`