# Status Page Documentation

## Overview
The Status page is a real-time workflow monitoring system that provides detailed visibility into the execution of automation workflows for each website in the Website Factory system.

## Architecture

### Backend Components

1. **StatusService** (`/management-hub-api/app/services/status_service.py`)
   - Manages workflow status tracking in the database
   - Provides phase and step-level status updates
   - Tracks timing information and error messages

2. **Status API Endpoints** (`/management-hub-api/app/api/status.py`)
   - `GET /status/{site_id}` - Get detailed status for a specific site
   - `GET /status/queue` - Get all sites currently being processed
   - `GET /status/recent` - Get recently completed sites
   - `POST /status/{site_id}/clear` - Clear status data for a site

3. **Database Tables**
   - `workflow_status` - Tracks current workflow phase and overall status
   - `workflow_steps` - Detailed step-by-step execution logs

### Frontend Components

1. **StatusPage Component** (`/management-hub-ui/src/pages/StatusPage.tsx`)
   - Main page component with three sections:
     - Processing Queue (active workflows)
     - Recently Completed
     - All Sites

2. **Key Features**
   - Real-time updates via polling (every 2 seconds for active sites)
   - Time elapsed tracking for running workflows
   - Expandable details showing individual workflow steps
   - Error message display
   - Quick action buttons for retry/view

3. **Status Display Components**
   - `StatusBadge` - Visual status indicators
   - `TimeElapsed` - Real-time elapsed time counter
   - `WorkflowPhases` - Detailed phase and step breakdown

## Workflow Integration

### How Workflows Update Status

1. **Phase Start**
   ```python
   await self.status_service.start_phase(site_id, "dns_setup")
   ```

2. **Step Updates**
   ```python
   await self.status_service.update_workflow_step(
       site_id, "dns_setup", "Creating Cloudflare Zone",
       "Setting up DNS records...", "running"
   )
   ```

3. **Phase Completion**
   ```python
   await self.status_service.complete_phase(site_id, "dns_setup")
   ```

4. **Error Handling**
   ```python
   await self.status_service.fail_phase(site_id, "dns_setup", error_message)
   ```

## Current Issues & Debugging

### 1. Workflows Not Triggering

**Issue**: After creating a site, workflows remain in "pending" status and don't execute.

**Root Cause**: The background tasks are being added to FastAPI's BackgroundTasks, but they may not be executing due to:
- Missing environment variables (`DNS_AUTOMATOR_URL`, `HOSTING_AUTOMATOR_URL`)
- Background task execution issues in the Railway deployment
- Async execution context problems

**Debug Steps**:
1. Check Railway logs for the Management Hub API:
   ```bash
   railway logs -s management-hub-api
   ```

2. Look for these log messages:
   - "Created site {domain} with ID {id}"
   - "Adding DNS setup task for site {id}"
   - "Executing DNS setup for site {id}"

3. Verify environment variables are set in Railway:
   - `DNS_AUTOMATOR_URL=http://dns-automator.railway.internal`
   - `HOSTING_AUTOMATOR_URL=http://hosting-automator.railway.internal`

### 2. Status Page Not Updating

**Issue**: The Status page shows sites but doesn't display workflow progress.

**Root Cause**: The workflow execution isn't creating status records in the database.

**Solution**: The workflow needs to actually execute for status updates to appear. Once the background task issue is resolved, status updates will flow automatically.

## Testing Workflow Execution

Use the provided test script to debug workflow execution:

```bash
python test_workflow_debug.py
```

This script will:
1. Login to the API
2. Create a test site
3. Monitor the site status for 2 minutes
4. Display all workflow phases and steps

## Railway Deployment Configuration

### Required Environment Variables

For Management Hub API:
```
SUPABASE_URL=<your-supabase-url>
SUPABASE_SERVICE_KEY=<your-service-key>
JWT_SECRET_KEY=<your-jwt-secret>
DNS_AUTOMATOR_URL=http://dns-automator.railway.internal
HOSTING_AUTOMATOR_URL=http://hosting-automator.railway.internal
```

### Service Communication

The services communicate via Railway's private networking:
- Management Hub API → DNS Automator (via internal URL)
- Management Hub API → Hosting Automator (via internal URL)

## Next Steps for Resolution

1. **Add Missing Environment Variables**
   - Go to Railway dashboard
   - Navigate to Management Hub API service
   - Add `DNS_AUTOMATOR_URL` and `HOSTING_AUTOMATOR_URL`
   - Redeploy the service

2. **Verify Background Task Execution**
   - Check if the DNS Automator is receiving requests
   - Monitor Railway logs for both services
   - Use the test script to create a site and watch logs

3. **Alternative Solution if Background Tasks Don't Work**
   - Consider using Celery for task queue management
   - Or implement a simple polling mechanism that processes pending sites

## Code References

- Background task creation: `/management-hub-api/app/api/sites.py:37`
- Workflow execution: `/management-hub-api/app/services/workflow_service.py:23`
- Status updates: `/management-hub-api/app/services/status_service.py`
- Status page UI: `/management-hub-ui/src/pages/StatusPage.tsx`