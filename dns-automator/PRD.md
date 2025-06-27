# PRD: DNS Automator

## 1. Product overview
### 1.1 Document title and version
*   PRD: DNS Automator
*   Version: 1.0

### 1.2 Product summary
This document outlines the requirements for the DNS Automator script. This is a backend module within the Website Factory system responsible for programmatically configuring all necessary DNS settings for a new website. It acts as a bridge between the central system database (Supabase), the domain registrar (Namecheap), and the designated DNS service provider (Cloudflare). Its purpose is to completely eliminate the manual, error-prone process of setting up DNS for each new domain, ensuring consistency and speed.

The script is designed to be executed on-demand, triggered by the Management Hub. It identifies pending sites, retrieves the specific Cloudflare account assigned to each, and uses the corresponding API credentials to perform its tasks. This includes updating nameservers at the registrar and creating the necessary zone and records in Cloudflare to point the domain to the project's hosting server.

## 2. Goals
### 2.1 Business goals
*   Eliminate manual DNS configuration time and associated labor costs.
*   Reduce human error in DNS setup, ensuring new sites resolve correctly on the first attempt.
*   Enforce a consistent, programmatic DNS setup process across the entire portfolio.

### 2.2 User goals
*   As an operator, I want the system to automatically handle all DNS changes for a new site after I add it to the Management Hub.
*   As an operator, I want the DNS to be configured within the specific Cloudflare account I assigned to the site.

### 2.3 Non-goals
*   This script will not create Cloudflare accounts.
*   This script will not purchase domains from Namecheap.
*   This script will not manage complex DNS records like DKIM, DMARC, or SPF; it will only handle records essential for pointing the site and future verification.

## 3. User personas
### 3.1 Key user types
*   System (invoked by Management Hub)

### 3.2 Basic persona details
*   **System**: This script is not user-facing. It is executed by the Management Hub API backend in response to a workflow trigger.

### 3.3 Role-based access
*   Not applicable. The script uses API keys stored securely to access required services.

## 4. Functional requirements
*   **Fetch Pending Sites** (Priority: High)
    *   The script must query the Supabase `sites` table to retrieve a list of all sites with a `status_dns` of 'pending'.
*   **Use Assigned Cloudflare Account** (Priority: High)
    *   For each pending site, the script must retrieve the assigned `cloudflare_account_id`.
    *   It must then query the `cloudflare_accounts` table to get the specific API token for that account.
*   **Update Registrar Nameservers** (Priority: High)
    *   The script must connect to the Namecheap API.
    *   It must update the nameservers for the domain to the standard Cloudflare nameservers.
*   **Configure Cloudflare Zone** (Priority: High)
    *   The script must connect to the Cloudflare API using the specific account token.
    *   It must create a new zone for the domain in that Cloudflare account.
    *   It must create an 'A' record pointing to the main hosting server IP.
    *   It must create a 'CNAME' record for 'www' pointing to the root domain.
*   **Update Status** (Priority: High)
    *   Upon successful completion for a site, the script must update its `status_dns` to 'active' in the Supabase `sites` table.
    *   If an unrecoverable error occurs, it must update the status to 'failed' and log the error message.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable. This is a non-interactive script.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Idempotency**: If the script is run again on a site that is already partially configured (e.g., the zone exists but records are missing), it should handle this gracefully by checking for existing resources before attempting to create them.
*   **Error Logging**: The script must log detailed errors, including the domain being processed and the specific API error message received, to a log file for debugging.

### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
The Management Hub identifies that "new-site.com" has been added and needs its DNS configured. It triggers the DNS Automator script. The script wakes up, sees "new-site.com" in its pending queue, and finds it's assigned to "CF_Batch_4". It fetches the unique API token for "CF_Batch_4" and the Namecheap API key. First, it tells Namecheap to use Cloudflare's nameservers. Then, it logs into the "CF_Batch_4" Cloudflare account via API and creates the "new-site.com" zone, adding the necessary records to point it to the Vultr server. Finally, it reports back to the central database, marking the site's DNS as "active" before shutting down.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Percentage of DNS setups completed successfully without manual intervention. Target: > 99%.
*   Average time taken to fully configure DNS for one site. Target: < 2 minutes.

### 7.3. Technical metrics
*   API error rate when connecting to Namecheap and Cloudflare.
*   Script execution time.

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (to read site data and account credentials, and write status updates).
*   Namecheap API.
*   Cloudflare API.

### 8.2. Data storage & privacy
*   The script will handle sensitive API keys for Namecheap and Cloudflare. These must be loaded from environment variables and never logged.

### 8.3. Scalability & performance
*   The script is stateless and processes sites sequentially. Performance can be improved with parallel processing if the number of sites added at once becomes very large, but this is not required for V1.

### 8.4. Potential challenges
*   DNS propagation delays can affect timing, although this is less of an issue as the script's next steps are not dependent on public resolution.
*   Handling API-specific error codes and rate limits from both Namecheap and Cloudflare.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Small: 3-5 days

### 9.2. Team size & composition
*   1 Backend Engineer

### 9.3. Suggested phases
*   **Phase 1**: Develop core logic for Namecheap NS updates and Cloudflare zone/record creation for a single site.
*   **Phase 2**: Integrate with Supabase to fetch pending sites and update statuses in a loop. Implement robust logging and error handling.

## 10. User stories
*   **ID**: US-DNS-001
*   **Description**: As the system, I want to process all sites pending DNS setup so that their infrastructure can be provisioned.
*   **Acceptance criteria**:
    *   The script successfully queries the Supabase `sites` table for records where `status_dns` is 'pending'.
    *   The script processes each returned site one by one.
    *   If no sites are pending, the script exits cleanly.
*   **ID**: US-DNS-002
*   **Description**: As the system, I want to update a domain's nameservers at the registrar to point to Cloudflare.
*   **Acceptance criteria**:
    *   The script authenticates with the Namecheap API using credentials from environment variables.
    *   The script successfully calls the appropriate Namecheap API endpoint to change the nameservers for the target domain.
    *   The script logs the success or failure of the API call.
*   **ID**: US-DNS-003
*   **Description**: As the system, I want to create and configure a DNS zone in the specific Cloudflare account assigned to the site.
*   **Acceptance criteria**:
    *   The script fetches the `api_token` for the site's assigned `cloudflare_account_id` from Supabase.
    *   The script authenticates with the Cloudflare API using that specific token.
    *   A new zone for the domain is successfully created in the correct account.
    *   An 'A' record pointing to the production server IP is created.
    *   A 'CNAME' record for 'www' pointing to the root domain is created.
*   **ID**: US-DNS-004
*   **Description**: As the system, I want to report the outcome of the DNS setup process back to the central database.
*   **Acceptance criteria**:
    *   If all steps for a domain complete successfully, its `status_dns` field in the Supabase `sites` table is updated to 'active'.
    *   If any unrecoverable error occurs, the `status_dns` field is updated to 'failed'.
    *   The `error_message` field is populated with a relevant error if the process failed.