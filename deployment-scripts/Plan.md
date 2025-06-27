# `deployment-scripts` Development Plan

## Overview
This plan details the development of the `deployment-scripts` module. This module is composed of a Python orchestration script and an Astro static site generator project. It builds the static site using content from Directus and deploys the files to the server via `rsync`.

## 1. Project Setup
- [ ] **Main Project Structure**
    - [ ] Initialize a Git repository.
    - [ ] Create a top-level Python project for the orchestrator script.
    - [ ] Create a subdirectory `astro-template/` for the Astro project.
- [ ] **Python Orchestrator Setup**
    - [ ] Create a `requirements.txt` file with dependencies: `supabase-py`, `python-dotenv`, `requests`.
    - [ ] Create an `.env.example` file: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DIRECTUS_API_URL`, `DIRECTUS_API_TOKEN`, `SSH_HOST`, `SSH_USER`, `SSH_KEY_PATH`, `GSC_API_CREDENTIALS_JSON_PATH`.
- [ ] **Astro Template Setup (`astro-template/`)**
    - [ ] Initialize a new Astro project with `npm create astro@latest`.
    - [ ] Install dependencies: `astro`, Directus SDK (`@directus/sdk`).
    - [ ] Set up Tailwind CSS within the Astro project.
    - [ ] Create a `.env.example` in the Astro project for build-time variables like `DIRECTUS_API_URL` and `DIRECTUS_API_TOKEN`.
    - [ ] Add `dist/` and `node_modules/` to the Astro project's `.gitignore`.

## 2. Astro Template Development (`astro-template/`)
- [ ] **Directus Client**
    - [ ] Create a utility file (`src/lib/directus.ts`) to initialize and export the Directus SDK client.
- [ ] **Data Fetching Logic**
    - [ ] In a dynamic page route (e.g., `src/pages/[...slug].astro`), implement the logic to fetch page data from Directus.
    - [ ] The fetch logic must filter content based on the site's domain (passed via an environment variable during build) and `status = 'published'`.
    - [ ] Use `getStaticPaths` to generate pages based on data from Directus.
- [ ] **Component & Layout Development**
    - [ ] Create a main `Layout.astro` component.
    - [ ] Implement logic in the layout to inject the Matomo tracking script, using the `MATOMO_SITE_ID` passed as an environment variable.
    - [ ] Create Astro components to render different `page_sections` fetched from Directus (e.g., `HeroSection.astro`, `TextBlock.astro`).
- [ ] **Build Configuration**
    - [ ] Configure `astro.config.mjs` to read environment variables for the build process.

## 3. Python Orchestrator Development
- [ ] **Core Logic**
    - [ ] Create `deploy_site.py` as the main entry point, accepting a `site_id`.
    - [ ] Implement configuration loading and logging.
    - [ ] Implement a Supabase client to fetch site metadata (`domain`, `matomo_site_id`, `hosting_doc_root`).
- [ ] **Build Function (`run_astro_build`)**
    - [ ] Implement a function that executes the Astro build command (`npm run build`) using `subprocess.run`.
    - [ ] Pass the site-specific `SITE_DOMAIN_FILTER` and `MATOMO_SITE_ID` as environment variables to the subprocess.
    - [ ] Capture `stdout` and `stderr` for logging and error handling.
    - [ ] Ensure the build output goes to a unique temporary directory (e.g., `/tmp/build/{domain}`).
- [ ] **Deploy Function (`run_rsync_deploy`)**
    - [ ] Implement a function that constructs and executes the `rsync` command using `subprocess.run`.
    - [ ] The command must use the correct SSH key, user, host, and destination path (`hosting_doc_root`).
    - [ ] The command must include flags for archive (`-a`), verbose (`-v`), compress (`-z`), and delete (`--delete`).
- [ ] **Verification Function (`run_verification`)**
    - [ ] Implement a function to perform a basic HTTP GET request to the live domain to check for a 200 OK status.
    - [ ] Implement a function to call the Google Site Verification API.
- [ ] **Main Workflow**
    - [ ] Orchestrate the calls: update status to `deploying`, run build, run deploy, run verification, update status to `deployed` or `failed`.

## 4. Testing
- [ ] **Astro Template**
    - [ ] Manually run `astro build` with hardcoded environment variables to test the build process against a dev Directus instance.
- [ ] **Python Orchestrator**
    - [ ] Write unit tests for the build and deploy functions, mocking the `subprocess.run` calls.
- [ ] **End-to-End**
    - [ ] Perform a full manual test for a site: run the `deploy_site.py` script and verify that the build runs, files appear on the server, and the live site is updated.

## 5. Documentation and Deployment
- [ ] **Documentation**
    - [ ] Write a `README.md` explaining the two-part structure (Python + Astro), the setup for both, and the deployment process.
- [ ] **Deployment**
    - [ ] Document the server requirements: Node.js, npm, Python, rsync, ssh.
    - [ ] Document the process of installing Astro dependencies (`npm install`) on the server where the script runs.