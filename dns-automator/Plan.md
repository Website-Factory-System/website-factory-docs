# `dns-automator` Development Plan

## Overview
This plan details the tasks required to build the `dns-automator` script. This module is a command-line Python script responsible for programmatically setting domain nameservers at the registrar (Namecheap) and configuring DNS zones and records in the assigned Cloudflare account.

## 1. Project Setup
- [ ] Initialize a new Python project.
- [ ] Create a `requirements.txt` file and add initial dependencies:
    - [ ] `supabase-py`
    - [ ] `python-dotenv`
    - [ ] `python-namecheap` (or `requests` if a custom wrapper is preferred)
    - [ ] `cloudflare-python`
- [ ] Set up the directory structure.
    - [ ] `dns_automator/main.py` (main script logic)
    - [ ] `dns_automator/core/config.py` (for loading settings)
    - [ ] `dns_automator/services/supabase_client.py`
    - [ ] `dns_automator/services/namecheap_client.py`
    - [ ] `dns_automator/services/cloudflare_client.py`
- [ ] Create an `.env.example` file documenting all required environment variables:
    - [ ] `SUPABASE_URL`
    - [ ] `SUPABASE_SERVICE_KEY`
    - [ ] `NAMECHEAP_API_USER`
    - [ ] `NAMECHEAP_API_KEY`
    - [ ] `NAMECHEAP_USERNAME`
    - [ ] `NAMECHEAP_CLIENT_IP`
    - [ ] `HOSTING_SERVER_IP`
- [ ] Initialize a Git repository and add a `.gitignore` file to exclude `.env`, `__pycache__`, etc.

## 2. Backend Development (Core Logic)
- [ ] **Configuration Module (`core/config.py`)**
    - [ ] Implement a function or class to load all environment variables from the `.env` file using `python-dotenv`.
- [ ] **Logging Setup**
    - [ ] Configure the standard `logging` library in `main.py` to output structured logs to both the console and a rotating file (`dns_automator.log`).
- [ ] **Supabase Service (`services/supabase_client.py`)**
    - [ ] Create a class or functions to handle all interactions with Supabase.
    - [ ] Implement `fetch_pending_dns_sites()` to query the `sites` table for records where `status_dns = 'pending'`.
    - [ ] Implement `fetch_cloudflare_account(account_id)` to get the `api_token` from the `cloudflare_accounts` table.
    - [ ] Implement `update_site_status(site_id, status, error_message=None)` to update the `sites` table record.
- [ ] **Namecheap Service (`services/namecheap_client.py`)**
    - [ ] Create a wrapper class for the Namecheap API client.
    - [ ] Implement `set_nameservers(domain, nameservers)` to update the domain's nameservers. This function should include error handling for API calls.
- [ ] **Cloudflare Service (`services/cloudflare_client.py`)**
    - [ ] Create a wrapper class for the Cloudflare API client.
    - [ ] Implement `create_zone(domain)` that creates a new zone and handles the case where the zone already exists.
    - [ ] Implement `create_dns_record(zone_id, type, name, content, proxied=True)` to create A and CNAME records, handling cases where records already exist.

## 3. Feature Implementation (Workflow)
- [ ] **Main Processing Logic (`main.py`)**
    - [ ] Implement the main execution block.
    - [ ] Call `fetch_pending_dns_sites()` to get the list of work.
    - [ ] If no sites are pending, log a message and exit gracefully.
    - [ ] Create a loop to iterate through each pending site.
    - [ ] Inside the loop, log the start of processing for the current domain.
    - [ ] **Step 1: Fetch Credentials**
        - [ ] Call `fetch_cloudflare_account()` to get the specific API token for the site. Handle cases where the account is not found.
    - [ ] **Step 2: Update Registrar**
        - [ ] Call `namecheap_client.set_nameservers()` with the standard Cloudflare nameservers.
        - [ ] If the call fails, update the site status to 'failed' with the error message and `continue` to the next site in the loop.
    - [ ] **Step 3: Configure Cloudflare**
        - [ ] Initialize the Cloudflare client with the fetched token.
        - [ ] Call `cloudflare_client.create_zone()`. If it fails, update status to 'failed' and continue.
        - [ ] Call `cloudflare_client.create_dns_record()` to add the 'A' record pointing to `HOSTING_SERVER_IP`.
        - [ ] Call `cloudflare_client.create_dns_record()` to add the 'CNAME' record for 'www' pointing to the root domain.
        - [ ] If any record creation fails, update status to 'failed' and continue.
    - [ ] **Step 4: Finalize Status**
        - [ ] If all steps are successful, call `update_site_status()` to set `status_dns` to 'active'.
    - [ ] Add a final log message indicating the script run is complete.

## 4. Testing
- [ ] **Unit Tests**
    - [ ] Set up `pytest`.
    - [ ] Write tests for the Namecheap client, mocking the API calls.
    - [ ] Write tests for the Cloudflare client, mocking the API calls.
    - [ ] Write tests for the Supabase client, mocking the database responses.
- [ ] **Integration Tests**
    - [ ] Write a test script that runs the main loop against a mock Supabase client to ensure the logic flow is correct.
    - [ ] Perform a manual end-to-end test with a real test domain and test credentials to verify the entire process.

## 5. Documentation and Deployment
- [ ] **Documentation**
    - [ ] Write a comprehensive `README.md` explaining the script's purpose, setup, required environment variables, and how to run it.
- [ ] **Deployment**
    - [ ] Create a shell script (`run.sh`) to simplify execution.
    - [ ] Document the steps for deploying the script to the production server, including setting up the `.env` file with real credentials and ensuring file permissions are correct.