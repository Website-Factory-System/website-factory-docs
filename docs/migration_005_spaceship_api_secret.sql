-- Migration: Add API secret support for Spaceship registrar
-- This adds an api_secret column to registrar_credentials table for Spaceship.com support

-- Add api_secret column to registrar_credentials
ALTER TABLE registrar_credentials 
ADD COLUMN IF NOT EXISTS api_secret TEXT;

-- Update the check constraint to allow api_secret (optional for most providers)
ALTER TABLE registrar_credentials 
DROP CONSTRAINT IF EXISTS registrar_credentials_provider_check;

ALTER TABLE registrar_credentials 
ADD CONSTRAINT registrar_credentials_provider_check 
CHECK (provider IN ('namecheap', 'spaceship'));

-- Add comment explaining the field usage
COMMENT ON COLUMN registrar_credentials.api_secret IS 'API secret for providers that require it (e.g., Spaceship). Encrypted at rest.';