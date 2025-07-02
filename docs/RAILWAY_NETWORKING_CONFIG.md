# Railway Private Networking Configuration

## Overview
This document explains how to properly configure private networking between services in Railway for the Website Factory system.

## Key Requirements

### 1. Port Specification is MANDATORY
Railway's private networking requires explicit port specification in URLs. The format must be:
```
http://service-name.railway.internal:PORT
```

### 2. Environment Variables Configuration

#### For Management Hub API Service
Add these environment variables in Railway:

```bash
# DNS Automator connection
DNS_AUTOMATOR_URL=http://dns-automator.railway.internal
DNS_AUTOMATOR_PORT=8000

# Hosting Automator connection  
HOSTING_AUTOMATOR_URL=http://hosting-automator.railway.internal
HOSTING_AUTOMATOR_PORT=8000

# Existing variables
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-service-key
JWT_SECRET_KEY=your-jwt-secret
```

#### For DNS Automator Service
```bash
PORT=8000
# No other env vars needed - receives credentials from Management Hub
```

#### For Hosting Automator Service
```bash
PORT=8000  
# No other env vars needed - receives credentials from Management Hub
```

## Common Issues and Solutions

### Issue: "ConnectError - All connection attempts failed"
**Cause**: Missing port specification in internal URLs
**Solution**: Ensure URLs include port: `http://service.railway.internal:8000`

### Issue: Services can't find each other
**Cause**: Services in different Railway environments or projects
**Solution**: Ensure all services are in the same Railway project and environment

### Issue: IPv6 connection failures
**Cause**: Service not binding to IPv6
**Solution**: Services must use `host="::"` when starting (already configured in our services)

## Testing Private Networking

1. **Check Service Health via Public URL First**
   ```bash
   curl https://dns-automator-production.up.railway.app/health
   ```

2. **Monitor Logs During Workflow Execution**
   ```bash
   railway logs -s management-hub-api --tail 100
   ```

3. **Look for These Success Indicators**
   - "DNS_AUTOMATOR_URL configured as: http://dns-automator.railway.internal:8000"
   - "DNS Automator health check passed"
   - "DNS Automator response: {status: 'accepted'}"

## Architecture

```
Management Hub API -----> http://dns-automator.railway.internal:8000
                  \
                   -----> http://hosting-automator.railway.internal:8000
```

All services communicate via Railway's internal IPv6 network using the `.railway.internal` domain.

## Deployment Order

1. Deploy DNS Automator service first
2. Deploy Hosting Automator service  
3. Deploy Management Hub API with correct environment variables
4. Test by creating a new site through the UI

## Verification Steps

After deployment, verify the configuration:

1. Check Management Hub API logs for the correct URL format with port
2. Create a test site and monitor the workflow execution
3. Verify DNS automator receives the request
4. Check status updates in the UI

## Important Notes

- Never use HTTPS for internal communication (use HTTP)
- Port must be explicitly specified (default 8000)
- All services must be in the same Railway project
- Services automatically get IPv6 addresses in Railway's private network