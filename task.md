# Email Campaign Management System Refactor Tasks

- `[x]` Delete old SQLite database to start fresh with UUIDs
- `[x]` **Configuration & Deployment**
  - `[x]` Update `app/config.py` (add SMTP & APP_DOMAIN)
  - `[x]` Update `.env.example`
  - `[x]` Create `docker-compose.yml`
- `[x]` **Database Layer**
  - `[x]` Update `app/models.py` (UUIDs, new models `SendingLog`, `SuppressionList`, update `Subscriber`, `Campaign`)
  - `[x]` Update `app/schemas.py`
- `[x]` **Core Deliverability & Email Service**
  - `[x]` Update `app/services/security.py` (HMAC for unsubs)
  - `[x]` Update `app/services/email.py` (`smtplib` + multipart/alternative + RFC 8058 headers)
- `[x]` **Celery Dispatch Engine**
  - `[x]` Update `app/worker.py` (query filters, rate limits, `SendingLog` updates)
- `[x]` **API Endpoints & Admin UI**
  - `[x]` Update `app/main.py` (add `/healthz`)
  - `[x]` Update `app/routers/api.py` (upload CSV, webhooks, launch, test, unsubscribe HMAC)
  - `[x]` Update `app/routers/admin.py` (UUID updates, queries)
  - `[x]` Update `app/templates/*.html` (Tailwind, HTMX/Alpine.js snippets)
