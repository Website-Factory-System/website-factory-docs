# PRD: Website Factory System

## 1. Product overview

### 1.1 Document title and version

*   PRD: Website Factory System
*   Version: 1.0

### 1.2 Product summary

The Website Factory is an integrated software system designed to automate the creation, deployment, and monitoring of a large portfolio of static websites. Its primary purpose is to empower a single operator to efficiently manage hundreds of web properties by minimizing manual intervention in technical setup and routine management tasks. The system orchestrates a series of modular automation scripts and services through a central web-based dashboard, the Management Hub.

The core workflow begins with the operator providing basic domain information. The system then automates DNS configuration across a pool of managed Cloudflare accounts, provisions server space and SSL on a CloudPanel instance, and prepares analytics tracking. From the Management Hub, the operator can trigger an asynchronous content engine that uses AI to generate unique text and imagery, which is then stored in a central Headless CMS (Directus).

Once content is reviewed and approved within the CMS, a final deployment command triggers a build process using the Astro static site generator. This process creates highly optimized, static website files that are then deployed to the live server. Ongoing performance, including traffic from a self-hosted Matomo instance and search data from Google Search Console, is aggregated and displayed in the Management Hub, providing a centralized monitoring solution for the entire website portfolio.

## 2. Goals

### 2.1 Business goals

*   Drastically reduce the time and cost required to launch a new website, from days to minutes of active work.
*   Enable scalable management of a portfolio of 200+ websites by a single operator.
*   Increase operational efficiency by automating repetitive technical tasks (DNS, hosting, SSL, deployment).
*   Centralize performance monitoring to enable data-driven decisions on portfolio strategy.
*   Maintain a degree of DNS and structural diversity across sites to manage online footprint.

### 2.2 User goals

*   As an operator, I want to add new websites to the system through a simple UI, either one by one or in bulk via CSV.
*   As an operator, I want to assign new sites to pre-configured Cloudflare accounts to manage DNS setup.
*   As an operator, I want to trigger a complex, AI-driven content generation process with a single click.
*   As an operator, I want an easy way to review and optionally edit the generated content before it goes live.
*   As an operator, I want to deploy a fully built website to the live server with a single click.
*   As an operator, I want to view key performance metrics (traffic, search clicks/impressions) for all my websites in one consolidated dashboard.

### 2.3 Non-goals

*   This system will not automatically create Cloudflare or Google user accounts.
*   This system is not intended to build or manage complex, dynamic web applications (e.g., e-commerce stores with real-time inventory, social networks).
*   This system will not provide advanced, real-time collaborative editing features for content.
*   This system will not manage billing or subscriptions for any of the third-party services it uses.
*   This system will not perform advanced SEO actions like automated backlink generation or AI-driven keyword optimization strategies.

## 3. User personas

### 3.1 Key user types

*   System Operator

### 3.2 Basic persona details

*   **System Operator**: The primary and only user of the system. This individual is technically competent, responsible for managing the entire website portfolio, initiating automated workflows, and monitoring performance. They manage the initial setup of cloud services and credentials.

### 3.3 Role-based access

*   **System Operator**: Has full administrative access to all features within the Management Hub, the Directus CMS, the CloudPanel server, and other integrated services. There are no other user roles.

## 4. Functional requirements

*   **Centralized Site Management** (Priority: High)
    *   Ability to add a new site individually via a form.
    *   Ability to add multiple sites in bulk via a CSV file upload.
    *   A dashboard view listing all managed websites with their current statuses (DNS, Hosting, Content, Deployment).
    *   Ability to assign each new site to a pre-configured Cloudflare account.
*   **Automated Infrastructure Setup** (Priority: High)
    *   Automate DNS configuration by updating nameservers at the registrar (Namecheap) and creating records in the assigned Cloudflare account.
    *   Automate hosting environment creation on a CloudPanel server, including SSL certificate provisioning.
    *   Automate tracking site creation in a self-hosted Matomo analytics instance.
*   **Asynchronous Content & Deployment Workflows** (Priority: High)
    *   Trigger an AI-powered content generation process per site with a single button click.
    *   The system must provide visual feedback (e.g., progress indicators) for long-running tasks.
    *   Content must be saved to a Headless CMS (Directus) in a 'draft' state.
    *   Trigger a site build and deployment process with a single button click.
*   **Content Management Integration** (Priority: High)
    *   The system must provide a link to the Directus admin panel for content review and editing.
    *   The deployment process must only build content that has been marked as 'published' within the CMS.
*   **Centralized Analytics Dashboard** (Priority: Medium)
    *   Aggregate and display traffic data from Matomo for all sites.
    *   Aggregate and display search data (clicks, impressions) from Google Search Console for all sites.
    *   Provide filtering by date range (Today, Yesterday, Last 7/30 days, Custom).
    *   Provide sorting of sites by various performance metrics.
    *   Provide a detailed drill-down view for individual site performance.
