# Website Factory Development Plan

## Overview
The Website Factory is an integrated software system designed to automate the creation, deployment, and monitoring of a large portfolio of static websites. It empowers a single operator to efficiently manage hundreds of web properties by orchestrating a series of modular automation scripts and services through a central web-based dashboard, the Management Hub.

## 1. Project Setup
- [ ] **Infrastructure Provisioning**
    - [ ] Provision Vultr cloud server instance for hosting core services.
    - [ ] Perform initial server setup: install OS updates, configure firewall (UFW), set up user accounts.
    - [ ] Install Docker and Docker Compose on the Vultr server.
- [ ] **Repository Setup**
    - [ ] Create a new GitHub organization or project group for "Website Factory".
    - [ ] Create Git repositories for all 7 modules:
        - [ ] `management-hub-api`
        - [ ] `management-hub-ui`
        - [ ] `dns-automator`
        - [ ] `hosting-automator`
        - [ ] `content-engine`
        - [ ] `deployment-scripts`
        - [ ] `analytics-aggregator`
    - [ ] Initialize each repository with a standard `.gitignore`, `README.md`, and license file.
    - [ ] Configure branch protection rules for `main` branches.
- [ ] **Database & Services Setup**
    - [ ] Create a new Supabase project to serve as the central database.
    - [ ] Secure and store Supabase project URL and API keys (`anon` and `service_role`).
    - [ ] Set up a self-hosted Directus instance on the Vultr server using Docker.
    - [ ] Set up a self-hosted Matomo instance on the Vultr server using Docker.
    - [ ] Set up CloudPanel on the Vultr server.
- [ ] **Development Environment Configuration**
    - [ ] Create a `docker-compose.yml` file in the project root to manage local development services (PostgreSQL, Redis if using Celery).
    - [ ] Create `.env.example` files for each service, documenting all required environment variables.
    - [ ] Write a developer setup guide (`CONTRIBUTING.md`) covering repository cloning, environment setup, and running services locally.

## 2. Backend Foundation (`management-hub-api`)
- [ ] **Project Scaffolding**
    - [ ] Initialize a new Python project with FastAPI and Uvicorn.
    - [ ] Set up project structure: `app/api`, `app/core`, `app/db`, `app/schemas`, `app/services`, `app/tasks`.
    - [ ] Configure settings management using Pydantic's `BaseSettings` to load from environment variables.
- [ ] **Database Integration & Models**
    - [ ] Implement Supabase client initialization and session management.
    - [ ] Define database table schemas in a migration tool (e.g., Alembic) or as SQL scripts based on the TDD.
        - [ ] `cloudflare_accounts` table
        - [ ] `gsc_accounts` table
        - [ ] `sites` table
        - [ ] `daily_analytics` table
        - [ ] `brand_data` table (for `content-engine`)
    - [ ] Apply initial migrations to the Supabase database.
    - [ ] Create Directus collections mirroring the required content structure (`pages`, `page_sections`, linked to `sites`).
- [ ] **Authentication System**
    - [ ] Implement password hashing using `passlib[bcrypt]`.
    - [ ] Create `/auth/token` endpoint for user login, returning a JWT.
    - [ ] Implement JWT token creation and validation logic using `python-jose`.
    - [ ] Create a `get_current_user` dependency to protect all necessary endpoints.
- [ ] **Core Services & Utilities**
    - [ ] Set up a centralized logging configuration.
    - [ ] Implement background task runner (FastAPI `BackgroundTasks` for V1, or Celery/Redis).
    - [ ] Define a service function to execute external scripts (`dns-automator`, etc.) via `subprocess`, capturing output and errors.

## 3. Feature-specific Backend (`management-hub-api` & Scripts)
- [ ] **Operator Authentication (US-001)**
    - [ ] **API:** Implement the `/auth/token` endpoint logic in the `services` layer.
    - [ ] **API:** Implement the `get_current_user` dependency to secure endpoints.
