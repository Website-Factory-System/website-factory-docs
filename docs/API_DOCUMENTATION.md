# Website Factory Management Hub API Documentation

## Overview

The Management Hub API is a comprehensive RESTful API for managing 200+ websites through automated workflows. Built with FastAPI, it provides endpoints for site management, credential storage, workflow orchestration, and system monitoring.

**Base URL:** `https://your-api-domain.com`  
**Authentication:** JWT Bearer Token  
**API Version:** 1.0.0

## Authentication

### JWT Token Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### POST `/auth/token`
**Description:** Login endpoint - obtain JWT access token  
**Authentication:** None required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=your-username&password=your-password
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "username": "your-username",
    "email": "user@example.com",
    "is_active": true
  }
}
```

#### GET `/auth/me`
**Description:** Get current user information  
**Authentication:** JWT Required

**Response:**
```json
{
  "id": "user-uuid",
  "username": "your-username", 
  "email": "user@example.com",
  "is_active": true
}
```

#### POST `/auth/refresh`
**Description:** Refresh JWT token  
**Authentication:** JWT Required

**Response:**
```json
{
  "access_token": "new-jwt-token...",
  "token_type": "bearer"
}
```

#### POST `/auth/change-password`
**Description:** Change user password  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "current_password": "current-password",
  "new_password": "new-password"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

---

## Site Management

### GET `/sites/`
**Description:** Get sites with pagination and filtering  
**Authentication:** JWT Required

**Query Parameters:**
- `limit` (integer, 1-100, default: 50): Number of items per page
- `offset` (integer, ≥0, default: 0): Number of items to skip
- `status_dns` (string, optional): Filter by DNS status
- `status_hosting` (string, optional): Filter by hosting status  
- `status_content` (string, optional): Filter by content status
- `status_deployment` (string, optional): Filter by deployment status
- `domain_search` (string, optional): Search by domain name
- `has_error` (boolean, optional): Filter sites with errors

**Response:**
```json
{
  "items": [
    {
      "id": "site-uuid",
      "domain": "example.com",
      "brand_name": "Example Brand",
      "cloudflare_account_id": "cf-account-uuid",
      "gsc_account_id": "gsc-account-uuid",
      "status_dns": "active",
      "status_hosting": "active", 
      "status_content": "generated",
      "status_deployment": "deployed",
      "gsc_verification_status": "verified",
      "hosting_doc_root": "/var/www/example.com",
      "matomo_site_id": 123,
      "error_message": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_next": true,
  "has_prev": false
}
```

### POST `/sites/`
**Description:** Create a single new site  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "domain": "newsite.com",
  "brand_name": "New Site Brand",
  "cloudflare_account_id": "cf-account-uuid"
}
```

**Response:**
```json
{
  "id": "new-site-uuid",
  "domain": "newsite.com",
  "brand_name": "New Site Brand",
  "cloudflare_account_id": "cf-account-uuid",
  "status_dns": "pending",
  "status_hosting": "pending",
  "status_content": "pending",
  "status_deployment": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST `/sites/bulk`
**Description:** Create multiple sites from CSV data  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "sites": [
    {
      "domain": "site1.com",
      "brand_name": "Site 1",
      "cloudflare_account_nickname": "CF_Batch_1"
    },
    {
      "domain": "site2.com", 
      "brand_name": "Site 2",
      "cloudflare_account_nickname": "CF_Batch_2"
    }
  ]
}
```

**Response:**
```json
{
  "created": 2,
  "failed": 0,
  "errors": []
}
```

### GET `/sites/simple`
**Description:** Get all sites without pagination  
**Authentication:** JWT Required

**Response:**
```json
[
  {
    "id": "site-uuid",
    "domain": "example.com",
    "brand_name": "Example Brand",
    "status_dns": "active"
  }
]
```

### GET `/sites/stats`
**Description:** Get site statistics for dashboard  
**Authentication:** JWT Required

**Response:**
```json
{
  "total_sites": 150,
  "active_sites": 140,
  "pending_sites": 8,
  "failed_sites": 2,
  "dns_stats": {
    "active": 140,
    "pending": 8,
    "failed": 2
  },
  "hosting_stats": {
    "active": 135,
    "pending": 12,
    "failed": 3
  }
}
```

### PATCH `/sites/{site_id}`
**Description:** Update a site with partial data  
**Authentication:** JWT Required

**Path Parameters:**
- `site_id` (string): Site UUID

**Request Body:**
```json
{
  "brand_name": "Updated Brand Name",
  "status_dns": "active"
}
```

**Response:**
```json
{
  "id": "site-uuid",
  "domain": "example.com",
  "brand_name": "Updated Brand Name",
  "status_dns": "active",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### DELETE `/sites/{site_id}`
**Description:** Delete a site and all related data  
**Authentication:** JWT Required

**Path Parameters:**
- `site_id` (string): Site UUID

**Response:**
```json
{
  "message": "Site deleted successfully",
  "site_id": "site-uuid"
}
```

### POST `/sites/{site_id}/retry`
**Description:** Retry all failed workflows for a site  
**Authentication:** JWT Required

**Path Parameters:**
- `site_id` (string): Site UUID

**Response:**
```json
{
  "retried": 3,
  "message": "Retried 3 failed workflows for site"
}
```

---

## Workflow Management

### POST `/workflows/trigger`
**Description:** Trigger a workflow for a specific site  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "workflow_type": "content", 
  "site_id": "site-uuid"
}
```

**Workflow Types:**
- `content`: AI content generation
- `deployment`: Site deployment

**Response:**
```json
{
  "message": "content workflow started",
  "site_id": "site-uuid"
}
```

---

## Monitoring & System Health

### GET `/monitoring/workflows/executions`
**Description:** Get workflow executions with filtering  
**Authentication:** JWT Required

**Query Parameters:**
- `site_id` (string, optional): Filter by site ID
- `workflow_type` (string, optional): Filter by workflow type
- `status` (string, optional): Filter by status
- `limit` (integer, 1-200, default: 50): Number of executions to return
- `days` (integer, 1-30, default: 7): Number of days to look back

**Response:**
```json
[
  {
    "id": "execution-uuid",
    "site_id": "site-uuid",
    "workflow_type": "dns",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:05:00Z",
    "error_message": null
  }
]
```

### GET `/monitoring/workflows/stats`
**Description:** Get workflow statistics  
**Authentication:** JWT Required

**Query Parameters:**
- `days` (integer, 1-30, default: 7): Number of days for statistics

**Response:**
```json
{
  "total_executions": 1250,
  "successful": 1180,
  "failed": 70,
  "success_rate": 94.4,
  "by_workflow_type": {
    "dns": {"total": 400, "successful": 385, "failed": 15},
    "hosting": {"total": 350, "successful": 340, "failed": 10},
    "content": {"total": 300, "successful": 275, "failed": 25},
    "deployment": {"total": 200, "successful": 180, "failed": 20}
  }
}
```

### GET `/monitoring/workflows/sites/{site_id}/executions`
**Description:** Get all workflow executions for a specific site  
**Authentication:** JWT Required

**Path Parameters:**
- `site_id` (string): Site UUID

**Response:**
```json
[
  {
    "id": "execution-uuid",
    "workflow_type": "dns",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:05:00Z"
  }
]
```

### GET `/monitoring/workflows/failed`
**Description:** Get failed workflow executions for immediate attention  
**Authentication:** JWT Required

**Query Parameters:**
- `days` (integer, 1-7, default: 1): Number of days to look back

**Response:**
```json
[
  {
    "id": "execution-uuid",
    "site_id": "site-uuid",
    "workflow_type": "dns",
    "status": "failed",
    "error_message": "API key invalid",
    "started_at": "2024-01-01T00:00:00Z",
    "failed_at": "2024-01-01T00:02:00Z"
  }
]
```

### GET `/monitoring/workflows/retrying`
**Description:** Get workflows currently in retry state  
**Authentication:** JWT Required

**Response:**
```json
[
  {
    "id": "execution-uuid",
    "site_id": "site-uuid", 
    "workflow_type": "hosting",
    "status": "retrying",
    "retry_count": 2,
    "max_retries": 3,
    "next_retry_at": "2024-01-01T00:10:00Z"
  }
]
```

### POST `/monitoring/workflows/{execution_id}/retry`
**Description:** Manually trigger retry for a specific workflow execution  
**Authentication:** JWT Required

**Path Parameters:**
- `execution_id` (string): Workflow execution UUID

**Response:**
```json
{
  "message": "Workflow retry triggered",
  "execution_id": "execution-uuid"
}
```

### GET `/monitoring/system/health`
**Description:** Get overall system health metrics  
**Authentication:** JWT Required

**Response:**
```json
{
  "status": "healthy",
  "health_score": 95.2,
  "issues": [],
  "components": {
    "database": "healthy",
    "external_apis": "healthy", 
    "automation_modules": "healthy"
  },
  "workflow_stats": {
    "active_executions": 15,
    "failed_last_hour": 2,
    "avg_execution_time": "45s"
  }
}
```

### GET `/monitoring/alerts`
**Description:** Get system alerts  
**Authentication:** JWT Required

**Query Parameters:**
- `severity` (string, optional): Filter by severity level (low, medium, high, critical)
- `acknowledged` (boolean, optional): Filter by acknowledgment status

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-uuid",
      "severity": "high",
      "message": "DNS automation failure rate above 10%",
      "acknowledged": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "summary": {
    "total": 1,
    "unacknowledged": 1,
    "by_severity": {
      "critical": 0,
      "high": 1,
      "medium": 0,
      "low": 0
    }
  }
}
```

### POST `/monitoring/alerts/{alert_id}/acknowledge`
**Description:** Acknowledge an alert  
**Authentication:** JWT Required

**Path Parameters:**
- `alert_id` (string): Alert UUID

**Response:**
```json
{
  "message": "Alert acknowledged",
  "alert_id": "alert-uuid"
}
```

### POST `/monitoring/alerts/{alert_id}/resolve`
**Description:** Resolve an alert  
**Authentication:** JWT Required

**Path Parameters:**
- `alert_id` (string): Alert UUID

**Response:**
```json
{
  "message": "Alert resolved",
  "alert_id": "alert-uuid"
}
```

### POST `/monitoring/health-check`
**Description:** Manually trigger system health checks  
**Authentication:** JWT Required

**Response:**
```json
{
  "health_check_id": "check-uuid",
  "status": "running",
  "message": "Health check initiated"
}
```

---

## Status & Processing

### GET `/status/processing`
**Description:** Get current processing status for all workflows  
**Authentication:** JWT Required

**Response:**
```json
{
  "dns_automator": {
    "status": "idle",
    "last_execution": "2024-01-01T00:00:00Z",
    "sites_in_queue": 0
  },
  "hosting_automator": {
    "status": "processing",
    "current_site": "site-uuid",
    "sites_in_queue": 3
  },
  "content_engine": {
    "status": "idle",
    "sites_in_queue": 0
  },
  "deployment_scripts": {
    "status": "idle", 
    "sites_in_queue": 0
  }
}
```

### POST `/status/update-step`
**Description:** Update the current processing step (called by automation modules)  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "module": "dns_automator",
  "site_id": "site-uuid",
  "step": "configuring_cloudflare_zone",
  "status": "in_progress",
  "message": "Creating DNS zone for example.com"
}
```

**Response:**
```json
{
  "status": "updated"
}
```

---

## Credentials Management

All credentials endpoints use the `/api/v1/credentials` prefix.

### Server Management

#### GET `/api/v1/credentials/servers`
**Description:** List all servers  
**Authentication:** JWT Required

**Query Parameters:**
- `active_only` (boolean, default: false): Filter active servers only

**Response:**
```json
[
  {
    "id": "server-uuid",
    "name": "Main Server",
    "ip_address": "192.168.1.100",
    "type": "vultr",
    "cloudpanel_url": "https://192.168.1.100:8080",
    "is_active": true,
    "metadata": {},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST `/api/v1/credentials/servers`
**Description:** Create a new server configuration  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "name": "New Server",
  "ip_address": "192.168.1.101",
  "type": "vultr",
  "cloudpanel_url": "https://192.168.1.101:8080",
  "is_active": true,
  "metadata": {}
}
```

**Response:**
```json
{
  "id": "new-server-uuid",
  "name": "New Server",
  "ip_address": "192.168.1.101",
  "type": "vultr",
  "cloudpanel_url": "https://192.168.1.101:8080",
  "is_active": true,
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/v1/credentials/servers/{server_id}`
**Description:** Get a specific server by ID  
**Authentication:** JWT Required

**Path Parameters:**
- `server_id` (string): Server UUID

#### PUT `/api/v1/credentials/servers/{server_id}`
**Description:** Update server configuration  
**Authentication:** JWT Required

**Path Parameters:**
- `server_id` (string): Server UUID

**Request Body:**
```json
{
  "name": "Updated Server Name",
  "is_active": false
}
```

#### DELETE `/api/v1/credentials/servers/{server_id}`
**Description:** Delete a server (soft delete)  
**Authentication:** JWT Required

**Path Parameters:**
- `server_id` (string): Server UUID

**Response:**
```json
{
  "success": true
}
```

### Registrar Credentials

#### GET `/api/v1/credentials/registrars`
**Description:** List registrar credentials  
**Authentication:** JWT Required

**Query Parameters:**
- `provider` (string, optional): Filter by provider

**Response:**
```json
[
  {
    "id": "registrar-uuid",
    "provider": "namecheap",
    "api_user": "your-api-user",
    "api_endpoint": "https://api.namecheap.com/xml.response",
    "username": "your-username",
    "client_ip": "192.168.1.100",
    "is_active": true,
    "metadata": {},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST `/api/v1/credentials/registrars`
**Description:** Create or update registrar credentials  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "provider": "namecheap",
  "api_user": "your-api-user",
  "api_key": "your-api-key",
  "api_secret": "your-api-secret",
  "api_endpoint": "https://api.namecheap.com/xml.response",
  "username": "your-username",
  "client_ip": "192.168.1.100",
  "is_active": true
}
```

#### PUT `/api/v1/credentials/registrars/{provider}`
**Description:** Update registrar credentials  
**Authentication:** JWT Required

**Path Parameters:**
- `provider` (string): Provider name (e.g., "namecheap")

### Infrastructure Credentials

#### GET `/api/v1/credentials/infrastructure`
**Description:** List infrastructure credentials  
**Authentication:** JWT Required

**Query Parameters:**
- `service_name` (string, optional): Filter by service name

**Response:**
```json
[
  {
    "id": "infra-uuid",
    "service": "matomo",
    "url": "https://analytics.example.com",
    "username": "admin",
    "is_active": true,
    "metadata": {},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST `/api/v1/credentials/infrastructure`
**Description:** Create or update infrastructure credentials  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "service": "matomo",
  "url": "https://analytics.example.com",
  "username": "admin",
  "password": "secure-password",
  "api_token": "api-token-here",
  "is_active": true
}
```

#### PUT `/api/v1/credentials/infrastructure/{service}`
**Description:** Update infrastructure credentials  
**Authentication:** JWT Required

**Path Parameters:**
- `service` (string): Service name

### Cloudflare Accounts

#### GET `/api/v1/credentials/cloudflare-accounts`
**Description:** List all Cloudflare accounts  
**Authentication:** JWT Required

**Response:**
```json
[
  {
    "id": "cf-uuid",
    "email": "user+cf1@example.com",
    "account_nickname": "CF_Batch_1",
    "api_token": "api-token...",
    "cloudflare_account_id": "abc123def456...",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST `/api/v1/credentials/cloudflare-accounts`
**Description:** Create a new Cloudflare account  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "email": "user+cf2@example.com",
  "account_nickname": "CF_Batch_2", 
  "api_token": "new-api-token...",
  "cloudflare_account_id": "def789ghi012..."
}
```

#### GET `/api/v1/credentials/cloudflare-accounts/{account_id}`
**Description:** Get a specific Cloudflare account by ID  
**Authentication:** JWT Required

**Path Parameters:**
- `account_id` (string): Cloudflare account UUID

#### PUT `/api/v1/credentials/cloudflare-accounts/{account_id}`
**Description:** Update Cloudflare account  
**Authentication:** JWT Required

**Path Parameters:**
- `account_id` (string): Cloudflare account UUID

#### DELETE `/api/v1/credentials/cloudflare-accounts/{account_id}`
**Description:** Delete a Cloudflare account  
**Authentication:** JWT Required

**Path Parameters:**
- `account_id` (string): Cloudflare account UUID

**Response:**
```json
{
  "success": true
}
```

### Cloudflare Bulk Import

#### POST `/api/v1/credentials/cloudflare/bulk-import`
**Description:** Bulk import Cloudflare accounts from CSV file  
**Authentication:** JWT Required  
**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: CSV file with headers: `email,account_nickname,api_token,cloudflare_account_id`

**CSV Format Example:**
```csv
email,account_nickname,api_token,cloudflare_account_id
user+cf1@gmail.com,CF_Batch_1,token123...,abc123def456...
user+cf2@gmail.com,CF_Batch_2,token456...,def789ghi012...
```

**Response:**
```json
{
  "imported": 2,
  "failed": 0,
  "errors": []
}
```

#### POST `/api/v1/credentials/cloudflare/bulk-import-json`
**Description:** Bulk import Cloudflare accounts from JSON  
**Authentication:** JWT Required

**Request Body:**
```json
{
  "accounts": [
    {
      "email": "user+cf1@example.com",
      "account_nickname": "CF_Batch_1",
      "api_token": "token123...",
      "cloudflare_account_id": "abc123def456..."
    }
  ]
}
```

**Response:**
```json
{
  "imported": 1,
  "failed": 0,
  "errors": []
}
```

---

## Debug & Utilities

### GET `/`
**Description:** API welcome message and version info  
**Authentication:** None required

**Response:**
```json
{
  "message": "Website Factory Management Hub API",
  "version": "1.0.0"
}
```

### GET `/health`
**Description:** Health check endpoint  
**Authentication:** None required

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### GET `/debug/cloudflare-count`
**Description:** Debug endpoint to check cloudflare accounts without auth  
**Authentication:** None required

**Response:**
```json
{
  "count": 5,
  "accounts": [
    {
      "id": "cf-uuid",
      "email": "user+cf1@example.com",
      "nickname": "CF_Batch_1",
      "has_account_id": true
    }
  ]
}
```

### GET `/debug/test-internal-network`
**Description:** Test Railway internal networking  
**Authentication:** JWT Required

**Response:**
```json
{
  "network_test": "passed",
  "internal_services": {
    "database": "accessible",
    "external_apis": "accessible"
  }
}
```

---

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error: Invalid domain format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Site not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "domain"],
      "msg": "Invalid domain format",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Data Models

