-- Migration 005: Add Processing Status Tracking
-- This migration adds tables for tracking detailed workflow processing status

-- Workflow processing steps table
CREATE TABLE IF NOT EXISTS workflow_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    phase TEXT NOT NULL, -- 'dns_setup', 'hosting_setup', 'content_generation', 'deployment'
    step_name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Active processing status (only one site at a time)
CREATE TABLE IF NOT EXISTS active_processing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    current_phase TEXT NOT NULL,
    current_step_id UUID REFERENCES workflow_steps(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(site_id) -- Only one active processing per site
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_workflow_steps_site_id ON workflow_steps(site_id);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_phase ON workflow_steps(phase);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_status ON workflow_steps(status);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_created_at ON workflow_steps(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_active_processing_site_id ON active_processing(site_id);

-- Create updated_at trigger for active_processing
CREATE TRIGGER update_active_processing_updated_at BEFORE UPDATE ON active_processing
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add phase step counts to sites table for quick progress calculation
ALTER TABLE sites ADD COLUMN IF NOT EXISTS dns_steps_completed INTEGER DEFAULT 0;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS dns_steps_total INTEGER DEFAULT 6;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS hosting_steps_completed INTEGER DEFAULT 0;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS hosting_steps_total INTEGER DEFAULT 5;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS content_steps_completed INTEGER DEFAULT 0;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS content_steps_total INTEGER DEFAULT 8;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS deployment_steps_completed INTEGER DEFAULT 0;
ALTER TABLE sites ADD COLUMN IF NOT EXISTS deployment_steps_total INTEGER DEFAULT 4;