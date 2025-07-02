# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Context
This is the **Website Factory System** - an integrated platform to automate creation, deployment, and monitoring of 200+ static websites. The system consists of multiple modules working together:

- **management-hub-api** (FastAPI): Central orchestrator and API
- **management-hub-ui** (React/TypeScript): Dashboard interface  
- **dns-automator** (Python): Automates Namecheap + Cloudflare DNS setup
- **hosting-automator** (Python): Configures CloudPanel hosting + Matomo
- **content-engine** (Python): AI-powered content generation → Directus CMS
- **deployment-scripts** (Python): Astro build + rsync deployment
- **analytics-aggregator** (Python): Collects Matomo + GSC data

**CRITICAL: Always update PROJECT_STATUS.md as features are completed and verified.**
**CRITICAL: Always try to use existing documentation instead of creating new docs. You better edit the existing docs and keep them up to date than create unlimited new docs.**
**CRITICAL: Try not to hardcode any values that should be relative**

### System Architecture & Data Flow

The system follows a distributed, event-driven architecture with the Management Hub API as the central orchestrator:

```
Operator Browser (React UI) → Management Hub API (FastAPI) → On-Demand Python Scripts
                                     ↓
Central Database (Supabase) ← → External APIs (Cloudflare, Namecheap, AI, etc.)
                                     ↓
Multi-tenant Directus CMS ← → Static Site Generator (Astro) → Deployment (rsync/SSH)
```

### Core Components

#### Long-Running Services (Docker on Vultr)
- **Management Hub API** (FastAPI/Python): Central orchestrator, REST API backend with JWT auth
- **Management Hub UI** (React + shadcn/ui): SPA dashboard with real-time status updates, asynchronous task feedback
- **Directus CMS** (Node.js): Multi-tenant headless CMS managing content for 200+ sites
- **Matomo Analytics** (PHP): Self-hosted analytics with reporting API

#### On-Demand Automation Scripts (Python)
- **DNS Automator**: Namecheap nameserver updates + Cloudflare zone/record management
- **Hosting Automator**: CloudPanel site creation, SSL provisioning, Matomo site setup  
- **Content Engine**: AI-powered content generation (OpenAI/Gemini) with web data collection
- **Deployment Scripts**: Astro build process + rsync deployment over SSH
- **Analytics Aggregator**: Scheduled data collection from Matomo + Google Search Console

### Key Technologies & Integration Points

- **Database**: Supabase (PostgreSQL) - central state, credentials, and analytics storage
- **CMS**: Directus (self-hosted) - multi-tenant headless CMS for all website content
- **Static Site Generator**: Astro - builds optimized static sites from Directus content
- **Analytics**: Self-hosted Matomo + Google Search Console API integration
- **DNS/CDN**: Cloudflare (~25 accounts for distribution) + Namecheap domain management
- **Hosting**: Primary Vultr server with CloudPanel (NO API - uses CLI commands only), Docker Compose for services
- **CloudPanel CLI**: Site creation via `clpctl site:add:static`, SSL via `clpctl lets-encrypt:install:certificate`
- **Deployment**: rsync over SSH to CloudPanel document roots
- **AI Services**: OpenAI, Gemini for content generation + Brave/Perplexity for data collection

## 📝 Documentation Standards

### Documentation Hierarchy
**IMPORTANT**: When working on the project, follow this documentation priority:
1. **System-level docs** (`/docs/`): SYSTEM_PRD.md, SYSTEM_TDD.md, SYSTEM_Plan.md - High-level architecture and overall project understanding
2. **Module-level docs** (`/<module-name>/`): PRD.md, TDD.md, Plan.md - Detailed implementation specifics for each module
3. Always check module documentation for implementation details before starting work on any module

### Code Comments
- **Why over what** - explain business logic, not syntax
- **API integration notes** - document quirks, rate limits, auth methods
- **TODO comments** with context: `# TODO: Add retry logic for Cloudflare rate limits`

### PROJECT_STATUS.md Updates
**IMPORTANT**: After completing any feature or major change:
1. Update PROJECT_STATUS.md with:
   - ✅ Completed features
   - 🧪 Features ready for testing  
   - 🚧 In progress
   - ❌ Blocked/issues
2. Include **verification steps** for each completed feature
3. Note any **breaking changes** or **deployment requirements**

## ⚠️ Common Pitfalls to Avoid

- **Don't** hardcode server URLs or file paths
- **Don't** assume external APIs will always work - implement retries
- **Don't** forget to handle edge cases in async workflows
- **Always** test the full user journey, not just individual components

## Database Schema (Supabase)

### Core Tables