### Site
```json
{
  "id": "string (uuid)",
  "domain": "string",
  "brand_name": "string",
  "cloudflare_account_id": "string (uuid)",
  "gsc_account_id": "string (uuid, optional)",
  "status_dns": "string (pending|active|failed)",
  "status_hosting": "string (pending|active|failed)",
  "status_content": "string (pending|generating|generated|failed)",
  "status_deployment": "string (pending|deploying|deployed|failed)",
  "gsc_verification_status": "string (pending|verified|failed)",
  "hosting_doc_root": "string (optional)",
  "matomo_site_id": "integer (optional)",
  "error_message": "string (optional)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### CloudflareAccount
```json
{
  "id": "string (uuid)",
  "email": "string",
  "account_nickname": "string",
  "api_token": "string",
  "cloudflare_account_id": "string (optional)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### WorkflowExecution
```json
{
  "id": "string (uuid)",
  "site_id": "string (uuid)",
  "workflow_type": "string (dns|hosting|content|deployment)",
  "status": "string (pending|running|completed|failed|retrying)",
  "started_at": "string (ISO 8601)",
  "completed_at": "string (ISO 8601, optional)",
  "error_message": "string (optional)",
  "retry_count": "integer",
  "max_retries": "integer"
}
```

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **General endpoints:** 100 requests per minute per user
- **Bulk operations:** 10 requests per minute per user
- **Authentication endpoints:** 20 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## WebSocket (Future Feature)

Real-time updates for workflow status will be available via WebSocket:

```javascript
const ws = new WebSocket('wss://your-api-domain.com/ws');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Handle real-time workflow updates
};
```

---

## SDKs and Integrations

### Python SDK (Planned)
```python
from website_factory import ManagementHubClient

client = ManagementHubClient(api_key="your-jwt-token")
sites = client.sites.list(limit=50)
```

### JavaScript SDK (Planned)
```javascript
import { ManagementHubClient } from '@website-factory/sdk';

const client = new ManagementHubClient({ apiKey: 'your-jwt-token' });
const sites = await client.sites.list({ limit: 50 });
```

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Full CRUD operations for sites, credentials, workflows
- JWT authentication
- Comprehensive monitoring endpoints
- Bulk import capabilities

---

For additional support or questions, please refer to the project documentation or contact the development team.