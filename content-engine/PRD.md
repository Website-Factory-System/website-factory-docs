# PRD: Content Engine

## 1. Product overview
### 1.1 Document title and version
*   PRD: Content Engine
*   Version: 1.0

### 1.2 Product summary
This document details the product requirements for the Content Engine, the most complex and intelligent module in the Website Factory system. Its purpose is to automate the creation of initial website content by performing large-scale data collection and leveraging generative AI. The engine is designed to be a powerful, asynchronous service that can be triggered on a per-site basis from the Management Hub.

The process involves two main stages. First, the Data Collection stage uses search APIs and targeted scraping to gather a rich dataset about a given brand or product. Second, the Content Generation stage feeds this structured data into AI models with sophisticated prompts to produce unique text and identify image needs for predefined website sections. The final, generated content is then programmatically saved into the central Directus Headless CMS, ready for review and deployment.

## 2. Goals
### 2.1 Business goals
*   Massively reduce the time and cost associated with manual content writing and research.
*   Enable the creation of content for hundreds of sites at a scale impossible for human writers alone.
*   Ensure a baseline level of unique, relevant content for every site to improve initial SEO value.

### 2.2 User goals
*   As an operator, I want to trigger a comprehensive content creation process for a site with a single click.
*   As an operator, I want the generated content to be structured, relevant to the site's topic, and ready for minor edits.
*   As an operator, I want the system to handle both text generation and identifying image requirements.

### 2.3 Non-goals
*   This engine will not produce perfectly polished, ready-to-publish content 100% of the time. Operator review is expected.
*   This engine will not perform ongoing content updates or blog post writing. It is for initial site population only.
*   This engine will not manage content localization or translation.
*   This engine will not fine-tune AI models; it will use existing foundation models via their APIs.

## 3. User personas
### 3.1 Key user types
*   System (invoked by Management Hub)

### 3.2 Basic persona details
*   **System**: A non-interactive module triggered asynchronously by the Management Hub API.

### 3.3 Role-based access
*   Not applicable.

## 4. Functional requirements
*   **Data Collection** (Priority: High)
    *   The engine must accept a `site_id` as input to identify the target brand/domain.
    *   It must use search APIs (e.g., Brave, Perplexity) to gather general information, news, and find key pages (e.g., Amazon store, social media profiles).
    *   It must be able to perform targeted data extraction from specified sources (e.g., scrape product features from an Amazon page, get info from Justia trademarks).
*   **Data Structuring** (Priority: High)
    *   The engine must process the raw collected data into a structured format (e.g., JSON).
    *   This structured data should be saved to a database (e.g., Supabase `brand_data` table) for traceability and potential reuse.
*   **AI Content Generation** (Priority: High)
    *   The engine must use the structured data to dynamically build prompts for generative AI models (e.g., OpenAI, Gemini).
    *   It must generate text for a predefined set of website sections (e.g., Hero headline, About Us paragraph, Feature list, Contact details).
    *   It must identify image needs, which could involve sourcing existing image URLs or generating prompts for AI image models.
*   **CMS Population** (Priority: High)
    *   The engine must connect to the Directus CMS API.
    *   It must format the generated content to match the pre-configured Directus data model (collections for `pages`, `page_sections`).
    *   It must create the corresponding page and section items in Directus, linking them to the correct site.
    *   All content created in Directus must be set to a 'draft' status by default.
*   **Status Reporting** (Priority: High)
    *   The engine must update the `status_content` field in the Supabase `sites` table to 'generating', 'generated', or 'failed' throughout its lifecycle.

## 5. User experience
### 5.1. Entry points & first-time user flow
*   Not applicable.

### 5.2. Core experience
*   Not applicable.

### 5.3. Advanced features & edge cases
*   **Partial Success**: If data collection from one source fails, the engine should proceed with the data it has, logging a warning.
*   **Prompt Templating**: The prompts used for AI generation should be stored in a configurable way (e.g., template files) to allow for easy tweaking without changing the code.
*   **Content Variability**: The engine should incorporate mechanisms to ensure content is unique across different sites, such as varying prompts or using different AI model parameters (e.g., temperature).

### 5.4. UI/UX highlights
*   Not applicable.

