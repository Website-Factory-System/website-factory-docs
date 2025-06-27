# `hosting-automator` Development Plan

## Overview
This plan covers the development of the `hosting-automator` script. This module is a command-line Python script that provisions the server-side hosting environment on CloudPanel, including SSL, and creates a corresponding tracking site in Matomo.

## 1. Project Setup
- [ ] Initialize a new Python project.
- [ ] Create a `requirements.txt` file and add dependencies:
    - [ ] `supabase-py`
    - [ ] `python-dotenv`
    - [ ] `requests`
- [ ] Set up the directory structure.
    - [ ] `hosting_automator/main.py`
    - [ ] `hosting_automator/core/config.py`
    - [ ] `hosting_automator/services/supabase_client.py`
    - [ ] `hosting_automator/services/cloudpanel_client.py`
    - [ ] `hosting_automator/services/matomo_client.py`
- [ ] Create an `.env.example` file documenting required variables:
    - [ ] `SUPABASE_URL`
    - [ ] `SUPABASE_SERVICE_KEY`
    - [ ] `CLOUDPANEL_API_URL`
    - [ ] `CLOUDPANEL_API_TOKEN`
    - [ ] `MATOMO_API_URL`
    - [ ] `MATOMO_API_TOKEN`
- [ ] Initialize a Git repository and a `.gitignore` file.

## 2. Backend Development (Core Logic)
- [ ] **Configuration Module (`core/config.py`)**
    - [ ] Implement logic to load all environment variables from `.env`.
- [ ] **Logging Setup**
    - [ ] Configure the `logging` library in `main.py` for console and file output (`hosting_automator.log`).
- [ ] **Supabase Service (`services/supabase_client.py`)**
    - [ ] Create a class/functions for Supabase interactions.
    - [ ] Implement `fetch_pending_hosting_sites()` to get sites where `status_dns = 'active'` and `status_hosting = 'pending'`.
    - [ ] Implement `update_site_hosting_status(site_id, status, doc_root=None, matomo_id=None, error_message=None)` to update the `sites` record.
- [ ] **CloudPanel Service (`services/cloudpanel_client.py`)**
    - [ ] Create a client class to interact with the CloudPanel API via `requests`.
    - [ ] Implement `create_static_site(domain)` which:
        - [ ] Generates a secure site user and password.
        - [ ] Makes the `POST` request to create the site.
        - [ ] Handles errors and idempotency (if site already exists).
        - [ ] Returns the document root path on success.
    - [ ] Implement `provision_ssl(domain)` to trigger the Let's Encrypt SSL certificate creation.
- [ ] **Matomo Service (`services/matomo_client.py`)**
    - [ ] Create a client class to interact with the Matomo Reporting API.
    - [ ] Implement `create_tracking_site(domain)` which:
        - [ ] Makes the `SitesManager.addSite` API call.
        - [ ] Parses the response to get the new `idSite`.
        - [ ] Handles API errors gracefully.

## 3. Feature Implementation (Workflow)
- [ ] **Main Processing Logic (`main.py`)**
    - [ ] Implement the main execution block and fetch pending sites from Supabase.
    - [ ] Create a loop to iterate through each pending site.
    - [ ] **Step 1: Create Hosting in CloudPanel**
        - [ ] Call `cloudpanel_client.create_static_site()`.
        - [ ] If successful, store the returned `doc_root`.
        - [ ] If it fails, update status to 'failed' with an error message and `continue` to the next site.
    - [ ] **Step 2: Provision SSL**
        - [ ] Call `cloudpanel_client.provision_ssl()`.
        - [ ] If it fails, log a critical error, update status to 'failed', and continue.
    - [ ] **Step 3: Create Analytics Site in Matomo**
        - [ ] Call `matomo_client.create_tracking_site()`.
        - [ ] Store the returned `matomo_id`.
        - [ ] If this step fails, log it as a `WARNING` but do not fail the entire hosting process. The `matomo_id` will be `None`.
    - [ ] **Step 4: Finalize Status in Database**
        - [ ] Call `update_site_hosting_status()` with `status='active'` and the collected `doc_root` and `matomo_id`.
    - [ ] Add a final log message for script completion.

## 4. Testing
- [ ] **Unit Tests**
    - [ ] Set up `pytest`.
    - [ ] Write tests for the CloudPanel client, mocking `requests` calls and responses.
    - [ ] Write tests for the Matomo client, mocking `requests` calls and responses.
    - [ ] Write tests for the Supabase client functions.
- [ ] **Integration Tests**
    - [ ] Perform a manual end-to-end test with a test domain whose DNS is already configured to point to the server.

## 5. Documentation and Deployment
- [ ] **Documentation**
    - [ ] Write a `README.md` explaining the script's purpose, setup, and execution.
- [ ] **Deployment**
    - [ ] Document the steps to deploy the script to the production server and set up the `.env` file.