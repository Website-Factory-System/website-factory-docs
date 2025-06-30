# PRD: Hosting Automator

## 1. Product overview
### 1.1 Document title and version
*   PRD: Hosting Automator
*   Version: 1.0

### 1.2 Product summary
This document specifies the requirements for the Hosting Automator script, a core backend module in the Website Factory system. Its primary responsibility is to programmatically provision the server-side environment for a new website after its DNS has been successfully configured. This involves creating a dedicated space for the website's files, securing it with an SSL certificate, and registering the site with the internal analytics platform.

The script operates on-demand, triggered by the Management Hub once a site's DNS status is marked as active. It automates these tasks by executing commands on the CloudPanel Command-Line Interface (CLI) over a secure SSH connection. By doing so, it eliminates manual server configuration, reduces setup time, and ensures a consistent, secure environment for every website deployed by the system.

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
*   Not applicable. The script uses an SSH key and API tokens from a secure configuration.
## 4. Functional requirements
*   **Fetch Pending Sites** (Priority: High)
    *   The script must query the Supabase `sites` table for all records where `status_dns` is 'active' and `status_hosting` is 'pending'.
**Create Site via CLI** (Priority: High)
    *   The script must establish a secure SSH connection to the hosting server.
    *   For each pending site, it must execute the `clpctl site:add:static` command with the appropriate domain name and user parameters.
*   **Provision SSL Certificate via CLI** (Priority: High)
    *   The script must execute the `clpctl ssl:add:lets-encrypt` command for the domain.
*   **Provision SSL Certificate** (Priority: High)
    *   The script must trigger the provisioning of a free Let's Encrypt SSL certificate for the domain via the CloudPanel API.
*   **Create Analytics Tracking Site** (Priority: High)
    *   The script must connect to the self-hosted Matomo instance's Reporting API.
    *   It must create a new trackable website entity in Matomo for the domain.
*   **Update Status and Metadata** (Priority: High)
    *   Upon successful completion for a site, the script must update its `status_hosting` to 'active' in the Supabase `sites` table.
    *   It must also save the inferred `hosting_doc_root` path and the `matomo_site_id` into the corresponding fields for that site's record.
    *   If an unrecoverable error occurs, it must update the status to 'failed' and log the error.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Resilience**: If the Matomo API call fails, it should be logged as a warning, but the overall hosting setup should not be marked as failed, as the core web hosting is functional.
*   **Idempotency**: If a site already exists in CloudPanel, the corresponding `clpctl` command will fail. The script should catch this specific error, log it as a warning, and proceed as if successful, assuming a previous run was interrupted.
### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
Following the successful DNS setup for "new-site.com", the Management Hub triggers the Hosting Automator. The script wakes up and establishes a secure SSH connection to the Vultr server. It then remotely executes a series of `clpctl` commands: first to create a new user, then to add "new-site.com" as a static site under that user, and finally to provision its SSL certificate. It notes the standard document root path. Disconnecting from SSH, it then calls the Matomo analytics server's API, creating a new tracking property. Finally, it updates the central database record for "new-site.com" with the new status, document root path, and Matomo ID, then quietly shuts down.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Percentage of hosting setups completed successfully without manual intervention. Target: > 99%.
*   Average time taken to provision a new hosting environment. Target: < 1 minute.

### 7.3. Technical metrics
*   CLI command success rate.
*   API error rate for Matomo APIs.
*   Script execution time.

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (to read/write site status and metadata).
*   CloudPanel CLI (via a secure SSH connection).
*   Matomo Reporting API (via direct HTTP requests).

### 8.2. Data storage & privacy
*   The script will handle the SSH private key for server access and the API key for Matomo. These must be loaded from environment variables.

### 8.3. Scalability & performance
*   The script is stateless and can be run in parallel for different sites if necessary, though a sequential loop is sufficient for V1. API interactions are fast.

### 8.4. Potential challenges
*   **CLI Automation Fragility**: Automating via CLI is more brittle than a stable REST API. Updates to CloudPanel could change command syntax or output format and break the script. This is the primary risk.
*   **SSH Key Management**: Securely managing the SSH key required for root/sudo access to the production server is critical.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Small: 2-4 days

### 9.2. Team size & composition
*   1 Backend Engineer

### 9.3. Suggested phases
*   **Phase 1**: Develop SSH connection logic using `paramiko`. Implement the functions to execute the `clpctl` commands for site and SSL creation.
*   **Phase 2**: Add logic for Matomo site creation via its API.
*   **Phase 3**: Integrate with Supabase to process sites in a loop and update statuses. Add robust error handling for failed SSH commands.

## 10. User stories
*   **ID**: US-HOST-001
*   **Description**: As the system, I want to identify all sites that have completed DNS setup but are awaiting hosting provisioning.
*   **Acceptance criteria**:
    *   The script successfully queries the Supabase `sites` table for records where `status_dns` is 'active' and `status_hosting` is 'pending'.
    *   The script processes each returned site.
*   **ID**: US-HOST-002
*   **Description**: As the system, I want to create a secure, ready-to-use hosting space for a website by executing remote CLI commands.
*   **Acceptance criteria**:
    *   The script establishes an SSH connection to the hosting server.
    *   The `clpctl site:add:static` command is executed successfully with the correct parameters for the target domain.
    *   The `clpctl ssl:add:lets-encrypt` command is executed successfully for the target domain.
    *   The script can correctly infer the document root path based on the creation parameters.
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
    *   If a critical CLI command fails, `status_hosting` is updated to 'failed' and an error message is logged.
