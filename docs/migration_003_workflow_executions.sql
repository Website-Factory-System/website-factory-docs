-- Migration 003: Add workflow execution tracking
-- This enables robust workflow orchestration with retry logic and monitoring

CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    workflow_type TEXT NOT NULL, -- 'dns', 'hosting', 'content', 'deployment'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'retrying'
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_workflow_executions_site_id ON workflow_executions(site_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_type ON workflow_executions(workflow_type);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_next_retry ON workflow_executions(next_retry_at) WHERE status = 'retrying';
CREATE INDEX IF NOT EXISTS idx_workflow_executions_created_at ON workflow_executions(created_at);

-- Add a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_workflow_executions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_workflow_executions_updated_at ON workflow_executions;
CREATE TRIGGER trigger_update_workflow_executions_updated_at
    BEFORE UPDATE ON workflow_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_workflow_executions_updated_at();

-- Insert initial workflow executions for any existing sites
-- This ensures backward compatibility
INSERT INTO workflow_executions (site_id, workflow_type, status, started_at, completed_at)
SELECT 
    id as site_id,
    'dns' as workflow_type,
    CASE 
        WHEN status_dns = 'pending' THEN 'pending'
        WHEN status_dns = 'active' THEN 'completed'
        WHEN status_dns = 'failed' THEN 'failed'
        ELSE 'pending'
    END as status,
    created_at as started_at,
    CASE WHEN status_dns = 'active' THEN created_at ELSE NULL END as completed_at
FROM sites 
WHERE NOT EXISTS (
    SELECT 1 FROM workflow_executions 
    WHERE workflow_executions.site_id = sites.id 
    AND workflow_executions.workflow_type = 'dns'
);

-- Verify the migration
SELECT 'Migration 003 completed successfully' as result;