- [ ] **Site Management (US-002, US-003, US-004)**
    - [ ] **API:** Create Pydantic schemas for `SiteCreate`, `SiteStatus`, `BulkCreateResponse`.
    - [ ] **API:** Implement `GET /sites` endpoint with pagination to list all sites.
    - [ ] **API:** Implement `POST /sites` endpoint to create a single new site, which triggers the `dns-automator` and `hosting-automator` scripts in the background.
    - [ ] **API:** Implement `POST /sites/bulk` endpoint for CSV upload, parsing, validation, and batch site creation.
    - [ ] **API:** Implement `GET /cloudflare-accounts` endpoint to populate UI dropdowns.
- [ ] **DNS Automation (`dns-automator`)**
    - [ ] **Script:** Develop `dns-automator` Python script.
    - [ ] **Script:** Implement logic to fetch pending sites from Supabase.
    - [ ] **Script:** Integrate with Namecheap API to update nameservers.
    - [ ] **Script:** Integrate with Cloudflare API to create zones and records using account-specific tokens.
    - [ ] **Script:** Implement status update logic (`active`/`failed`) in Supabase.
- [ ] **Hosting Automation (`hosting-automator`)**
    - [ ] **Script:** Develop `hosting-automator` Python script.
    - [ ] **Script:** Implement logic to fetch sites pending hosting setup from Supabase.
    - [ ] **Script:** Integrate with CloudPanel API to create static site, system user, and provision SSL.
    - [ ] **Script:** Integrate with Matomo API to create a new trackable website entity.
    - [ ] **Script:** Implement status and metadata updates in Supabase (`status_hosting`, `hosting_doc_root`, `matomo_site_id`).
- [ ] **Content Generation Workflow (US-005, US-007, `content-engine`)**
    - [ ] **API:** Implement `POST /sites/{site_id}/generate-content` endpoint to trigger the `content-engine` as a background task.
    - [ ] **Script:** Develop `content-engine` Python package with a modular structure (`collectors`, `generators`, `publishers`).
    - [ ] **Script:** Implement data collection module using Brave/Perplexity APIs and web scraping (BeautifulSoup).
    - [ ] **Script:** Implement AI generation module with prompt templating and integration with OpenAI/Gemini APIs.
    - [ ] **Script:** Implement publisher module to write generated content as 'draft' to Directus via its API.
    - [ ] **Script:** Implement status updates in Supabase (`generating`, `generated`, `failed`).
- [ ] **Deployment Workflow (US-006, `deployment-scripts`)**
    - [ ] **API:** Implement `POST /sites/{site_id}/deploy` endpoint to trigger the `deployment-scripts` as a background task.
    - [ ] **Astro:** Create the base Astro project template with placeholder pages and components.
    - [ ] **Astro:** Implement data fetching logic in Astro to pull 'published' content for a specific site from the Directus API.
    - [ ] **Astro:** Implement logic to inject the site-specific `matomo_site_id` into the template.
    - [ ] **Script:** Develop `deployment-scripts` Python orchestrator.
    - [ ] **Script:** Implement `subprocess` call to run `astro build`.
    - [ ] **Script:** Implement `subprocess` call to run `rsync` over SSH for file deployment.
    - [ ] **Script:** Integrate with Google Site Verification API for post-deployment verification.
    - [ ] **Script:** Implement deployment status updates in Supabase.
- [ ] **Analytics Aggregation & Display (US-008, US-009, US-010, `analytics-aggregator`)**
    - [ ] **Script:** Develop `analytics-aggregator` Python script.
    - [ ] **Script:** Implement logic to fetch site lists from Supabase.
    - [ ] **Script:** Integrate with Matomo Reporting API to fetch visit data.
    - [ ] **Script:** Implement logic for GSC API authentication using stored OAuth refresh tokens for multiple accounts.
    - [ ] **Script:** Integrate with GSC API to fetch clicks and impressions.
    - [ ] **Script:** Implement logic to `UPSERT` daily aggregated data into the `daily_analytics` table.
    - [ ] **API:** Implement `GET /analytics` endpoint with date range filtering.
    - [ ] **API:** Implement `GET /analytics/{site_id}` endpoint for detailed site data.

## 4. Frontend Foundation (`management-hub-ui`)
- [ ] **Project Scaffolding**
    - [ ] Initialize a new React project using Vite and the TypeScript template.
    - [ ] Set up Tailwind CSS.
    - [ ] Install and configure `shadcn/ui`.
    - [ ] Set up client-side routing (e.g., `react-router-dom`).
