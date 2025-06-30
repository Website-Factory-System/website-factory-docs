# Technical Design Document: Hosting Automator

## 1. Architecture & Design

This module is a stateless Python script, executed on-demand by the Management Hub API. Its architecture is now centered around remote command execution over SSH, as CloudPanel lacks a suitable REST API for site creation.

*   **Language**: Python 3.9+
*   **Execution Model**: Command-line script (`python hosting_manager.py`).
*   **Remote Execution**: The script will use the **`paramiko`** Python library to establish a secure SSH connection to the Vultr server. It will execute `clpctl` (CloudPanel CLI) commands remotely.
*   **Configuration**: Secrets (Supabase keys, Matomo API info, SSH host/user/key details) will be loaded from an `.env` file using `python-dotenv`.

## 2. Data Flow & Logic

1.  **Initialization**:
    *   Load environment variables from `.env` (SUPABASE_URL, SUPABASE_SERVICE_KEY, MATOMO_API_URL, MATOMO_API_TOKEN, **SSH_HOST, SSH_USER, SSH_KEY_PATH**).
    *   Initialize Supabase client. Configure `logging`.
2.  **Fetch Work**:
    *   Query Supabase: `SELECT * FROM sites WHERE status_dns = 'active' AND status_hosting = 'pending'`.
    *   If no rows, log and exit.
3.  **Process Loop**:
    *   Establish a persistent SSH connection to the Vultr server using `paramiko`.
    *   Iterate through each pending `site`.
    *   Log `INFO: Processing hosting for {site.domain}`.
    *   Generate a secure, random password for the new site user.
    *   Call `create_cloudpanel_site()` function, passing the SSH client, site details, and generated password. If it returns `False`, update status to 'failed', log the error, and continue to the next site.
    *   Call `create_matomo_site()`. Store the returned `matomo_id`.
    *   Construct the `hosting_doc_root` path based on the known pattern.
    *   Call `update_status_in_db()` with 'active' and the retrieved metadata.
4.  **Completion**: Close the SSH connection.

## 3. Core Function Algorithms

### 3.1 `execute_remote_command(ssh_client, command)`

*   **Input**: `ssh_client` (a connected `paramiko.SSHClient` object), `command` (str)
*   **Output**: `tuple` (`stdout_str`, `stderr_str`, `exit_code`)
*   **Logic**:
    1.  `try`:
        *   Execute `stdin, stdout, stderr = ssh_client.exec_command(command)`.
        *   Read the output: `stdout_str = stdout.read().decode().strip()`, `stderr_str = stderr.read().decode().strip()`.
        *   Get the exit status: `exit_code = stdout.channel.recv_exit_status()`.
        *   Log the command and its `exit_code`. If `stderr_str` is not empty, log it as a `WARNING` or `ERROR`.
        *   Return `(stdout_str, stderr_str, exit_code)`.
    2.  `except Exception as e`:
        *   Log `CRITICAL: SSH command execution failed: {e}`.
        *   Return `(None, str(e), -1)`.

### 3.2 `create_cloudpanel_site(ssh_client, site, password)`

*   **Input**: `ssh_client` object, `site` object, `password` (str)
*   **Output**: `bool` (Success/Failure)
*   **Logic**:
    1.  Generate a unique and sanitized `userName` for the site (e.g., `user_{site.domain.replace('.', '')[:10]}`).
    2.  **Sanitize Inputs**: Before building commands, validate `site.domain` and the generated `userName` to contain only safe alphanumeric characters (`a-z`, `A-Z`, `0-9`, `-`, `.`) to prevent command injection.
    3.  **Create User**: Construct the command string: `f"clpctl user:add --userName='{userName}' --firstName='Site' --lastName='{site.domain}' --password='{password}' --state='active'"`. Call `execute_remote_command()`. If `exit_code != 0`, log `stderr`, store error, and return `False`.
    4.  **Create Static Site**: Construct the command string: `f"clpctl site:add:static --domainName='{site.domain}' --siteUser='{userName}' --phpVersion='8.2' --vhostTemplate='Static'"`. Call `execute_remote_command()`. If `exit_code != 0`, log `stderr`, store error, and return `False`.
    5.  **Add SSL**: Construct the command string: `f"clpctl ssl:add:lets-encrypt --domainName='{site.domain}'"`. Call `execute_remote_command()`. If `exit_code != 0`, log `stderr`, store error, and return `False`.
    6.  Log `INFO: Successfully created CloudPanel site for {site.domain}`.
    7.  Return `True`.

### 3.3 `create_matomo_site(domain)`

*   *(This function's logic is unchanged from the previous TDD, as it uses the Matomo REST API.)*

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.9+ | Core scripting language. |
| Libraries | `supabase-py` | Interaction with Supabase database. |
| | `python-dotenv` | Loading configuration from `.env` files. |
| | **`paramiko`** | **For making SSH connections and executing remote commands.** |
| | `requests` | For making HTTP API calls to Matomo. |
| | `logging` | Standard library for structured logging. |
| APIs & CLIs| **CloudPanel CLI (via SSH)**, Matomo Reporting API | Core service integrations. |

## 5. Security Measures

*   **SSH Key Management**: The private SSH key used to connect to the Vultr server is extremely sensitive. Its path will be loaded from an environment variable. The key file itself on the server must have strict file permissions (`400` or `600`) so only the executing user can read it.
*   **Command Injection**: **This is the highest risk.** All variables (`domain`, `userName`, `password`) used to construct CLI command strings **MUST be strictly validated and sanitized** using a whitelist of allowed characters (e.g., regex `^[a-zA-Z0-9.-]+$`). Never pass raw input directly into a command string. Python's `shlex.quote()` should be used on each parameter to make it safe for shell execution.
*   **Root Access**: The script will connect as a user with `sudo` privileges or as `root` to run `clpctl`. This connection must be carefully secured. Consider creating a specific automation user with passwordless `sudo` access scoped *only* to the `/usr/local/bin/clpctl` command to limit privileges.
*   **Credential Management**: Matomo API token will be loaded from the `.env` file. No secrets will be hardcoded.