# Technical Design Document: Content Engine

## 1. Architecture & Design

This module will be a Python package designed to be run as an on-demand, asynchronous task. It is likely the most complex script and should be designed with clear separation of concerns.

*   **Language**: Python 3.9+
*   **Execution Model**: The package will be triggered by a main script (`run_engine.py`) which takes a `site_id` as an argument. This script will be called by the Management Hub's task queue (Celery or FastAPI BackgroundTasks).
*   **Modular Structure**: The package will be broken into logical modules:
    *   `collectors/`: Contains modules for different data sources (e.g., `brave_collector.py`, `amazon_scraper.py`).
    *   `generators/`: Contains modules for AI interaction (e.g., `openai_generator.py`).
    *   `publishers/`: Contains the module for interacting with the Directus API (`directus_publisher.py`).
    *   `core/`: Contains main orchestration logic and data models.
*   **Configuration**: All API keys and configuration will be loaded from `.env` files. Prompt templates will be stored in separate text files (`prompts/hero_prompt.txt`) to allow for easy editing.

## 2. Data Flow & Logic

1.  **Entry Point (`run_engine.py`)**: Receives `site_id`. Initializes services (Supabase, Directus, AI clients, etc.) from config. Updates site status to `'generating'`.
2.  **Data Collection**:
    *   Orchestration logic calls various collectors in `collectors/`.
    *   Each collector gathers raw data and returns it in a standardized format.
    *   The orchestrator combines this raw data into a single, structured JSON object (a "brand profile").
    *   This "brand profile" is saved to the `brand_data` table in Supabase for auditing.
3.  **Content Generation**:
    *   The orchestrator passes the "brand profile" to the generator modules in `generators/`.
    *   The generator reads a prompt template from disk, populates it with data from the profile, and sends it to the AI API.
    *   This is repeated for each required website section.
    *   The results (generated text, image URLs) are collected into a final content object, structured to mirror the Directus data model.
4.  **CMS Population**:
    *   The orchestrator passes the final content object to the `directus_publisher.py`.
    *   The publisher connects to the Directus API and creates the `pages` and `page_sections` items, ensuring all statuses are set to `'draft'`.
5.  **Status Update**: Upon completion, the main script updates the site status in Supabase to `'generated'` or `'failed'`.

## 3. Core Function Algorithms (Conceptual)

### 3.1 `collectors.base_collector`

*   An abstract base class could define a standard interface (`fetch(brand_info)`) that all specific collectors must implement.
*   `amazon_scraper.fetch(brand_info)` would use `requests` and `BeautifulSoup4` to parse a specific Amazon store or product page.
*   `brave_collector.fetch(brand_info)` would use the Brave Search API to perform queries and return top results/snippets.

### 3.2 `generators.openai_generator`

*   `generate_section(prompt_template_path, brand_profile, section_name)`:
    1.  Reads the prompt template file.
    2.  Uses string formatting or a templating engine to inject data from `brand_profile` into the prompt.
    3.  Calls the OpenAI Chat Completions API with the final prompt.
    4.  Parses the response and returns the generated text.

### 3.3 `publishers.directus_publisher`

*   `publish_content(site_id, content_object)`:
    1.  Authenticates with the Directus API.
    2.  First, finds the Directus internal ID for the site using the `site_id` (which should match a field we created, e.g., `supabase_site_id`).
    3.  Iterates through the pages in `content_object`. For each page:
        *   Makes a `POST` request to `/items/pages` with the page data (title, slug, link to site ID).
        *   Gets the new page's ID.
    4.  Iterates through the sections for that page. For each section:
        *   Makes a `POST` request to `/items/page_sections` with the section data (content, type, variation, link to new page ID).
    5.  All API calls must include `status: 'draft'`.

## 4. Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.9+ | Core scripting language. |
| Libraries | `supabase-py` | DB interaction. |
| | `python-dotenv` | Config loading. |
| | `requests` | All direct API calls. |
| | `openai`, `google-generativeai` | AI model interaction. |
| | `beautifulsoup4` | Web scraping HTML parsing. |
| | `logging` | Structured logging. |
| APIs | Directus, Supabase, Brave, Perplexity, OpenAI, etc. | Core service integrations. |

## 5. Security Measures

*   **Credential Management**: All API keys will be loaded from environment variables. No keys in code.
*   **Scraping Ethics**: Any scraping logic must include a `User-Agent` header and respect `robots.txt` files where feasible to avoid being blocked.
*   **API Cost Control**: Implement sanity checks and potential budget limits/alerts. Log the number of tokens used per run to monitor costs.
*   **Input Sanitization**: Data scraped from the web should be treated as untrusted. While it's being used for AI prompts, ensure it is not used in a way that could lead to injection attacks against internal systems (e.g., if it were ever displayed directly in an admin panel without sanitization).