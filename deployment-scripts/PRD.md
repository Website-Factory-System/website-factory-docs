# PRD: Deployment Scripts

## 1. Product overview
### 1.1 Document title and version
*   PRD: Deployment Scripts
*   Version: 1.0

### 1.2 Product summary
This document defines the requirements for the Deployment Scripts module. This module is the final step in the automated workflow, responsible for transforming the content stored in the Headless CMS into a live, publicly accessible website. It is a critical, on-demand service triggered by the Management Hub.

The process is twofold. First, the "Build" stage uses the Astro static site generator to fetch published content from the Directus CMS and combine it with design templates to create a set of highly optimized, static files (HTML, CSS, JS). Second, the "Deploy" stage securely transfers these built files to the correct directory on the production hosting server (CloudPanel), making the website live. This module ensures that deployments are fast, reliable, and consistent across the entire portfolio.

## 2. Goals
### 2.1 Business goals
*   Automate the final "go-live" step of website creation, eliminating manual file uploads.
*   Ensure every deployed website is a high-performance static site.
*   Enable near-instantaneous updates to live sites when content is changed in the CMS.

### 2.2 User goals
*   As an operator, I want to deploy a fully prepared website with a single click of a "Deploy" button.
*   As an operator, I want to be confident that what I see in the CMS as "published" is exactly what will appear on the live site.
*   As an operator, I want site updates to appear online within seconds of me triggering a deployment.

### 2.3 Non-goals
*   This module will not edit or generate content; it only reads it from the CMS.
*   This module will not provision the server; it assumes the target directory already exists.
*   This module will not run its own web server; it only produces files for another server (Nginx/CloudPanel) to handle.

## 3. User personas
### 3.1 Key user types
*   System (invoked by Management Hub)

### 3.2 Basic persona details
*   **System**: A non-interactive script executed asynchronously by the Management Hub API.

### 3.3 Role-based access
*   Not applicable. The script uses SSH keys and API tokens from a secure configuration.

## 4. Functional requirements
*   **Fetch Site Data** (Priority: High)
    *   The script must accept a `site_id` as input.
    *   It must query the Supabase `sites` table to retrieve the site's `domain` and its specific `hosting_doc_root` path.
*   **Build Static Site** (Priority: High)
    *   The script must execute the Astro build process.
    *   The Astro project must be configured to fetch content for the specific `domain` from the Directus API.
    *   The Astro build must only fetch content items marked with a `status` of 'published'.
    *   The Astro build must dynamically inject the site-specific Matomo tracking code (`matomo_site_id` from Supabase) into the final HTML.
    *   The build output must be directed to a temporary, clean directory.
*   **Deploy Files to Server** (Priority: High)
    *   The script must use `rsync` over SSH to transfer the contents of the temporary build directory.
    *   The destination for the transfer must be the `hosting_doc_root` on the production server.
    *   The transfer must delete any files in the destination that are not present in the source (ensuring a clean deployment).
*   **Perform Post-Deploy Verification** (Priority: Medium)
    *   After deployment, the script must trigger the GSC site verification process.
    *   The script should perform a basic HTTP check on the live domain to ensure it returns a 200 OK status.
*   **Update Status** (Priority: High)
    *   The script must update the `status_deployment` field in Supabase to 'deploying', 'deployed', or 'failed' throughout its lifecycle.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Build Caching**: The Astro build process should be configured to leverage caching where possible to speed up subsequent builds.
*   **Delta Sync**: `rsync` inherently only transfers changed files, making the deployment step very efficient for minor content updates.

### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
The operator, having approved the content for "new-site.com" in Directus, clicks "Deploy" in the Management Hub. This activates the Deployment Scripts module. First, the script tells the Astro build tool to wake up. Astro calls the Directus API, gets all the published content and images for "new-site.com", and combines them with the site's design templates. Within seconds, a complete, optimized static website is built in a temporary folder. Immediately after, the script initiates a secure `rsync` connection to the Vultr server and syncs this folder with the live website directory. Finally, it performs a quick check to see if the site is online and tells Google to verify it. It then reports "Deployed" back to the Management Hub.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Average time from "Deploy" click to the site being live. Target: < 30 seconds.

### 7.3. Technical metrics
*   Astro build time per site.
*   `rsync` transfer time per site.
*   Deployment success rate. Target: > 99.5%.

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (to read site metadata).
*   Directus CMS API (read-only, used by the Astro build process).
*   Astro CLI (executed as a subprocess).
*   `rsync` and `ssh` system commands.
*   Google Site Verification API.

### 8.2. Data storage & privacy
*   Handles SSH private key for server access. This key must be stored securely on the machine running the script, with strict file permissions, and its path loaded from an environment variable.

### 8.3. Scalability & performance
*   Astro build times are a key performance metric. Keeping the Astro project and templates optimized is important.
*   The script is on-demand. If many deployments are triggered at once, a task queue (Celery) would be beneficial to process them sequentially or in parallel up to a certain limit.

### 8.4. Potential challenges
*   SSH key management and ensuring the correct keys are used for server access.
*   The machine running the script must have Node.js and the Astro project dependencies installed. This is a good use case for a dedicated Docker build image.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Small: 4-6 days

### 9.2. Team size & composition
*   1 Backend/DevOps Engineer

### 9.3. Suggested phases
*   **Phase 1**: Create the Astro project template with placeholder data fetching.
*   **Phase 2**: Develop the Python script to orchestrate the Astro build and `rsync` deploy for a hardcoded site.
*   **Phase 3**: Integrate with Supabase to make the script dynamic, fetching `site_id` and metadata. Add status updates and error handling.

## 10. User stories
*   **ID**: US-DEP-001
*   **Description**: As the system, I want to build a static website using the latest published content from the CMS.
*   **Acceptance criteria**:
    *   The script successfully triggers the `astro build` command.
    *   The Astro build process authenticates with the Directus API.
    *   The build fetches content only where `status` is 'published' for the specified site.
    *   The correct `matomo_site_id` is injected into the HTML templates.
    *   The build completes without errors and outputs files to a designated directory.
*   **ID**: US-DEP-002
*   **Description**: As the system, I want to securely transfer the built website files to the live production server.
*   **Acceptance criteria**:
    *   The script uses `rsync` over `ssh` for the file transfer.
    *   Authentication is performed using a pre-configured SSH key.
    *   Files are transferred to the correct `hosting_doc_root` for the site.
    *   The `--delete` flag is used to ensure the destination directory perfectly mirrors the source build directory.
*   **ID**: US-DEP-003
*   **Description**: As the system, I want to verify the deployment and report the final status.
*   **Acceptance criteria**:
    *   The script initiates Google Site Verification for the domain.
    *   The script performs an HTTP GET request to the live domain and expects a 200 status code.
    *   The script updates the `status_deployment` in Supabase to 'deployed' on success or 'failed' on error.