# DNS Automator Deployment Guide

## How to Connect DNS Automator to Management Hub

### Step 1: Deploy DNS Automator on Railway

1. Push the code to GitHub (already done)
2. Create a new service in Railway
3. Connect the GitHub repository
4. Railway will automatically deploy it

### Step 2: Get the Internal URL

After deployment, Railway provides two URLs:
- **Public URL**: `https://dns-automator-production.up.railway.app` (accessible from internet)
- **Internal URL**: `http://dns-automator.railway.internal` (only accessible within your Railway project)

### Step 3: Configure Management Hub API

Add this environment variable to your Management Hub API service in Railway:

```
DNS_AUTOMATOR_URL=http://dns-automator.railway.internal
```

This uses Railway's private networking - the services talk directly without going through the public internet.

### Step 4: How It Works

1. User clicks "Setup DNS" in the UI
2. UI calls Management Hub API
3. Management Hub API calls DNS Automator via internal URL:
   ```
   POST http://dns-automator.railway.internal/process
   {
     "supabase_url": "...",
     "supabase_service_key": "...",
     "site_id": "..."
   }
   ```
4. DNS Automator:
   - Uses the provided Supabase credentials
   - Fetches site details and other credentials from database
   - Updates nameservers at registrar
   - Creates Cloudflare zone and records
   - Updates site status in database

### Security Benefits

- ✅ DNS Automator is NOT exposed to public internet
- ✅ Only Management Hub API can call it
- ✅ Supabase credentials stay within Railway's private network
- ✅ No hardcoded credentials in DNS Automator

### Testing the Connection

1. Deploy both services
2. Check Management Hub API logs for the DNS_AUTOMATOR_URL
3. Try creating a new site and triggering DNS setup
4. Check logs in both services

### Fallback Behavior

If `DNS_AUTOMATOR_URL` is not set, the Management Hub API will:
- Use the simulated workflow (current behavior)
- Log a warning
- Still update the site status

This means you can deploy and test incrementally without breaking existing functionality.

## Alternative Approaches (Not Recommended)

### Why NOT Service Accounts?

A "service account" approach would mean:
1. Creating a dedicated Supabase user just for automation
2. Storing its credentials in every automation service
3. Managing permissions for that account

This is MORE complex than what we have now and doesn't solve the core issue.

### Why NOT Redis/Queue?

A queue-based approach would mean:
1. Adding Redis to your infrastructure
2. Management Hub puts jobs in queue
3. DNS Automator polls queue for jobs

This adds complexity without clear benefits for your use case.

## Summary

The private networking approach is:
- ✅ Simple to implement (just one env var)
- ✅ Secure (internal traffic only)
- ✅ Scalable (can add more automation services the same way)
- ✅ Portable (can replicate this pattern anywhere that supports private networking)