## 6. Narrative
The operator clicks "Generate" for "new-site.com" in the Management Hub. This action awakens the Content Engine. First, the engine's data collectors scour the web, using Brave and Perplexity APIs to learn about the "new-site" brand, finding its Amazon page and social media chatter. It structures this research into a clean dataset. Then, its AI core uses this dataset to craft compelling text for the homepage hero, a detailed about page, and product feature blurbs, all via the OpenAI API. Finally, it logs into the Directus CMS as a bot, creates the necessary pages and content blocks, fills them with the newly written text, and sets everything to 'draft'. It reports its success back to the central database before going back to sleep.

## 7. Success metrics
### 7.1. User-centric metrics
*   Not applicable.

### 7.2. Business metrics
*   Cost per site for content generation (API usage costs).
*   Time taken for the end-to-end content process per site.

### 7.3. Technical metrics
*   Success rate of data collection from primary sources.
*   API error rates for AI and data source APIs.
*   Subjective quality score of generated content (to be evaluated periodically by the operator).

## 8. Technical considerations
### 8.1. Integration points
*   Supabase Database API (read site info, write status, write structured data).
*   Data Source APIs (Brave, Perplexity).
*   Generative AI APIs (OpenAI, Gemini, etc.).
*   Directus CMS API (write content).
*   Web scraping libraries might be used for sources without APIs.

### 8.2. Data storage & privacy
*   Handles numerous sensitive API keys. Must use secure environment variable loading.
*   Collected data is public information. No user PII is processed.

### 8.3. Scalability & performance
*   This is the most computationally and time-intensive part of the workflow. Running it asynchronously is non-negotiable.
*   Scalability depends on API rate limits of external services and the ability to run multiple instances of the engine in parallel if needed (using a proper task queue like Celery).

### 8.4. Potential challenges
*   **AI Quality & "Hallucinations"**: Generated content can be inaccurate or nonsensical, requiring operator review.
*   **Changing Website Structures**: If data sources (e.g., Amazon) change their website HTML, scraping logic will break.
*   **Cost Management**: Uncontrolled use of high-end AI models can become very expensive.
*   **Prompt Engineering**: Achieving consistently good results requires significant investment in crafting and refining prompts.

## 9. Milestones & sequencing
### 9.1. Project estimate
*   Medium: 2-3 weeks

### 9.2. Team size & composition
*   1-2 Backend Engineers

### 9.3. Suggested phases
*   **Phase 1**: Develop the CMS population logic. Manually create JSON data and ensure it can be correctly inserted into Directus via API.
*   **Phase 2**: Develop the AI generation stage. Use static, structured data to test prompt templates and AI model interactions.
*   **Phase 3**: Develop the data collection stage. Integrate search APIs and scraping logic to dynamically create the structured data.
*   **Phase 4**: Integrate all stages and connect with Supabase for status updates.

## 10. User stories
*   **ID**: US-CONT-001
*   **Description**: As the system, I want to collect data about a specified brand from multiple online sources.
*   **Acceptance criteria**:
    *   The script uses the site's domain/brand name as a query.
    *   The script successfully calls at least one search API (e.g., Brave).
    *   The script can extract text content from specified URLs returned by the search API.
    *   The collected raw data is stored temporarily for processing.
*   **ID**: US-CONT-002
*   **Description**: As the system, I want to generate unique text content for predefined website sections using an AI model.
*   **Acceptance criteria**:
    *   The script authenticates with at least one generative AI API (e.g., OpenAI).
    *   The script uses structured data to build dynamic prompts.
    *   The script successfully generates text for a 'hero' section and an 'about' section.
    *   The generated text is stored in memory or a local variable.
*   **ID**: US-CONT-003
*   **Description**: As the system, I want to save the generated content into the Directus CMS as a draft.
*   **Acceptance criteria**:
    *   The script authenticates with the Directus API.
    *   The script creates a new `pages` item for the homepage, linked to the correct `sites` item.
    *   The script creates `page_sections` items with the generated text and links them to the new page.
    *   All created items in Directus have their `status` field set to 'draft'.
*   **ID**: US-CONT-004
*   **Description**: As the system, I want to report the status of the content generation process to the central database.
*   **Acceptance criteria**:
    *   Before starting, the script updates the `status_content` in Supabase to 'generating'.
    *   Upon successful completion, the status is updated to 'generated'.
    *   If a critical, unrecoverable error occurs, the status is updated to 'failed' and an error message is logged.