*   **Secure Credential Management** (Priority: High)
    *   The system must provide a secure way to store and manage API keys and credentials for all integrated services.
    *   Credentials must not be hardcoded in the application source code.

## 5. User experience

### 5.1. Entry points & first-time user flow

*   The primary entry point is the login page for the Management Hub web application.
*   A first-time user (the operator after initial system setup) will need to configure the system by adding credentials for various services (Cloudflare accounts, Namecheap, Google, etc.) into the secure store (Supabase, likely via its UI or a dedicated settings page in the Hub).
*   The first core action is to add a new site via the "Add New Site" or "Bulk Create" feature on the "General" tab.

### 5.2. Core experience

*   **Add a new site**: The operator navigates to the "General" tab, clicks "Add New Site", fills in the domain and selects a Cloudflare account from a dropdown, and submits.
    *   The experience is fast and simple. The UI provides immediate feedback that the site has been added and background processes have started.
*   **Trigger workflows**: The operator scans the list of sites and clicks the "Generate" or "Deploy" button.
    *   The UI gives instant visual feedback that the asynchronous task has begun, changing the button to a status indicator.
*   **Review content**: The operator clicks a link in the site's action menu to open the Directus CMS in a new tab.
    *   The transition is seamless. The operator can easily find the site's content, use a familiar WYSIWYG editor, and publish changes.
*   **Monitor analytics**: The operator navigates to the "Analytics" tab.
    *   The dashboard loads quickly with a clear, high-level overview of portfolio performance. Data is easy to filter, sort, and understand at a glance.

### 5.3. Advanced features & edge cases

*   **Bulk Creation**: The operator can add hundreds of sites at once by preparing a CSV file with the required columns (`domain`, `cloudflare_account_nickname`) and uploading it. The system will process the entire batch.
*   **Re-generation and Re-deployment**: The operator can re-trigger the "Generate" and "Deploy" processes for any site at any time to update content or redeploy the site.
*   **Error Handling**: If an automated step fails (e.g., DNS verification fails), the status for that step will be updated to "Failed" in the UI with a potential error note, allowing the operator to investigate. The failure of one site's workflow will not stop the workflows of other sites.
*   **API Rate Limiting**: The system's automation scripts should have basic retry logic to handle transient API failures or rate limiting from external services.

### 5.4. UI/UX highlights

*   **Clarity and Focus**: The UI is designed to be clean and utilitarian, focusing on status clarity and ease of action. It uses `shadcn/ui` for a modern, consistent look and feel.
*   **Asynchronous Feedback**: The UI excels at providing feedback for background tasks, ensuring the operator is always aware of the system's state without needing to refresh the page constantly (polling or WebSockets).
*   **Data Density**: The analytics dashboard presents a high density of information in a digestible format, using sortable tables and clear data visualizations.

## 6. Narrative

Alex is a portfolio operator who wants to build and manage a large network of niche websites efficiently. The traditional process of setting up DNS, hosting, SSL, installing a CMS, creating content, and deploying for each site is prohibitively slow and expensive. Alex finds the Website Factory system, a centralized platform designed to solve this exact problem. Alex uses the Management Hub to add 50 new domains at once by uploading a simple CSV file, assigning them across the pre-configured Cloudflare accounts. With a few clicks, Alex watches as the system automatically sets up the entire technical infrastructure for all 50 sites. Next, Alex triggers the AI content engine for the batch, and later reviews the generated content in the integrated CMS. Finally, Alex triggers the deployment, and within an hour, 50 new, unique static websites are live. The next day, Alex logs into the analytics dashboard to see the initial performance data for the entire portfolio, all in one place.

## 7. Success metrics

### 7.1. User-centric metrics

*   Time to launch a single site (from adding the site in the Hub to successful deployment). Target: < 15 minutes of operator "wait time".
*   Number of clicks required to initiate key workflows (Add, Generate, Deploy). Target: <= 2 clicks per workflow.
*   Successful task completion rate (e.g., % of DNS setups that complete without error). Target: > 98%.

### 7.2. Business metrics

*   Total number of active websites managed by the system.
*   Rate of new website creation per week/month.
*   Aggregated performance of the entire website portfolio (total traffic, clicks, impressions).

### 7.3. Technical metrics

*   Average duration of the content generation process per site.
*   Average duration of the build & deploy process per site.
*   API error rate for all integrated external services.
*   Server resource utilization (CPU, memory) for the core services (Hub API, Directus, etc.).

## 8. Technical considerations

### 8.1. Integration points

