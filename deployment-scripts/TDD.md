# Technical Design Document: Deployment Scripts

## 1. Architecture & Design

This module consists of a primary Python orchestration script (`deploy_site.py`) and a separate Astro project template. The Python script is the entry point, responsible for controlling the build and deploy stages.

*   **Orchestrator Language**: Python 3.9+
*   **SSG**: Astro
*   **Deployment Tool**: `rsync` (system command)
*   **Execution Model**: The `deploy_site.py` script will be executed as an asynchronous background task by the Management Hub API, taking a `site_id` as its primary argument.
*   **Environment**: The machine or Docker container executing this script must have Python, Node.js, `npm`/`yarn`, `rsync`, and `ssh` installed. The Astro project dependencies must also be installed (`npm install`).

## 2. Data Flow & Logic

1.  **Entry Point (`deploy_site.py`)**:
    *   Receives `site_id`.
    *   Loads configuration from `.env` (SUPABASE_URL/KEY, DIRECTUS_URL/TOKEN, SSH_HOST, SSH_USER, SSH_KEY_PATH).
    *   Initializes Supabase client. Updates site status to `'deploying'`.
    *   Fetches site metadata (`domain`, `matomo_site_id`, `hosting_doc_root`) from Supabase.
2.  **Build Stage**:
    *   Calls `run_astro_build(domain, matomo_site_id)`.
    *   This function sets environment variables for the Astro process (e.g., `DIRECTUS_TOKEN`, `SITE_DOMAIN_FILTER`, `MATOMO_SITE_ID`).
    *   It executes `npm run build` within the Astro project directory using `subprocess`.
    *   It captures `stdout` and `stderr` from the build process for logging.
    *   If the subprocess returns a non-zero exit code, it logs the error, updates status to `'failed'`, and terminates.
3.  **Deploy Stage**:
    *   If the build is successful, it calls `run_rsync_deploy(build_output_path, destination_path)`.
    *   This function constructs the full `rsync` command string.
    *   It executes the command using `subprocess`.
    *   If the subprocess returns a non-zero exit code, it logs the error, updates status to `'failed'`, and terminates.
4.  **Verification Stage**:
    *   Calls GSC verification logic.
    *   Performs a simple `requests.get()` on the live URL.
5.  **Completion**:
    *   If all steps succeed, it updates the site status to `'deployed'`.
    *   Cleans up the temporary build directory.

## 3. Core Function Algorithms

### 3.1 `run_astro_build(domain, matomo_site_id)` in `deploy_site.py`

*   **Input**: `domain` (str), `matomo_site_id` (int)
*   **Output**: `bool` (Success/Failure)
*   **Logic**:
    1.  Define the path to the Astro project directory.
    2.  Define the build output directory path (e.g., `/tmp/build/{domain}`). Ensure it's clean.
    3.  Create an environment dictionary for the subprocess, including `process.env` and adding our custom variables like `SITE_DOMAIN_FILTER=domain`.
    4.  Construct the command: `['npm', 'run', 'build']`. The Astro config will be set up to use the output path.
    5.  `try`:
        *   Execute the command using `subprocess.run(..., check=True, capture_output=True, text=True, env=...)`. The `check=True` will raise an exception on a non-zero exit code.
        *   Log the `stdout` of the build process.
        *   Return `True`.
    6.  `except subprocess.CalledProcessError as e`:
        *   Log `ERROR: Astro build failed for {domain}`.
        *   Log the `stderr` from `e.stderr`.
        *   Return `False`.

### 3.2 Astro Project Data Fetching (`src/pages/index.astro`)

*   **Logic (inside Astro's frontmatter script block)**:
    1.  Read `import.meta.env.DIRECTUS_TOKEN` and `import.meta.env.SITE_DOMAIN_FILTER`.
    2.  Initialize the Directus SDK or a `fetch` client.
    3.  Construct the API query to `/items/pages`. Use the `filter` parameter to fetch only pages linked to a site where `domain` equals `SITE_DOMAIN_FILTER` AND where the page `status` is `'published'`. Use `deep` or `fields` parameters to also fetch nested `page_sections`.
    4.  The fetched data is then available to the Astro template for rendering.

### 3.3 `run_rsync_deploy(source_path, ssh_details, destination_path)` in `deploy_site.py`

*   **Input**: `source_path` (str), `ssh_details` (dict), `destination_path` (str)
*   **Output**: `bool` (Success/Failure)
*   **Logic**:
    1.  Construct the `rsync` command array: `['rsync', '-avz', '--delete', '-e', f'ssh -i {ssh_details["key_path"]}', f'{source_path}/', f'{ssh_details["user"]}@{ssh_details["host"]}:{destination_path}/']`. Note the trailing slashes.
    2.  Execute the command using `subprocess.run` as in the build step.
    3.  Handle success and failure based on the exit code.

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Orchestrator | Python 3.9+ | Runs the main deployment script. |
| SSG | Astro | To build the static website from data and templates. |
| SSG Env | Node.js, npm/yarn | To run Astro and manage its dependencies. |
| Deployment | `rsync`, `ssh` | System command-line tools for file transfer. |
| Libraries | `supabase-py`, `python-dotenv`, `subprocess` | Python dependencies. |

## 5. Security Measures

*   **SSH Key Security**: The private SSH key used for `rsync` is highly sensitive. Its path will be loaded from an environment variable. The key file itself on the server must have strict file permissions (e.g., `400` or `600`) so only the executing user can read it.
*   **Environment Segregation**: The Astro build process will receive API tokens via temporary environment variables, not command-line arguments, to prevent them from being visible in system process lists.
*   **Dependency Pinning**: Both `requirements.txt` (Python) and `package-lock.json` (Node.js) will be committed to the repository to ensure reproducible and secure builds.