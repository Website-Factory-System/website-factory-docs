# PRD: Hosting Automator

## 1. Product overview
### 1.1 Document title and version
*   PRD: Hosting Automator
*   Version: 1.0

### 1.2 Product summary
This document specifies the requirements for the Hosting Automator script, a core backend module in the Website Factory system. Its primary responsibility is to programmatically provision the server-side environment for a new website after its DNS has been successfully configured. This involves creating a dedicated space for the website's files, securing it with an SSL certificate, and registering the site with the internal analytics platform.

The script operates on-demand, triggered by the Management Hub once a site's DNS status is marked as active. By automating these hosting setup tasks, the module eliminates manual server configuration, reduces setup time, and ensures a consistent, secure environment for every website deployed by the system.

## 2. Goals
### 2.1 Business goals
*   Automate the creation of hosting environments, further reducing the manual effort required per site.
*   Ensure every website is secured with SSL by default, improving security and SEO posture.
*   Standardize server configurations across the entire website portfolio.

### 2.2 User goals
*   As an operator, I want the system to automatically prepare the server space for my new website as soon as its DNS is ready.
*   As an operator, I want every new website to have analytics tracking set up automatically so I can monitor its performance from day one.

### 2.3 Non-goals
*   This script will not deploy any website files; it only prepares the empty directory structure.
*   This script will not manage server-level configurations like firewalls or package installations.
*   This script will not configure the CloudPanel or Matomo instances themselves; it assumes they are already installed and running.

## 3. User personas
### 3.1 Key user types
*   System (invoked by Management Hub)

### 3.2 Basic persona details
*   **System**: This is a non-interactive script executed by the Management Hub API as part of an automated workflow.

### 3.3 Role-based access
*   Not applicable. The script uses API keys from a secure configuration store.

## 4. Functional requirements
*   **Fetch Pending Sites** (Priority: High)
    *   The script must query the Supabase `sites` table for all records where `status_dns` is 'active' and `status_hosting` is 'pending'.
*   **Create Site in Hosting Panel** (Priority: High)
    *   The script must connect to the CloudPanel API.
    *   For each pending site, it must create a new "Static Site" environment.
    *   The process must include creating a dedicated system user and setting the document root.
*   **Provision SSL Certificate** (Priority: High)
    *   The script must trigger the provisioning of a free Let's Encrypt SSL certificate for the domain via the CloudPanel API.
*   **Create Analytics Tracking Site** (Priority: High)
    *   The script must connect to the self-hosted Matomo instance's Reporting API.
    *   It must create a new trackable website entity in Matomo for the domain.
*   **Update Status and Metadata** (Priority: High)
    *   Upon successful completion for a site, the script must update its `status_hosting` to 'active' in the Supabase `sites` table.
    *   It must also save the `hosting_doc_root` path and the `matomo_site_id` into the corresponding fields for that site's record.
    *   If an unrecoverable error occurs, it must update the status to 'failed' and log the error.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Resilience**: If the Matomo API call fails, it should be logged as a warning, but the overall hosting setup should not be marked as failed, as the core web hosting is functional.
*   **Idempotency**: If a site already exists in CloudPanel, the script should gracefully handle the error, check if the configuration is correct, and proceed without failing.

### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
Following the successful DNS setup for "new-site.com", the Management Hub triggers the Hosting Automator. The script wakes up and sees the site is ready for hosting. It connects to the CloudPanel server's API and instructs it to create a new static site environment for "new-site.com", complete with an SSL certificate. It notes the document root path `/home/newsit/htdocs/new-site.com`. Next, it calls the Matomo analytics server's API, creating a new tracking property and receiving back `matomo_site_id: 123`. Finally, it updates the central database record for "new-site.com" with the new status, document root path, and Matomo ID, then quietly shuts down, ready for the next task.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Percentage of hosting setups completed successfully without manual intervention. Target: > 99%.
*   Average time taken to provision a new hosting environment. Target: < 1 minute.

### 7.3. Technical metrics
*   API error rate for CloudPanel and Matomo APIs.
*   Script execution time.

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (to read/write site status and metadata).
*   CloudPanel API (via direct HTTP requests).
*   Matomo Reporting API (via direct HTTP requests).

### 8.2. Data storage & privacy
*   The script will handle API keys for CloudPanel and Matomo. These must be loaded from environment variables.

### 8.3. Scalability & performance
*   The script is stateless and can be run in parallel for different sites if necessary, though a sequential loop is sufficient for V1. API interactions are fast.

### 8.4. Potential challenges
*   CloudPanel may not have a fully comprehensive API for all actions, requiring workarounds or direct server commands if necessary.
*   Ensuring the domain's DNS has propagated enough for SSL certificate validation to succeed. CloudPanel's Let's Encrypt integration usually handles this retry logic.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Small: 2-4 days

### 9.2. Team size & composition
*   1 Backend Engineer

### 9.3. Suggested phases
*   **Phase 1**: Develop logic for CloudPanel site creation and SSL provisioning via API.
*   **Phase 2**: Add logic for Matomo site creation. Integrate with Supabase to process sites in a loop and update statuses.

## 10. User stories
*   **ID**: US-HOST-001
*   **Description**: As the system, I want to identify all sites that have completed DNS setup but are awaiting hosting provisioning.
*   **Acceptance criteria**:
    *   The script successfully queries the Supabase `sites` table for records where `status_dns` is 'active' and `status_hosting` is 'pending'.
    *   The script processes each returned site.
*   **ID**: US-HOST-002
*   **Description**: As the system, I want to create a secure, ready-to-use hosting space for a website.
*   **Acceptance criteria**:
    *   The script authenticates with the CloudPanel API.
    *   A new "Static Site" is successfully created in CloudPanel for the target domain.
    *   A Let's Encrypt SSL certificate is successfully provisioned for the domain.
    *   The script successfully retrieves the document root path for the new site.
*   **ID**: US-HOST-003
*   **Description**: As the system, I want to automatically register each new site with the analytics platform.
*   **Acceptance criteria**:
    *   The script authenticates with the Matomo Reporting API.
    *   A new trackable site is created in Matomo for the target domain.
    *   The script successfully retrieves the `idSite` for the newly created Matomo site.
*   **ID**: US-HOST-004
*   **Description**: As the system, I want to store the results and metadata of the hosting setup in the central database.
*   **Acceptance criteria**:
    *   Upon successful setup, the `status_hosting` field in the Supabase `sites` table is updated to 'active'.
    *   The `hosting_doc_root` and `matomo_site_id` fields are correctly populated with the retrieved values.
    *   If a critical error occurs (e.g., CloudPanel site creation fails), `status_hosting` is updated to 'failed' and an error message is logged.