# Credentials Management System

The Website Factory now includes a comprehensive credentials management system accessible through the Settings page in the UI.

## Overview

All API keys, credentials, and server configurations can now be managed through the web interface instead of being hardcoded. This provides:
- Centralized credential storage in Supabase
- Easy updates without code changes
- Support for multiple servers and accounts
- Bulk import capabilities for Cloudflare accounts

## Features

### 1. Server Management
- Add multiple hosting servers (Vultr, DigitalOcean, AWS, etc.)
- Store IP addresses and CloudPanel URLs
- Mark servers as active/inactive
- Support for scaling across multiple servers

### 2. Domain Registrar Credentials
- **Namecheap**: API user, API key, and client IP
- **Spaceship**: API key support
- Easy switching between registrars

### 3. Infrastructure Services
- **Matomo Analytics**: URL, username, password, API token
- **CloudPanel**: Admin credentials
- **Directus CMS**: API access credentials
- Extensible for additional services

### 4. Cloudflare Accounts
- Bulk import via CSV file
- CSV format: `email,account_nickname,api_token`
- Automatic duplicate detection
- Import status reporting

## Usage

### Adding Credentials via UI

1. Navigate to `/settings` in the Management Hub
2. Select the appropriate tab:
   - **Servers**: For hosting server configuration
   - **Domain Registrars**: For Namecheap/Spaceship API keys
   - **Infrastructure**: For Matomo, CloudPanel, Directus
   - **Cloudflare Accounts**: For bulk CSV import

3. Fill in the required fields and click save

### Bulk Import Cloudflare Accounts

1. Prepare a CSV file with columns:
   ```csv
   email,account_nickname,api_token
   user+cf1@gmail.com,CF_Batch_1,token123...
   user+cf2@gmail.com,CF_Batch_2,token456...
   ```

2. Go to Settings → Cloudflare Accounts tab
3. Click "Choose CSV File" and select your file
4. The system will import all accounts and report results

## Database Schema

### New Tables Added:

1. **servers**
   - `id`, `name`, `ip_address`, `type`, `cloudpanel_url`, `is_active`

2. **registrar_credentials**
   - `id`, `provider`, `api_user`, `api_key`, `client_ip`, `is_active`

3. **infrastructure_credentials**
   - `id`, `service`, `url`, `username`, `password`, `api_token`, `is_active`

4. **cloudflare_accounts** (existing, enhanced)
   - Supports bulk import with duplicate detection

## Security Considerations

- All credentials are stored in Supabase with Row Level Security (RLS)
- Only authenticated users can access credentials
- API endpoints are protected with JWT authentication
- TODO: Implement encryption at rest for sensitive fields

## API Endpoints

All credential management endpoints are available under `/api/v1/credentials/`:

- `GET/POST /servers` - Manage servers
- `GET/POST /registrars` - Manage registrar credentials
- `GET/POST /infrastructure` - Manage infrastructure credentials
- `POST /cloudflare/bulk-import` - Bulk import Cloudflare accounts

## Next Steps

1. Add your credentials through the Settings page
2. Test credentials with the automation modules
3. Consider implementing field-level encryption for sensitive data

## Migration Required

Run the following SQL migration in your Supabase dashboard:
```sql
-- See: /docs/migration_004_credentials_management.sql
```

This creates all necessary tables and security policies.