- [ ] **Core Systems Setup**
    - [ ] Configure API client (e.g., Axios) with a base URL and interceptors for attaching auth tokens.
    - [ ] Set up state management (e.g., Zustand) for global state like authentication.
    - [ ] Set up server state management (`TanStack Query`) for data fetching, caching, and polling.
    - [ ] Create a `lib/` directory for API functions and utility helpers.
    - [ ] Create a `components/ui` directory for shared/customized `shadcn` components.
- [ ] **Authentication UI (US-001)**
    - [ ] Build the `LoginPage` component with a username/password form using `shadcn/ui` components.
    - [ ] Implement `useAuth` hook to handle login/logout logic and token storage.
    - [ ] Create a `ProtectedRoute` component that checks for an authenticated state and redirects to `/login` if not found.
    - [ ] Wrap all application routes (except `/login`) in the `ProtectedRoute`.

## 5. Feature-specific Frontend (`management-hub-ui`)
- [ ] **General Dashboard & Site List (US-004)**
    - [ ] Create a `DashboardPage` component.
    - [ ] Use `TanStack Query`'s `useQuery` to fetch data from the `GET /api/sites` endpoint.
    - [ ] Configure the `useQuery` hook with a `refetchInterval` to poll for status updates.
    - [ ] Build a `SiteDataTable` component using `shadcn/ui`'s DataTable.
    - [ ] Create a `StatusBadge` component that displays a colored badge based on the status string (`pending`, `active`, `failed`).
    - [ ] Implement pagination and client-side filtering/searching for the data table.
- [ ] **Site Creation UI (US-002, US-003)**
    - [ ] Add "Add New Site" button to the dashboard.
    - [ ] Create an `AddSiteDialog` component with a form for `domain` and `cloudflare_account_id`.
    - [ ] Populate the Cloudflare account dropdown by fetching data from `GET /api/cloudflare-accounts`.
    - [ ] Use `TanStack Query`'s `useMutation` to handle the `POST /api/sites` request and invalidate the site list query on success.
    - [ ] Add "Bulk Create" button and implement a file upload component for CSVs, using a mutation to post to `/api/sites/bulk`.
- [ ] **Workflow Interaction UI (US-005, US-006, US-007)**
    - [ ] Create an `ActionMenu` component (e.g., a dropdown from a three-dots icon) for each site row.
    - [ ] Add "Generate" and "Deploy" buttons to the action menu or as direct buttons in the table.
    - [ ] Hook these buttons up to `useMutation` calls for the respective API endpoints (`/generate-content`, `/deploy`).
    - [ ] Implement loading states on buttons to provide immediate feedback. The polling on the main table will handle the final status update.
    - [ ] Add a "View in CMS" link in the action menu that opens the Directus admin panel in a new tab.
- [ ] **Analytics Dashboard UI (US-008, US-009, US-010)**
    - [ ] Create an `AnalyticsPage` component.
    - [ ] Build `DateRangePicker` component using `shadcn/ui` components for filtering.
    - [ ] Create `AnalyticsOverviewWidgets` to display total metrics.
    - [ ] Build an `AnalyticsDataTable` to display per-site metrics.
    - [ ] Implement column sorting functionality in the `AnalyticsDataTable`.
    - [ ] Add charting components (using `Recharts`) to visualize data trends.
    - [ ] Implement navigation to a detailed single-site analytics page (`/analytics/{site_id}`).
- [ ] **Error Handling (US-011)**
    - [ ] Implement a system for displaying user-friendly error messages (e.g., "Toast" notifications) on API call failures.
    - [ ] Ensure `Failed` statuses in the dashboard table are visually distinct (e.g., red badge).
    - [ ] Implement a tooltip or modal to show the `error_message` from the API when hovering/clicking on a `Failed` status.

## 6. Integration
- [ ] **API Client Integration**
    - [ ] Connect all frontend data fetching hooks (`useQuery`) to their corresponding backend API endpoints.
    - [ ] Connect all frontend mutation hooks (`useMutation`) to their corresponding backend API endpoints.
    - [ ] Ensure data models (TypeScript interfaces) on the frontend match the Pydantic schemas on the backend.
