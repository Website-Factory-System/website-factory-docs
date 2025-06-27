# Technical Design Document: Hosting Automator

## 1. Architecture & Design

This module is a stateless Python script, executed on-demand by the Management Hub API via a `subprocess` call. It orchestrates interactions between the central Supabase database and the CloudPanel and Matomo APIs.

*   **Language**: Python 3.9+
*   **Execution Model**: Command-line script (`python hosting_manager.py`).
*   **Configuration**: Secrets (API keys, URLs) will be loaded from an `.env` file using `python-dotenv`.

## 2. Data Flow & Logic

1.  **Initialization**:
    *   Load environment variables from `.env` (SUPABASE_URL, SUPABASE_SERVICE_KEY, CLOUDPANEL_API_URL, CLOUDPANEL_API_TOKEN, MATOMO_API_URL, MATOMO_API_TOKEN).
    *   Initialize the Supabase client.
    *   Configure `logging`.
2.  **Fetch Work**:
    *   Query Supabase: `SELECT * FROM sites WHERE status_dns = 'active' AND status_hosting = 'pending'`.
    *   If no rows are returned, log and exit.
3.  **Process Loop**:
    *   Iterate through each pending `site`.
    *   Log `INFO: Processing hosting for {site.domain}`.
    *   Call `create_cloudpanel_site()`. Store the returned `doc_root`. If it returns `None`, update status to 'failed', log the error, and continue to the next site.
    *   Call `create_matomo_site()`. Store the returned `matomo_id`. If it returns `None`, log a `WARNING` but do not fail the entire process.
    *   Call `update_status_in_db()` with 'active' and the retrieved `doc_root` and `matomo_id`.

## 3. Core Function Algorithms

### 3.1 `create_cloudpanel_site(domain)`

*   **Input**: `domain` (str)
*   **Output**: `str` or `None` (document root path on success, None on failure)
*   **Logic**:
    1.  Prepare the `requests` session with the `Authorization: Bearer {CLOUDPANEL_API_TOKEN}` header.
    2.  Define the JSON payload for the CloudPanel "Add Static Site" endpoint. This will include `domainName`, a generated `siteUser`, and a randomly generated strong password.
    3.  `try`:
        *   Make a `POST` request to `{CLOUDPANEL_API_URL}/site`.
        *   Check for a successful HTTP status code (e.g., 201).
        *   Make a `POST` request to the CloudPanel "Add SSL Certificate" endpoint for the `domain`.
        *   Check for a successful status code.
        *   Log `INFO: Successfully created CloudPanel site for {domain}`.
        *   Construct the expected document root path (e.g., `/home/{siteUser}/htdocs/{domain}`).
        *   Return the document root path.
    4.  `except requests.RequestException as e`:
        *   Log `ERROR: CloudPanel API error for {domain}: {e}`.
        *   Store the error message.
        *   Return `None`.

### 3.2 `create_matomo_site(domain)`

*   **Input**: `domain` (str)
*   **Output**: `int` or `None` (Matomo site ID on success, None on failure)
*   **Logic**:
    1.  Construct the Matomo Reporting API request URL. The query parameters will include `module=API`, `method=SitesManager.addSite`, `siteName={domain}`, `urls=https://{domain}`, `format=json`, and `token_auth={MATOMO_API_TOKEN}`.
    2.  `try`:
        *   Make a `GET` request to the constructed URL.
        *   Check for a successful HTTP status code.
        *   Parse the JSON response. If it contains an error result, log it as a `WARNING`.
        *   Extract the `value` (the site ID) from the successful JSON response.
        *   Log `INFO: Successfully created Matomo site for {domain} with ID {id}`.
        *   Return the integer site ID.
    3.  `except requests.RequestException as e`:
        *   Log `WARNING: Matomo API error for {domain}: {e}. Hosting will proceed without analytics setup.`.
        *   Return `None`.

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.9+ | Core scripting language. |
| Libraries | `supabase-py` | Interaction with Supabase database. |
| | `python-dotenv` | Loading configuration from `.env` files. |
| | `requests` | For making direct HTTP API calls to CloudPanel and Matomo. |
| | `logging` | Standard library for structured logging. |
| APIs | CloudPanel API, Matomo Reporting API | Core service integrations. |

## 5. Security Measures

*   **Credential Management**: All API tokens and URLs for CloudPanel and Matomo will be loaded from environment variables (`.env` file) at runtime. The `.env` file must be in `.gitignore`.
*   **Network Communication**: All API calls to CloudPanel and Matomo will be made over HTTPS.
*   **Generated Passwords**: Passwords generated for CloudPanel site users will be cryptographically secure and will not be logged.
*   **Error Sanitization**: Ensure that raw API error responses, which might contain internal path information, are not written to the user-facing `error_message` field in the database. Log them to the secure server-side log file only.