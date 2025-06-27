# `analytics-aggregator` Development Plan

## Overview
This plan details the tasks for the `analytics-aggregator`, a scheduled Python script that fetches data from Matomo and Google Search Console and stores it in the central Supabase database.

## 1. Project Setup
- [ ] Initialize a new Python project.
- [ ] Create a `requirements.txt` file and add dependencies:
    - [ ] `supabase-py`
    - [ ] `python-dotenv`
    - [ ] `requests`
    - [ ] `google-api-python-client`
    - [ ] `google-auth-oauthlib`
- [ ] Create an `.env.example` file with required variables:
    - [ ] `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
    - [ ] `MATOMO_API_URL`, `MATOMO_API_TOKEN`
    - [ ] `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- [ ] Initialize a Git repository and a `.gitignore` file.

## 2. Backend Development (Core Logic)
- [ ] **Configuration and Services**
    - [ ] Implement configuration loading from `.env`.
    - [ ] Set up logging.
    - [ ] Implement a Supabase client to:
        - [ ] Fetch all active, deployed sites (`sites` table).
        - [ ] Fetch all GSC account credentials (`gsc_accounts` table).
        - [ ] Perform a bulk `UPSERT` into the `daily_analytics` table.
- [ ] **Matomo Data Fetcher**
    - [ ] Create a function `get_matomo_data(site_ids, date)` that:
        - [ ] Connects to the Matomo Reporting API.
        - [ ] Fetches the `nb_visits` metric for the given sites and date.
        - [ ] Returns a dictionary mapping `{site_id: visit_count}`.
- [ ] **Google Search Console (GSC) Data Fetcher**
    - [ ] Implement a helper function `get_google_client(refresh_token)` to handle the OAuth 2.0 flow and return an authenticated GSC service object.
    - [ ] Create a function `get_gsc_data(gsc_client, site_url, date)` that:
        - [ ] Makes a `searchanalytics.query` API call for the site.
        - [ ] Fetches `clicks` and `impressions`.
        - [ ] Handles cases where a site has no data yet.
        - [ ] Returns a dictionary `{clicks: count, impressions: count}`.

## 3. Feature Implementation (Workflow)
- [ ] **Main Aggregation Logic (`aggregator.py`)**
    - [ ] **Step 1: Initialization**
        - [ ] Determine the target date for fetching (e.g., `today - 2 days`). Allow overriding with a command-line argument for backfilling.
        - [ ] Fetch the list of all sites and all GSC accounts from Supabase.
    - [ ] **Step 2: Group Workload**
        - [ ] Group the site list by `gsc_account_id` to minimize re-authentication.
    - [ ] **Step 3: Fetch Data**
        - [ ] Create a master data dictionary to hold results, e.g., `{site_id: {matomo_visits: 0, gsc_clicks: 0, ...}}`.
        - [ ] Call `get_matomo_data()` for all sites and populate the master dictionary.
        - [ ] Loop through each GSC account group:
            - [ ] Authenticate once for the group using its refresh token.
            - [ ] Loop through the sites within the group and call `get_gsc_data()`.
            - [ ] Populate the master dictionary with the GSC results.
    - [ ] **Step 4: Store Data**
        - [ ] Transform the master data dictionary into a list of records suitable for the `daily_analytics` table.
        - [ ] Perform a single bulk `UPSERT` operation to save all records to Supabase.
    - [ ] Implement robust error handling to ensure failure for one site/API doesn't stop the entire script.

## 4. Testing
- [ ] **Unit Tests**
    - [ ] Write tests for the Matomo and GSC fetcher functions, mocking all API calls.
    - [ ] Write a test for the GSC authentication helper.
- [ ] **Integration Tests**
    - [ ] Perform a manual test run of the script, verifying that it correctly fetches data from both services and populates the `daily_analytics` table in a dev Supabase project.

## 5. Documentation and Deployment
- [ ] **Documentation**
    - [ ] Write a `README.md` explaining the script's purpose, the data sources, setup, and how to run it manually.
- [ ] **Deployment**
    - [ ] Document the steps for deploying the script to the production server.
    - [ ] Provide a sample `crontab` entry to schedule the script to run daily (e.g., `0 2 * * * /usr/bin/python /path/to/aggregator.py`).