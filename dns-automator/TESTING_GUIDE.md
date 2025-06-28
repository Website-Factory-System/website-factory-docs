# DNS Automator Testing Guide

## Prerequisites Checklist

Before testing, ensure you have:

1. ✅ **Credentials in Database** (via Management Hub Settings page):
   - [ ] At least one Cloudflare account
   - [ ] Domain registrar credentials (Namecheap or Spaceship)
   - [ ] At least one server with IP address

2. ✅ **Services Deployed**:
   - [ ] Management Hub API running
   - [ ] DNS Automator deployed on Railway
   - [ ] Environment variable set: `DNS_AUTOMATOR_URL=http://dns-automator.railway.internal`

## Step-by-Step Testing Process

### Step 1: Verify Credentials

1. **Login to Management Hub UI**
   ```
   https://management-hub-ui-production.up.railway.app
   ```

2. **Go to Settings Page**
   - Click "Settings" in sidebar
   - Check each tab:
     - **Servers**: At least one server with IP address
     - **Domain Registrars**: Namecheap or Spaceship credentials
     - **Cloudflare**: At least one account

3. **If Missing Credentials**, add them:
   - **Cloudflare**: Email, Nickname, API Token
   - **Namecheap**: API User, API Key, Username, Client IP
   - **Server**: Name, IP Address, mark as default

### Step 2: Check Service Health

1. **Check DNS Automator Health**
   ```bash
   # If public URL is enabled (not recommended for production)
   curl https://dns-automator-production.up.railway.app/health
   
   # Expected response:
   {
     "status": "healthy",
     "service": "dns-automator",
     "version": "1.0.0"
   }
   ```

2. **Check Management Hub API Logs**
   - Go to Railway dashboard
   - Click on management-hub-api service
   - Check logs for `DNS_AUTOMATOR_URL` confirmation

### Step 3: Create Test Site

1. **In Management Hub UI**:
   - Click "Add New Site" button
   - Enter domain: `test-domain-001.com` (use a domain you own)
   - Select a Cloudflare account from dropdown
   - Click "Create"

2. **Verify Site Created**:
   - Site appears in list with `status_dns: pending`

### Step 4: Trigger DNS Setup

Since DNS setup is triggered automatically when creating a site, check:

1. **Management Hub API Logs** (Railway):
   ```
   Executing DNS setup for site <site-id>
   DNS Automator response: {"status": "accepted", ...}
   ```

2. **DNS Automator Logs** (Railway):
   ```
   DNS Automator initialized
   Processing DNS for site: test-domain-001.com
   Successfully updated nameservers at namecheap
   Successfully created zone for test-domain-001.com
   Successfully completed DNS configuration
   ```

3. **Check Site Status**:
   - Refresh Management Hub UI
   - Site should show `status_dns: active` ✅

### Step 5: Verify Results

1. **Check Namecheap**:
   - Login to Namecheap
   - Find your domain
   - Verify nameservers changed to:
     - `celia.ns.cloudflare.com`
     - `cory.ns.cloudflare.com`

2. **Check Cloudflare**:
   - Login to Cloudflare (use account from dropdown)
   - Verify zone created for your domain
   - Check DNS records:
     - A record: @ → Server IP
     - CNAME record: www → domain

### Step 6: Troubleshooting

If something goes wrong:

1. **Site shows `status_dns: failed`**:
   - Check `error_message` in database
   - Common issues:
     - Wrong API credentials
     - Domain doesn't exist in registrar
     - Cloudflare API token lacks permissions

2. **"DNS_AUTOMATOR_URL not configured" in logs**:
   - Add env var to Management Hub API in Railway
   - Redeploy the service

3. **Connection refused errors**:
   - Ensure both services are in same Railway project
   - Check internal URL is exactly: `http://dns-automator.railway.internal`

4. **Timeout errors**:
   - DNS operations can take 30+ seconds
   - Check if registrar API is responding
   - Verify credentials are correct

## Manual Testing (Development)

For local testing without UI:

```bash
# 1. Set environment variables
export SUPABASE_URL=your-url
export SUPABASE_SERVICE_KEY=your-key
export SITE_ID=specific-site-uuid  # Optional

# 2. Run DNS Automator
python run.py

# 3. Check logs for results
```

## Success Indicators

✅ **Successful DNS Setup**:
- Site status changes from `pending` → `active`
- No error messages in logs
- Nameservers updated at registrar
- Cloudflare zone created with DNS records
- Process completes in under 60 seconds

❌ **Failed DNS Setup**:
- Site status shows `failed`
- Error message populated in database
- Detailed error in service logs
- Retry mechanism will attempt again (3 times)

## Next Steps After Testing

1. **If Successful**:
   - Deploy more sites!
   - Monitor for any edge cases
   - Check Railway usage/costs

2. **If Issues**:
   - Check logs in both services
   - Verify all credentials
   - Test with different domains
   - Report issues with full error details