#### `sites` - Central website tracking
| Column | Type | Description |
|--------|------|-------------|
| `id` | `uuid` | Primary key, unique site identifier |
| `domain` | `text` | Website domain (e.g., "example.com") |
| `brand_name` | `text` | Brand name associated with site |
| `cloudflare_account_id` | `uuid` | FK to cloudflare_accounts |
| `gsc_account_id` | `uuid` | FK to gsc_accounts |
| `status_dns` | `text` | 'pending', 'active', 'failed' |
| `status_hosting` | `text` | 'pending', 'active', 'failed' |
| `status_content` | `text` | 'pending', 'generating', 'generated', 'failed' |
| `status_deployment` | `text` | 'pending', 'deploying', 'deployed', 'failed' |
| `gsc_verification_status` | `text` | 'pending', 'verified', 'failed' |
| `hosting_doc_root` | `text` | Absolute path to site root on server |
| `matomo_site_id` | `integer` | Site ID from Matomo instance |
| `error_message` | `text` | Last critical error message |

#### `cloudflare_accounts` - ~25 CF account credentials
| Column | Type | Description |
|--------|------|-------------|
| `id` | `uuid` | Primary key |
| `email` | `text` | CF account email (unique) |
| `account_nickname` | `text` | UI-friendly name (e.g., "CF_Batch_1") |
| `api_token` | `text` | Scoped CF API token |

#### `gsc_accounts` - ~5 Google Search Console accounts  
| Column | Type | Description |
|--------|------|-------------|
| `id` | `uuid` | Primary key |
| `email` | `text` | Google account email |
| `oauth_refresh_token` | `text` | OAuth 2.0 refresh token |

#### `daily_analytics` - Aggregated performance metrics
| Column | Type | Description |
|--------|------|-------------|
| `date` | `date` | Metrics date |
| `site_id` | `uuid` | FK to sites |
| `matomo_visits` | `integer` | Total Matomo visits |
| `gsc_clicks` | `integer` | Total GSC clicks |
| `gsc_impressions` | `integer` | Total GSC impressions |

### Workflow Status Tracking
Each site tracks: `status_dns`, `status_hosting`, `status_content`, `status_deployment`, `gsc_verification_status`
- **DNS/Hosting**: 'pending' → 'active' → 'failed'
- **Content**: 'pending' → 'generating' → 'generated' → 'failed'  
- **Deployment**: 'pending' → 'deploying' → 'deployed' → 'failed'

## Development Commands

**Note**: System is currently in design phase. Implementation will use:

### Management Hub API (FastAPI)
```bash
# Setup virtual environment
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn supabase python-jose passlib python-multipart python-dotenv

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Management Hub UI (React)
```bash
# Setup with Vite + shadcn/ui
npm create vite@latest management-hub-ui -- --template react-ts
cd management-hub-ui && npm install
npx shadcn-ui@latest init

# Run development server
npm run dev
```

### Python Automation Scripts
```bash
# Common dependencies for all scripts
pip install supabase-py requests python-dotenv beautifulsoup4 openai google-generativeai

# Content Engine additional deps
pip install openai google-generativeai

# Run individual scripts (triggered by Management Hub API)
python dns-automator/run_dns_setup.py --site-id <uuid>
python content-engine/run_engine.py --site-id <uuid>
python deployment-scripts/run_deployment.py --site-id <uuid>
```

### Production Deployment
```bash
# Docker Compose services on Vultr server
docker-compose up -d  # Management Hub API, UI, Directus, Matomo

