# PRD: Analytics Aggregator

## 1. Product overview
### 1.1 Document title and version
*   PRD: Analytics Aggregator
*   Version: 1.0

### 1.2 Product summary
This document outlines the requirements for the Analytics Aggregator. This is a crucial backend automation script within the Website Factory system that operates on a recurring schedule. Its sole purpose is to gather performance data from disparate sources—the self-hosted Matomo analytics instance and Google Search Console—for every managed website in the portfolio.

The script fetches key metrics like visits, clicks, and impressions, then normalizes and stores this data in a central database table within Supabase. This aggregated data then powers the Analytics Dashboard in the Management Hub, providing the operator with a unified, high-level view of portfolio performance without needing to log into multiple services.

## 2. Goals
### 2.1 Business goals
*   Provide a single source of truth for website portfolio performance.
*   Enable data-driven decision-making by consolidating key metrics.
*   Eliminate the manual effort of checking analytics for hundreds of individual sites.

### 2.2 User goals
*   As an operator, I want the analytics data in my dashboard to be updated automatically and regularly (e.g., daily).
*   As an operator, I want to see both traffic data (from Matomo) and search performance data (from GSC) in the same place.

### 2.3 Non-goals
*   This script will not provide real-time analytics; the data will be as fresh as the last scheduled run.
*   This script will not perform deep analysis or generate insights; it only collects and stores raw metrics.
*   This script does not have a user interface.

## 3. User personas
### 3.1 Key user types
*   System (invoked by a scheduler)

### 3.2 Basic persona details
*   **System**: A non-interactive script triggered automatically by a system scheduler like `cron`.

### 3.3 Role-based access
*   Not applicable.

## 4. Functional requirements
*   **Scheduled Execution** (Priority: High)
    *   The script must be designed to be run automatically on a recurring schedule (e.g., once every 24 hours).
*   **Fetch Site List** (Priority: High)
    *   On each run, the script must query the Supabase `sites` table to get the list of all active, deployed sites to monitor.
    *   The query must retrieve necessary identifiers: `domain`, `matomo_site_id`, and `gsc_account_id`.
*   **Fetch Matomo Data** (Priority: High)
    *   The script must connect to the Matomo Reporting API.
    *   For each site, it must fetch key metrics (e.g., `nb_visits`) for a specified date range (e.g., the previous day).
*   **Fetch Google Search Console Data** (Priority: High)
    *   The script must be able to authenticate with multiple Google accounts using stored OAuth 2.0 refresh tokens.
    *   For each site, it must connect to the Google Search Console API using the correctly assigned Google account's credentials.
    *   It must fetch key metrics (e.g., `clicks`, `impressions`) for the same date range.
*   **Store Aggregated Data** (Priority: High)
    *   The script must combine the fetched Matomo and GSC data for each site.
    *   It must insert or update a record in the central Supabase `daily_analytics` table for each site for that day.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Resilience**: The failure to fetch data for one site (e.g., a newly added site not yet indexed by GSC) must not stop the script from processing all other sites.
*   **Backfilling**: The script could optionally accept a date range as an argument to allow for backfilling historical data if a run was missed.
*   **API Quota Management**: The script must be mindful of GSC API quotas and handle potential quota-exceeded errors gracefully.

### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
Every night at 2 AM, a `cron` job awakens the Analytics Aggregator script. The script connects to Supabase and gets its to-do list: all 200 live websites. It then goes to work. First, it calls the Matomo API, asking "How many visits did each of these sites get yesterday?" and records the answers. Next, it sorts the sites by their assigned Google account. For the first group of 50 sites, it logs into Google Account #1 via API and asks, "How many clicks and impressions did each of these sites get yesterday?". It repeats this for all Google accounts and their assigned sites. Finally, it takes all the collected data and neatly inserts it into the `daily_analytics` table in Supabase, ready for the operator to view in the Management Hub dashboard in the morning.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Data freshness in the analytics dashboard. Target: Data is never more than 24 hours old.

### 7.3. Technical metrics
*   Script run completion rate. Target: > 99%.
*   Total execution time for a full run.
*   API error rate from Matomo and GSC.

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (read `sites`, `gsc_accounts`; write `daily_analytics`).
*   Matomo Reporting API.
*   Google Search Console API.
*   System scheduler (`cron`).

### 8.2. Data storage & privacy
*   Handles sensitive Matomo API token and Google OAuth refresh tokens. These must be loaded securely from environment variables or the Supabase `gsc_accounts` table.

### 8.3. Scalability & performance
*   The script's runtime will scale linearly with the number of sites. Performance can be improved by making API calls concurrently (e.g., using `asyncio`), but this adds complexity and is not required for V1.
*   The main bottleneck will be GSC API quotas, which might require pacing the requests.

### 8.4. Potential challenges
*   Managing OAuth 2.0 refresh tokens for multiple Google accounts and ensuring they remain valid.
*   Handling the various data formats and potential inconsistencies from the different APIs.
*   The GSC API has data availability delays (typically ~48 hours), which must be accounted for when querying for "yesterday's" data. The script should query for data from two days prior.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Small: 3-5 days

### 9.2. Team size & composition
*   1 Backend Engineer

### 9.3. Suggested phases
*   **Phase 1**: Develop logic to fetch data from Matomo for a list of sites.
*   **Phase 2**: Develop logic to authenticate and fetch data from GSC for one account.
*   **Phase 3**: Integrate Supabase to get the site list and store the results. Add logic to handle multiple GSC accounts. Schedule the script with `cron`.

## 10. User stories
*   **ID**: US-AGG-001
*   **Description**: As the system, I want to run automatically on a daily schedule to keep analytics data fresh.
*   **Acceptance criteria**:
    *   The script can be executed from the command line.
    *   A `cron` job is configured on the server to run the script once every 24 hours.
*   **ID**: US-AGG-002
*   **Description**: As the system, I want to fetch daily traffic data from Matomo for all active websites.
*   **Acceptance criteria**:
    *   The script queries Supabase to get the `matomo_site_id` for all deployed sites.
    *   The script successfully authenticates with the Matomo Reporting API.
    *   The script makes an API call for each site to retrieve the number of visits for the previous full day (or D-2 to align with GSC).
*   **ID**: US-AGG-003
*   **Description**: As the system, I want to fetch daily search performance data from Google Search Console for all active websites, using the correct Google account for each.
*   **Acceptance criteria**:
    *   The script queries Supabase for the `gsc_account_id` and GSC refresh tokens for each site/account.
    *   The script successfully authenticates with the GSC API using the stored OAuth 2.0 refresh tokens for each required account.
    *   The script makes an API call for each site to retrieve the number of clicks and impressions for the previous full day (or D-2).
*   **ID**: US-AGG-004
*   **Description**: As the system, I want to store the collected metrics in a centralized database.
*   **Acceptance criteria**:
    *   For each site, the script combines the data from Matomo and GSC for a specific date.
    *   The script performs an INSERT or UPDATE (UPSERT) operation into the `daily_analytics` table in Supabase.
    *   The record in the database contains the correct `date`, `site_id`, `matomo_visits`, `gsc_clicks`, and `gsc_impressions`.