*   **Supabase**: Central database for configuration, credentials, and site status.
*   **Namecheap API**: To manage domain nameservers.
*   **Cloudflare API**: To manage DNS zones and records across multiple accounts.
*   **CloudPanel API**: For initial site setup (if available/used).
*   **Directus API**: To programmatically write (content engine) and read (Astro build) content.
*   **AI APIs (OpenAI, Gemini, etc.)**: For text and image generation.
*   **Data Source APIs (Brave, Perplexity, etc.)**: For data collection.
*   **Matomo Reporting API**: To create tracking sites and fetch analytics data.
*   **Google Search Console API & Site Verification API**: To verify sites and fetch search data.
*   **SSH/rsync**: For file deployment to the hosting server.

### 8.1.1. Deployment Architecture

*   **Railway Cloud (Control Plane)**: Hosts Management Hub API/UI, all automation scripts (DNS, Hosting, Content, Deployment, Analytics), and Matomo analytics. These run as separate Railway services triggered by the API.
*   **Vultr Server (Data Plane)**: Dedicated to serving websites - runs CloudPanel for web hosting, Directus CMS for content management, and Astro for static site generation. Hosts the actual 200+ static websites.

### 8.2. Data storage & privacy

*   All sensitive credentials (API keys, tokens) must be stored securely in Supabase and accessed via environment variables in the application modules, never hardcoded.
*   The system will process publicly available brand and product data. No sensitive personal user data (beyond the operator's login) will be stored.
*   Regular backups of the Supabase and Directus databases are critical.

### 8.3. Scalability & performance

*   The system is designed to be modular. The automation scripts are stateless and run on-demand, which scales well.
*   The primary scaling consideration is the load on the long-running services: Directus, the Management Hub API, and the Matomo instance. These will be hosted on a Vultr server that can be vertically scaled (more CPU/RAM) as needed.
*   The use of a static site generator (Astro) ensures that the deployed websites themselves are extremely performant and can handle high traffic with minimal server resources.
*   Asynchronous task handling (via Celery or FastAPI BackgroundTasks) is crucial to prevent the API from being blocked by long-running jobs.

### 8.4. Potential challenges

*   **API Changes**: Heavy reliance on third-party APIs means changes or deprecations by those services can break parts of the workflow.
*   **AI Content Quality**: The quality and uniqueness of the AI-generated content are critical for the websites' success and require significant prompt engineering and a robust data collection strategy.
*   **Error Handling Complexity**: Handling failures across a distributed, multi-step automated workflow is complex. The system needs robust logging and status tracking.
*   **Initial Setup**: The initial manual setup of all accounts and credentials is a significant upfront effort.

## 9. Milestones & sequencing

### 9.1. Project estimate

*   Large: 8-12 weeks

### 9.2. Team size & composition

*   Medium Team: 3-5 total people
    *   1 Product Manager/Lead
    *   1-2 Backend Engineers (Python, APIs, Automation Scripts)
    *   1 Frontend Engineer (React, UI/UX)
    *   1 DevOps/Sysadmin (Server setup, Docker, CI/CD)

### 9.3. Suggested phases

*   **Phase 1: Foundation & Infrastructure (2-3 weeks)**
    *   Key deliverables: Vultr server setup with CloudPanel, Directus, Matomo. Supabase database schema design. Develop and test `dns-automator` and `hosting-automator` scripts. Secure credential management strategy finalized.
*   **Phase 2: Core Application & Content Workflow (3-4 weeks)**
    *   Key deliverables: Management Hub API backend (FastAPI) with core endpoints for site management. Management Hub UI (React) with basic dashboard and workflow triggers. Initial version of the `content-engine` to populate Directus. Initial version of `deployment-scripts` to build (Astro) and deploy (rsync).
*   **Phase 3: Analytics & Integration (2-3 weeks)**
    *   Key deliverables: Develop `analytics-aggregator` script. Build out the Analytics tab in the Management Hub UI. Refine all workflows, implement robust error handling and logging across all modules. GSC verification automation.
*   **Phase 4: Beta Testing & Hardening (1-2 weeks)**
    *   Key deliverables: End-to-end testing with a batch of 10-20 sites. Bug fixing, performance tuning, and documentation refinement.

## 10. User stories

### 10.1. Operator Authentication

*   **ID**: US-001
*   **Description**: As an operator, I want to log into the Management Hub with a secure username and password so that only I can access the system.
*   **Acceptance criteria**:
    *   A login page exists.
    *   Submitting valid credentials grants access to the dashboard.
    *   Submitting invalid credentials shows an error message.
    *   Access to any other page requires a valid, authenticated session.

### 10.2. Add a Single Site

*   **ID**: US-002
*   **Description**: As an operator, I want to add a single new website to the system through a simple form.
*   **Acceptance criteria**:
    *   A button "Add New Site" is visible on the General tab.
    *   Clicking the button opens a form (e.g., a modal dialog).
    *   The form contains fields for "Domain Name" and a mandatory dropdown for "Cloudflare Account".
    *   The "Cloudflare Account" dropdown is populated with the nicknames of accounts from the Supabase database.
    *   Submitting the form creates a new site record in the Supabase `sites` table with the correct `cloudflare_account_id` and pending statuses.
    *   The site list on the dashboard updates to show the new site.

### 10.3. Bulk Add Sites via CSV

*   **ID**: US-003
*   **Description**: As an operator, I want to add multiple new websites at once by uploading a CSV file.
*   **Acceptance criteria**:
    *   A button "Bulk Create" is visible on the General tab.
    *   Clicking the button opens a file upload interface.
    *   The interface provides instructions on the required CSV format (columns: `domain`, `cloudflare_account_nickname`).
    *   Upon successful upload, the system parses the CSV and creates a record for each valid row in the Supabase `sites` table.
    *   The system validates that the `cloudflare_account_nickname` exists for each row.
    *   Rows with invalid data are reported back to the user with an error message.
    *   The site list on the dashboard updates to show all newly created sites.

### 10.4. View Site List and Statuses

*   **ID**: US-004
*   **Description**: As an operator, I want to see a list of all my managed websites and their current workflow statuses so I know what needs attention.
*   **Acceptance criteria**:
    *   The General tab displays a table of all sites.
    *   The table includes columns for Brand/Domain Name, DNS Status, Hosting Status, Content Status, and Deployment Status.
    *   The status fields update automatically as background tasks complete.

### 10.5. Trigger Content Generation

*   **ID**: US-005
*   **Description**: As an operator, I want to start the AI content generation process for a specific site with a single click.
*   **Acceptance criteria**:
    *   Each site row in the General tab has a "Generate" button when content status is 'pending'.
    *   Clicking the button sends a request to the backend to start the asynchronous `content-engine` task for that site.
    *   The button's appearance immediately changes to a progress indicator (e.g., "Generating...").
    *   When the task is complete, the indicator updates to "Done" or "Failed".

### 10.6. Trigger Site Deployment

*   **ID**: US-006
*   **Description**: As an operator, I want to deploy a website to the live server with a single click.
*   **Acceptance criteria**:
    *   Each site row has a "Deploy" button when content is generated.
    *   Clicking the button sends a request to the backend to start the asynchronous build & deploy task for that site.
    *   The button's appearance immediately changes to a progress indicator (e.g., "Deploying...").
    *   When the task is complete, the indicator updates to "Deployed" or "Failed".

### 10.7. Review Content in CMS

*   **ID**: US-007
*   **Description**: As an operator, I want a direct link to the content for a specific site in the Directus CMS so I can easily review and edit it.
*   **Acceptance criteria**:
    *   Each site row has an action menu (e.g., three-dots icon).
    *   The menu contains an option "View in CMS".
    *   Clicking the option opens the Directus admin panel in a new tab, ideally navigating to the content items for that specific site.

### 10.8. View Aggregated Analytics Dashboard

*   **ID**: US-008
*   **Description**: As an operator, I want to see a high-level overview of performance across my entire portfolio.
*   **Acceptance criteria**:
    *   An "Analytics" tab is available in the main navigation.
    *   The tab displays a table of all sites with columns for Brand/Domain, Matomo Visits, GSC Clicks, and GSC Impressions.
    *   Overview widgets display the sum of these metrics for the selected period.
    *   The table data is sortable by each metric column.

### 10.9. Filter Analytics by Date

*   **ID**: US-009
*   **Description**: As an operator, I want to filter the analytics data by different time periods to understand performance trends.
*   **Acceptance criteria**:
    *   The Analytics tab includes date filtering options (e.g., buttons or a dropdown).
    *   Options include "Today", "Yesterday", "Last 7 Days", "Last 30 Days", and "Custom Range".
    *   Selecting a date range updates the data in both the overview widgets and the main table.

### 10.10. View Detailed Site Analytics

*   **ID**: US-010
*   **Description**: As an operator, I want to drill down into the performance of a single website to see more detailed metrics.
*   **Acceptance criteria**:
    *   Clicking on a site row in the Analytics table navigates to a new page dedicated to that site's analytics.
    *   This page displays historical data charts for key metrics (e.g., line chart for visits over time).
    *   It shows more detailed data from both Matomo and Google Search Console.

### 10.11. Handle Asynchronous Task Failure

*   **ID**: US-011
*   **Description**: As an operator, if an automated process fails, I want to see a clear failure status in the dashboard so I can investigate.
*   **Acceptance criteria**:
    *   If a background task (DNS, Hosting, Content, Deploy) fails, the corresponding status in the site list table updates to "Failed".
    *   Hovering over the "Failed" status or clicking it might reveal a brief error message.
    *   The failure of one site's task does not prevent other sites' tasks from running.
