-- Migration 004: Add Credentials Management Tables
-- This migration adds tables for storing API credentials and server configuration

-- Servers table for managing multiple hosting servers
CREATE TABLE IF NOT EXISTS servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'vultr', -- vultr, digitalocean, etc.
    cloudpanel_url TEXT,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Domain registrar credentials
CREATE TABLE IF NOT EXISTS registrar_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    provider TEXT NOT NULL, -- 'namecheap', 'spaceship'
    api_user TEXT,
    api_key TEXT NOT NULL,
    api_endpoint TEXT,
    client_ip TEXT, -- Required for Namecheap
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(provider)
);

-- Infrastructure credentials (Matomo, CloudPanel, etc.)
CREATE TABLE IF NOT EXISTS infrastructure_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service TEXT NOT NULL, -- 'matomo', 'cloudpanel', etc.
    url TEXT NOT NULL,
    username TEXT,
    password TEXT,
    api_token TEXT,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(service)
);

-- Update sites table to reference server
ALTER TABLE sites ADD COLUMN IF NOT EXISTS server_id UUID REFERENCES servers(id);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_servers_name ON servers(name);
CREATE INDEX IF NOT EXISTS idx_servers_is_active ON servers(is_active);
CREATE INDEX IF NOT EXISTS idx_registrar_credentials_provider ON registrar_credentials(provider);
CREATE INDEX IF NOT EXISTS idx_infrastructure_credentials_service ON infrastructure_credentials(service);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_servers_updated_at BEFORE UPDATE ON servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_registrar_credentials_updated_at BEFORE UPDATE ON registrar_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_infrastructure_credentials_updated_at BEFORE UPDATE ON infrastructure_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add RLS policies for security (assuming auth.uid() exists)
ALTER TABLE servers ENABLE ROW LEVEL SECURITY;
ALTER TABLE registrar_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE infrastructure_credentials ENABLE ROW LEVEL SECURITY;

-- Only authenticated users can access credentials
CREATE POLICY "Authenticated users can view servers"
    ON servers FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can manage servers"
    ON servers FOR ALL
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view registrar credentials"
    ON registrar_credentials FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can manage registrar credentials"
    ON registrar_credentials FOR ALL
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view infrastructure credentials"
    ON infrastructure_credentials FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can manage infrastructure credentials"
    ON infrastructure_credentials FOR ALL
    TO authenticated
    USING (true);