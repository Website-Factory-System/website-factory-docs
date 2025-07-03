-- Migration 006: Add Cloudflare Account ID field
-- Issue: Missing account.id in zone creation requests causing "Invalid API key" errors
-- According to Cloudflare docs: https://developers.cloudflare.com/fundamentals/manage-domains/add-multiple-sites-automation/

ALTER TABLE cloudflare_accounts 
ADD COLUMN cloudflare_account_id TEXT;

-- Add comment to explain the field
COMMENT ON COLUMN cloudflare_accounts.cloudflare_account_id IS 'The actual Cloudflare Account ID (not the API token) required for zone creation API calls';

-- Note: This field will need to be populated manually for existing accounts
-- Users can find their Account ID in the Cloudflare dashboard right sidebar