# DNS Automator

DNS Automator is a Python service that automates DNS configuration for the Website Factory system. It handles updating domain nameservers at registrars (Namecheap/Spaceship) and configuring DNS zones and records in Cloudflare.

## Features

- 🔄 Automated nameserver updates at domain registrars (Namecheap & Spaceship)
- ☁️ Cloudflare zone creation and DNS record configuration
- 🔐 Secure credential management via Supabase database
- 🔁 Retry logic with exponential backoff for API calls
- 📊 Comprehensive logging and error tracking
- 🚀 Railway-ready deployment configuration

## Architecture

The DNS Automator follows a modular architecture:

```
dns_automator/
├── core/           # Core utilities (config, logging)
├── services/       # External service clients
│   ├── supabase_client.py    # Database operations
│   ├── namecheap_client.py   # Namecheap API
│   ├── spaceship_client.py   # Spaceship API
│   └── cloudflare_client.py  # Cloudflare API
└── main.py         # Main orchestrator
```

## Prerequisites

- Python 3.9+
- Supabase project with proper schema
- Credentials configured via Management Hub Settings page:
  - Domain registrar credentials (Namecheap or Spaceship)
  - Cloudflare accounts
  - Server configurations with IP addresses

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Website-Factory-System/dns-automator.git
cd dns-automator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment template:
```bash
cp .env.example .env
```

5. Configure your `.env` file with required credentials.

## Configuration

### Deployment Modes

#### 1. API Service Mode (Recommended for Production)
Deploy as a FastAPI service that receives credentials from Management Hub:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

No environment variables needed! All credentials are passed by the Management Hub API.

#### 2. Standalone Mode (For Testing)
Run directly with environment variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Optional
LOG_LEVEL=INFO  # Logging level (DEBUG, INFO, WARNING, ERROR)
SITE_ID=uuid    # Process specific site (for testing)
```

All other credentials (domain registrars, Cloudflare accounts, server IPs) are managed through the Management Hub Settings page and stored in the database.

### Database Configuration

The DNS Automator uses these Supabase tables:

- `sites` - Website records with DNS status tracking
- `cloudflare_accounts` - Cloudflare account credentials
- `registrar_credentials` - Domain registrar API credentials (Namecheap/Spaceship)
- `servers` - Hosting server configurations with IP addresses

## Usage

### Local Development

Run the automator:
```bash
python run.py
```

Or use the module directly:
```bash
python -m dns_automator.main
```

### Processing Specific Site

To process a specific site (useful for testing):
```bash
SITE_ID=your-site-uuid python run.py
```

### Railway Deployment

The service is configured for Railway deployment:

1. Push to GitHub
2. Connect repository to Railway
3. Set environment variables in Railway
4. Deploy

Railway will automatically:
- Detect Python runtime
- Install dependencies from `requirements.txt`
- Run the service

## Workflow

1. **Fetch Pending Sites**: Queries Supabase for sites with `status_dns = 'pending'`
2. **Load Credentials**: Fetches registrar and Cloudflare credentials from database
3. **Update Nameservers**: Automatically tries configured registrars (Namecheap, then Spaceship) until one succeeds
4. **Configure Cloudflare**:
   - Creates DNS zone
   - Adds A record for root domain → server IP
   - Adds CNAME record for www → root domain
5. **Update Status**: Marks site as `active` or `failed` with error details

## API Integrations

### Namecheap
- Uses XML API
- Requires whitelisted IP address
- Supports custom nameserver updates

### Spaceship
- Uses REST API with OAuth2
- Automatic token refresh
- Modern JSON-based interface

### Cloudflare
- Uses official Python SDK
- Scoped API tokens recommended
- Automatic record conflict resolution

## Error Handling

- **Retry Logic**: All API calls use exponential backoff (3 attempts)
- **Status Tracking**: Failed sites marked with error messages in database
- **Isolation**: One site's failure doesn't affect others
- **Comprehensive Logging**: All operations logged with context

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Registrar

1. Create new client in `services/` directory
2. Implement `set_nameservers()` method
3. Add client initialization in `main.py`
4. Update database schema if needed

## Monitoring

- Check `logs/dns_automator.log` for detailed execution logs
- Monitor Supabase `sites` table for status updates
- Failed sites will have details in `error_message` column

## Security Notes

- Never commit `.env` files
- Use scoped API tokens where possible
- Credentials stored encrypted in Supabase
- Service role key required for database access

## Troubleshooting

### Common Issues

1. **"No credentials found"**: Check database or environment variables
2. **"Zone already exists"**: Normal - will fetch existing zone
3. **"Nameserver update failed"**: Verify domain ownership and API credentials
4. **"Invalid domain format"**: Ensure domain is in format `example.com`

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python run.py
```

## License

Part of the Website Factory System. All rights reserved.