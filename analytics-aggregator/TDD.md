# Technical Design Document: Analytics Aggregator

## 1. Architecture & Design

This module is a stateless Python script designed for scheduled execution via `cron`. Its architecture is focused on data extraction, transformation (minimal), and loading (ETL).

*   **Language**: Python 3.9+
*   **Execution Model**: Command-line script (`python aggregator.py`) triggered by a system `cron` job. It can optionally accept `--date` arguments for backfilling.
*   **Configuration**: All secrets (API keys, DB connection strings) will be loaded from an `.env` file.

## 2. Data Flow & Logic

1.  **Initialization**:
    *   Load configuration from `.env`.
    *   Initialize Supabase client. Configure `logging`.
    *   Determine the target date for data fetching. Default to `today - 2 days` to account for GSC data lag.
2.  **Fetch Workload**:
    *   Query Supabase to get all sites: `SELECT id, domain, matomo_site_id, gsc_account_id FROM sites WHERE status_deployment = 'deployed'`.
    *   Query Supabase to get all GSC account credentials: `SELECT id, oauth_refresh_token FROM gsc_accounts`. Store this in a dictionary keyed by `id`.
3.  **Fetch Matomo Data**:
    *   Create a reusable function `get_matomo_data(site_ids, date)`.
    *   This function will make calls to the Matomo `API.getBulkRequest` endpoint if possible for efficiency, or loop through `site_ids` and call `VisitsSummary.get` for each.
    *   Return a dictionary mapping `site_id` to its visit count.
4.  **Fetch GSC Data**:
    *   Group sites by their `gsc_account_id`.
    *   Iterate through each group (`gsc_account_id` and its list of sites).
        *   Authenticate with the Google API client using the `oauth_refresh_token` for this `gsc_account_id`.
        *   Create a reusable function `get_gsc_data(gsc_client, site_urls, date)`.
        *   This function will loop through the `site_urls` in the group and make an API call to `searchanalytics.query` for each.
        *   Return a dictionary mapping `site_id` to its clicks and impressions.
    *   Combine results from all groups into a single dictionary.
5.  **Store Data**:
    *   Iterate through the master list of sites.
    *   For each `site_id`, retrieve the Matomo and GSC data from the dictionaries created in the previous steps.
    *   Construct a record object for the `daily_analytics` table.
    *   Perform a bulk `UPSERT` operation into the `daily_analytics` table in Supabase to insert new records or update existing ones for that date.
6.  **Completion**: Log a summary of the run (e.g., "Processed 198 sites. Fetched Matomo data for 195. Fetched GSC data for 180. Stored 198 records.").

## 3. Core Function Algorithms

### 3.1 GSC Authentication

*   A helper class or function `get_google_client(refresh_token)` will handle the OAuth 2.0 flow. It will use the `google.oauth2.credentials.Credentials` object, passing the stored `refresh_token` along with the client ID and secret (loaded from config). The `googleapiclient.discovery.build` function will then use these credentials to create the service object.

### 3.2 Database `UPSERT`

*   To avoid race conditions or errors on re-runs, the database insertion will use an `UPSERT` (Update if conflict, otherwise Insert) command.
*   In PostgreSQL (which Supabase uses), this is done with `INSERT INTO daily_analytics (...) VALUES (...) ON CONFLICT (date, site_id) DO UPDATE SET matomo_visits = EXCLUDED.matomo_visits, ...`.
*   The `supabase-py` library should support this, or a direct SQL execution can be used.

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.9+ | Core scripting language. |
| Libraries | `supabase-py` | DB interaction. |
| | `python-dotenv` | Config loading. |
| | `requests` | For Matomo API calls. |
| | `google-api-python-client` | Official Google API library. |
| | `google-auth-oauthlib` | For handling Google OAuth 2.0 flow. |
| Scheduler | `cron` | System tool for scheduled execution. |

## 5. Security Measures

*   **Credential Management**: Google OAuth `client_id` and `client_secret` along with Matomo token will be in the `.env` file. Google `refresh_tokens` will be fetched from the secure Supabase DB at runtime.
*   **Token Security**: Refresh tokens are highly sensitive and grant long-lived access. The Supabase `gsc_accounts` table must have restrictive access policies if ever exposed via an API (though this script accesses it via the secure service role key).
*   **Error Logging**: Ensure logs do not print out the full content of sensitive tokens or API responses that might contain personal information.