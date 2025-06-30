# Hosting Automator

This module is responsible for automating the server-side hosting setup for websites in the Website Factory system. It provisions hosting environments on CloudPanel, configures SSL certificates, and sets up analytics tracking in Matomo.

## Features

- **CloudPanel Integration**: Creates static sites via CLI commands over SSH
- **SSL Provisioning**: Automatically provisions Let's Encrypt SSL certificates
- **Matomo Analytics**: Creates tracking sites in self-hosted Matomo instance
- **Status Tracking**: Updates site status in Supabase database
- **Error Handling**: Comprehensive error handling with status updates

## Architecture

The Hosting Automator follows the same FastAPI service pattern as other automation modules:

1. **FastAPI Service**: Receives requests from Management Hub API
2. **Background Processing**: Runs automation tasks asynchronously
3. **SSH/CLI Automation**: Executes CloudPanel commands via Paramiko
4. **Database Integration**: Fetches credentials and updates status via Supabase

## Setup

### Prerequisites

- Python 3.9+
- Access to Supabase database
- SSH access to CloudPanel server
- Matomo API token (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/Website-Factory-System/hosting-automator.git
cd hosting-automator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

The service receives all configuration via the Management Hub API. No local environment variables are needed.

Required credentials in Supabase:
- **servers** table: SSH connection details
- **infrastructure_services** table: Matomo API credentials

## Running the Service

### Development

```bash
# Run with uvicorn
uvicorn app:app --reload --port 8001
```

### Production (via Railway)

The service is designed to run on Railway with private networking:

1. Deploy to Railway
2. Use internal URL: `http://hosting-automator.railway.internal`
3. Management Hub API will call this service internally

## API Endpoints

### POST /process
Process hosting setup for pending sites

Request body:
```json
{
  "supabase_url": "https://xxx.supabase.co",
  "supabase_service_key": "xxx",
  "site_id": "optional-specific-site-id"
}
```

Response:
```json
{
  "status": "accepted",
  "message": "Hosting automation task started",
  "task_id": "site-id-if-provided"
}
```

### GET /health
Health check endpoint

Response:
```json
{
  "status": "healthy",
  "service": "hosting-automator",
  "version": "1.0.0",
  "features": ["cloudpanel", "ssl", "matomo"]
}
```

## Workflow

1. **Fetch Pending Sites**: Queries sites with `status_dns='active'` and `status_hosting='pending'`
2. **SSH Connection**: Establishes secure connection to CloudPanel server
3. **Site Creation**: Executes `clpctl site:add:static` command
4. **SSL Provisioning**: Executes `clpctl lets-encrypt:install:certificate` command
5. **Matomo Setup**: Creates tracking site via Matomo API (if configured)
6. **Status Update**: Updates site status to 'active' with metadata

## Security

- **SSH Key Management**: Private keys stored securely in database
- **Command Injection Prevention**: Input sanitization and validation
- **Secure Password Generation**: Uses Python's `secrets` module
- **SSL Verification**: Verifies SSL certificates for API calls

## Error Handling

- **Idempotency**: Handles "already exists" errors gracefully
- **Partial Failures**: Matomo failures don't block hosting setup
- **Status Updates**: Failed operations update site status with error messages
- **Logging**: Comprehensive logging for debugging

## CloudPanel CLI Commands Used

- `clpctl site:add:static`: Creates a new static website
- `clpctl lets-encrypt:install:certificate`: Provisions SSL certificate

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=hosting_automator
```

## Integration with Management Hub

The Management Hub API calls this service when:
1. A new site's DNS status becomes 'active'
2. Manual retry is triggered for failed hosting setups

Example integration:
```python
# In Management Hub API
response = requests.post(
    "http://hosting-automator.railway.internal/process",
    json={
        "supabase_url": settings.SUPABASE_URL,
        "supabase_service_key": settings.SUPABASE_SERVICE_KEY,
        "site_id": site_id
    }
)