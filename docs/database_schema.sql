-- Website Factory Database Schema
-- Run this in your Supabase SQL Editor

-- Cloudflare accounts table
CREATE TABLE cloudflare_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    email TEXT NOT NULL UNIQUE,
    account_nickname TEXT NOT NULL UNIQUE,
    api_token TEXT NOT NULL
);

-- Google Search Console accounts table  
CREATE TABLE gsc_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    oauth_refresh_token TEXT NOT NULL
);

-- Sites table - central tracking
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    domain TEXT NOT NULL UNIQUE,
    brand_name TEXT,
    cloudflare_account_id UUID NOT NULL REFERENCES cloudflare_accounts(id),
    gsc_account_id UUID REFERENCES gsc_accounts(id),
    status_dns TEXT NOT NULL DEFAULT 'pending',
    status_hosting TEXT NOT NULL DEFAULT 'pending',
    status_content TEXT NOT NULL DEFAULT 'pending',
    status_deployment TEXT NOT NULL DEFAULT 'pending',
    gsc_verification_status TEXT NOT NULL DEFAULT 'pending',
    hosting_doc_root TEXT,
    matomo_site_id INTEGER,
    error_message TEXT
);

-- Daily analytics aggregation
CREATE TABLE daily_analytics (
    date DATE NOT NULL,
    site_id UUID NOT NULL REFERENCES sites(id),
    matomo_visits INTEGER,
    gsc_clicks INTEGER,
    gsc_impressions INTEGER,
    PRIMARY KEY (date, site_id)
);

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Insert sample Cloudflare account for testing
INSERT INTO cloudflare_accounts (email, account_nickname, api_token) 
VALUES ('test@example.com', 'CF_Test_1', 'sample_api_token_replace_with_real');

-- Insert default admin user (password: 'admin123' - change in production!)
INSERT INTO users (username, email, hashed_password)
VALUES ('admin', 'admin@websitefactory.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');

-- Create indexes for better performance
CREATE INDEX idx_sites_domain ON sites(domain);
CREATE INDEX idx_sites_created_at ON sites(created_at);
CREATE INDEX idx_daily_analytics_date ON daily_analytics(date);
CREATE INDEX idx_daily_analytics_site_id ON daily_analytics(site_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);