- [ ] **End-to-End Feature Connection**
    - [ ] Test the full "Add Site" flow: UI -> API -> `dns-automator` -> `hosting-automator`.
    - [ ] Test the full "Generate Content" flow: UI -> API -> `content-engine` -> Directus.
    - [ ] Test the full "Deploy" flow: UI -> API -> `deployment-scripts` -> Live Server.
    - [ ] Test the full "Analytics" flow: `analytics-aggregator` -> Supabase -> API -> UI.

## 7. Testing
- [ ] **Backend Testing (`management-hub-api`)**
    - [ ] Set up `pytest` for the FastAPI application.
    - [ ] Write unit tests for services and utility functions.
    - [ ] Write integration tests for API endpoints using `TestClient`, mocking external script calls.
- [ ] **Automation Scripts Testing**
    - [ ] Write unit tests for individual functions within each automation script, mocking API calls to external services (Cloudflare, etc.).
- [ ] **Frontend Testing (`management-hub-ui`)**
    - [ ] Set up `Vitest` or `Jest` with `React Testing Library`.
    - [ ] Write unit tests for individual components and hooks.
    - [ ] Write integration tests for user flows (e.g., filling out the login form and submitting).
- [ ] **End-to-End (E2E) Testing**
    - [ ] Set up an E2E testing framework like Playwright or Cypress.
    - [ ] Write E2E tests for critical user paths: Login, Add Site, Trigger Deploy, View Analytics.
- [ ] **Performance & Security Testing**
    - [ ] Perform load testing on the API.
    - [ ] Conduct security audit/penetration testing against the API and frontend for common vulnerabilities (OWASP Top 10).

## 8. Documentation
- [ ] **API Documentation**
    - [ ] Ensure FastAPI's auto-generated OpenAPI (`/docs`) and ReDoc (`/redoc`) documentation is clean and descriptive by adding summaries and descriptions to endpoints and schemas.
- [ ] **Developer Documentation**
    - [ ] Finalize and polish the `CONTRIBUTING.md` / developer setup guide for all repositories.
    - [ ] Document the architecture and data flow of the system (using the TDD's Mermaid diagram as a base).
    - [ ] Document the purpose and environment variables for each automation script.
- [ ] **Operator Documentation**
    - [ ] Write a user guide for the System Operator explaining how to use the Management Hub UI.

## 9. Deployment
- [ ] **CI/CD Pipeline Setup**
    - [ ] Create GitHub Actions workflows for each repository.
    - [ ] CI pipeline: On every push to a feature branch, run linters, type checks, and unit/integration tests.
    - [ ] CD pipeline: On merge to `main`, automatically build Docker images (for API and UI) and push them to a container registry (e.g., Docker Hub, GHCR).
    - [ ] CD pipeline: On merge to `main` for scripts, deploy the updated scripts to the server.
- [ ] **Staging Environment**
    - [ ] Configure a staging environment that mirrors production for final testing before release.
- [ ] **Production Environment**
    - [ ] Write a production `docker-compose.prod.yml` to run the `management-hub-api`, `management-hub-ui`, `directus`, and `matomo`.
    - [ ] Configure a reverse proxy (e.g., Nginx) to handle incoming traffic, route to the correct service, and manage SSL termination.
    - [ ] Set up the `cron` job for the `analytics-aggregator` on the production server.
- [ ] **Monitoring & Alerting**
    - [ ] Set up uptime monitoring for the live application URL.
    - [ ] Configure log aggregation for all services (e.g., using the ELK stack or a cloud service).
    - [ ] Set up alerting for high error rates or service downtime.

## 10. Maintenance
- [ ] **Bug Fixing & Updates**
    - [ ] Establish a process for reporting, triaging, and fixing bugs.
    - [ ] Schedule regular dependency updates to patch security vulnerabilities.
- [ ] **Backup & Recovery**
    - [ ] Configure automated daily backups for the Supabase database.
    - [ ] Configure automated daily backups for the Directus database and file storage.
    - [ ] Document the disaster recovery procedure.
- [ ] **Performance Monitoring**
    - [ ] Regularly review API response times and server resource utilization.
    - [ ] Monitor costs associated with third-party API usage (OpenAI, etc.).