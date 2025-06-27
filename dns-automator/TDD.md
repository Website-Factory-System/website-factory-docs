# Technical Design Document: DNS Automator

## 1. Architecture & Design

This module is a stateless Python script designed to be executed on-demand by the Management Hub API. It will not run as a persistent service.

*   **Language**: Python 3.9+
*   **Execution Model**: Command-line script (`python dns_manager.py`). It will be triggered via a `subprocess` call from the `management-hub-api` backend.
*   **Configuration**: All secrets (API keys, DB connection strings) will be managed via an `.env` file, loaded at runtime using the `python-dotenv` library. The script will not contain any hardcoded credentials.

## 2. Data Flow & Logic

1.  **Initialization**:
    *   Load environment variables from `.env` (SUPABASE_URL, SUPABASE_SERVICE_KEY, NAMECHEAP_API_USER, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP, HOSTING_SERVER_IP).
    *   Initialize the Supabase client.
    *   Configure the `logging` module to output to both console and a file (`dns_automator.log`).
2.  **Fetch Work**:
    *   Query the `sites` table in Supabase: `SELECT * FROM sites WHERE status_dns = 'pending'`.
    *   If the query returns no rows, log "No pending sites found." and exit gracefully.
3.  **Process Loop**:
    *   Iterate through each site returned from the query.
    *   For each `site`:
        a.  Log `INFO: Processing domain {site.domain}`.
        b.  Query `cloudflare_accounts` table: `SELECT api_token FROM cloudflare_accounts WHERE id = {site.cloudflare_account_id}`. If not found, log `ERROR` and skip to next site.
        c.  Call `update_registrar_ns()` function. If it returns `False`, call `update_status_in_db()` with 'failed' and an error message, then continue to the next site.
        d.  Call `configure_cloudflare()` function. If it returns `False`, call `update_status_in_db()` with 'failed' and an error message, then continue to the next site.
        e.  If both succeed, call `update_status_in_db()` with 'active'.
4.  **Completion**: Log "DNS Automator run finished."

## 3. Core Function Algorithms

### 3.1 `update_registrar_ns(domain)`

*   **Input**: `domain` (str)
*   **Output**: `bool` (Success/Failure)
*   **Logic**:
    1.  Initialize Namecheap API client using credentials from config.
    2.  `try`:
        *   Call Namecheap API endpoint to update nameservers for the `domain` to standard Cloudflare NS (e.g., `fay.ns.cloudflare.com`, `guy.ns.cloudflare.com`).
        *   Log `INFO: Successfully updated nameservers for {domain}`.
        *   Return `True`.
    3.  `except NamecheapAPIError as e`:
        *   Log `ERROR: Namecheap API error for {domain}: {e}`.
        *   Store error message.
        *   Return `False`.

### 3.2 `configure_cloudflare(domain, cf_api_token, server_ip)`

*   **Input**: `domain` (str), `cf_api_token` (str), `server_ip` (str)
*   **Output**: `bool` (Success/Failure)
*   **Logic**:
    1.  Initialize Cloudflare API client using the provided `cf_api_token`.
    2.  **Create Zone**:
        *   `try`: Call `zones.post()` with `name=domain`. Store the returned `zone_id`.
        *   `except CloudflareAPIError as e`: If error indicates zone already exists, log `WARNING` and proceed to fetch the existing `zone_id`. Otherwise, log `ERROR`, store error message, and return `False`.
    3.  **Create A Record**:
        *   `try`: Call `dns.records.post()` for the `zone_id` with `type='A'`, `name='@'`, `content=server_ip`, `proxied=True`.
        *   `except CloudflareAPIError as e`: If error indicates record already exists with same content, log `WARNING` and continue. Otherwise, log `ERROR`, store error message, and return `False`.
    4.  **Create CNAME Record**:
        *   `try`: Call `dns.records.post()` for the `zone_id` with `type='CNAME'`, `name='www'`, `content=domain`, `proxied=True`.
        *   `except CloudflareAPIError as e`: If error indicates record already exists, log `WARNING`. Otherwise, log `ERROR`, store error message, and return `False`.
    5.  Return `True`.

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.9+ | Core scripting language. |
| Libraries | `supabase-py` | Interaction with Supabase database. |
| | `python-dotenv` | Loading configuration from `.env` files. |
| | `python-namecheap` | Wrapper for Namecheap API (or `requests`). |
| | `cloudflare-python` | Official wrapper for Cloudflare API. |
| | `logging` | Standard library for structured logging. |
| Database | Supabase (PostgreSQL) | Central data store for site status and credentials. |

## 5. Security Measures

*   **Credential Storage**: The script will NOT store any credentials. It will load them from environment variables populated from a `.env` file at runtime. This `.env` file must be listed in `.gitignore` and managed securely on the production server with restricted file permissions.
*   **API Token Scope**: The script relies on the operator having created scoped Cloudflare API tokens with only the necessary "Edit zone DNS" permissions, not global API keys.
*   **Error Masking**: Logged error messages will be reviewed to ensure they do not leak sensitive information (like parts of an API key) into the log files.
*   **Input Validation**: The script implicitly trusts the domain names from the Supabase DB. The Management Hub API is responsible for validating domain name formats before insertion.
*   **Dependencies**: A `requirements.txt` file with pinned versions will be used to mitigate supply chain attacks by ensuring dependencies are known and consistent. The dependencies should be audited for known vulnerabilities.