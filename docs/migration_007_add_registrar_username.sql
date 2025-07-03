-- Migration 007: Add missing username field to registrar_credentials table
-- This field is required for Namecheap API authentication
-- Date: 2025-01-03

-- Add username column to registrar_credentials table
ALTER TABLE registrar_credentials 
ADD COLUMN username TEXT;

-- Add comment explaining the field
COMMENT ON COLUMN registrar_credentials.username IS 'Namecheap username (same as api_user typically). Required for Namecheap API authentication.';

-- For existing Namecheap credentials, set username = api_user as default
UPDATE registrar_credentials 
SET username = api_user 
WHERE provider = 'namecheap' AND username IS NULL;