# Cron job for analytics aggregation
0 2 * * * /usr/bin/python /path/to/analytics-aggregator/run_aggregator.py
```

## Workflow Architecture

### Site Creation Flow
1. Operator adds site via Management Hub UI
2. DNS Automator configures Namecheap nameservers + Cloudflare zone
3. Hosting Automator sets up CloudPanel site + SSL + Matomo tracking
4. Content Engine generates AI content → saves to Directus as drafts
5. Operator reviews/edits content in Directus CMS
6. Deployment Scripts build Astro site + deploy via rsync

### Asynchronous Task Handling
- Management Hub API uses FastAPI BackgroundTasks (v1) or Celery (future)
- All automation scripts are stateless, triggered on-demand
- Status updates tracked in Supabase for UI feedback
- Error states captured in `error_message` field

## Security Architecture

- All API keys/secrets stored in Supabase, loaded via environment variables
- JWT authentication for Management Hub API
- Principle of least privilege for all API tokens
- SSH key-based authentication for deployments
- CORS configured for frontend domain only

## Multi-Tenant Content Strategy

- Single Directus instance manages content for all 200+ sites
- Content linked to sites via relational fields
- AI-generated content starts as 'draft', requires manual publish
- Astro builds only fetch 'published' content per domain

## Integration Points

### External APIs
- **Namecheap API**: Domain nameserver management
- **Cloudflare API**: DNS zone/record management (25 accounts)
- **Google APIs**: Search Console data + Site Verification
- **OpenAI/Gemini**: Content generation
- **Brave/Perplexity**: Data collection for content context

### Internal Services
- **Supabase**: Primary database and auth
- **Directus**: Headless CMS with webhook triggers
- **Matomo**: Self-hosted analytics with reporting API

## Core User Workflows & Stories

### Site Creation Flow
1. Operator adds site via Management Hub UI (single or bulk CSV upload)
2. DNS Automator configures Namecheap nameservers + Cloudflare zone
3. Hosting Automator sets up CloudPanel site + SSL + Matomo tracking
4. Content Engine generates AI content → saves to Directus as drafts
5. Operator reviews/edits content in Directus CMS
6. Deployment Scripts build Astro site + deploy via rsync

### Key User Stories (from PRD)
- **US-002**: Add single site via form with Cloudflare account selection
- **US-003**: Bulk add sites via CSV upload (domain, cloudflare_account_nickname)
- **US-005**: Trigger AI content generation with single click → status feedback
- **US-006**: Deploy website with single click → progress indicators
- **US-007**: Direct link to site content in Directus CMS
- **US-008**: Analytics dashboard with Matomo + GSC aggregated data
- **US-009**: Filter analytics by date ranges (Today, 7/30 days, Custom)

## Security Architecture

- **Credential Management**: All API keys stored in Supabase, loaded via environment variables
- **Authentication**: JWT auth for Management Hub API, key-based SSH for deployments  
- **Network Security**: Vultr server firewall, HTTPS/SSL for all web services
- **API Security**: Scoped tokens (principle of least privilege), input validation with Pydantic
- **Application Security**: Regular security updates, dependency vulnerability scanning

## Error Handling & Monitoring

- **Centralized Logging**: Python logging library with structured logs (timestamp, level, module, context)
- **Failure State Tracking**: Failed workflows update status fields + populate error_message
- **API Retry Logic**: Exponential backoff for external service failures
- **User-Friendly Errors**: Clear JSON responses with appropriate HTTP status codes
- **Failure Isolation**: One site failure doesn't affect others

## Development Roadmap (8-12 weeks)

### Phase 1: Foundation & Infrastructure (2-3 weeks)
- **Week 1**: Supabase database schema + Vultr server setup with CloudPanel
- **Week 2**: Docker Compose setup (Directus, Matomo) + credential management
- **Week 3**: DNS Automator + Hosting Automator scripts with API integrations

### Phase 2: Core Application & Content Workflow (3-4 weeks)  
- **Week 4-5**: Management Hub API (FastAPI) with auth + site management endpoints
- **Week 6**: Management Hub UI (React) with dashboard + workflow triggers
- **Week 7**: Content Engine with AI integration + Directus publishing

### Phase 3: Analytics & Integration (2-3 weeks)
- **Week 8**: Deployment Scripts (Astro build + rsync) + webhook integration
- **Week 9**: Analytics Aggregator + Analytics dashboard UI
- **Week 10**: GSC verification automation + error handling refinement

### Phase 4: Beta Testing & Hardening (1-2 weeks)
- **Week 11**: End-to-end testing with 10-20 sites + performance tuning
- **Week 12**: Bug fixes + documentation + production deployment

## Error Handling Strategy

- Structured logging across all modules (timestamp, level, module, context)
- Failed workflows update status fields + populate error_message
- API retry logic with exponential backoff for external services
- Failure isolation (one site failure doesn't affect others)
- User-friendly error display in Management Hub UI

## 🔄 Background Tasks & Async Patterns

### Task Execution
- Use **FastAPI BackgroundTasks** for simple async operations
- **Subprocess calls** for external scripts: `subprocess.run(['python', 'script.py'])`
- **Status tracking** - always update database status before/after operations
- **Graceful failure** - never let one site's failure block others

## 🔐 Security Requirements

### Credential Management
- **NEVER** commit API keys, tokens, or passwords
- Use `.env` files (gitignored) for local development
- Store production credentials in Supabase securely
- Load credentials via `os.getenv()` with validation

### API Security
- **Always** validate input with Pydantic schemas
- Use **JWT tokens** for authentication
- **Rate limiting** on public endpoints
- **CORS** properly configured for production

### External API Best Practices
- **Retry logic** with exponential backoff for transient failures
- **Timeout settings** for all HTTP requests
- **API key rotation** support in credential management
- **Scoped permissions** - minimum required access for each service