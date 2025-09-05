# Project Implementation To-Do List

This document tracks the full implementation plan for the parking reservation application as specified in `README.md`.

Status Legend: ❌ Not Started | 🚧 In Progress | ✅ Done | 🔍 Under Review | ⏳ Deferred

---

## Phase 1: Repository Bootstrap & Core Setup

### 1.1 Repository Bootstrap
- Task: Create project folder structure (see README Architecture)
  - Files: `app/`, `tests/`, `migrations/`, `config/`, `static/`, `templates/`, `services/`, `api/`, `cli/`
  - Status: ❌
- Task: Add `requirements.txt` with pinned baseline dependencies
  - Status: ❌
- Task: Add `.env.example` with all documented variables
  - Status: ❌
- Task: Implement `config/settings.py` (Dev / Test / Prod classes)
  - Status: ❌
- Task: Flesh out `README` Quick Start from planned → actionable
  - Status: ❌

### 1.2 Application Factory & Extensions
- Task: Implement `create_app` factory in `app/__init__.py`
  - Status: ❌
- Task: Add `extensions.py` (db, migrate, login_manager, csrf, limiter placeholder)
  - Status: ❌
- Task: Configure logging (basic formatter) in factory
  - Status: ❌
- Task: Add global error handler scaffold
  - Status: ❌

---

## Phase 2: Data Layer (Models & Migrations)
- Task: Implement models (`ParkingSpot`, `Reservation`, `User`, `Action`)
  - Include UNIQUE `(spot_id, reservation_date)`
  - Status: ❌
- Task: Add indices (reservation_date, spot_id)
  - Status: ❌
- Task: Initial Alembic migration
  - Status: ❌
- Task: Model unit tests (constraints, relationships)
  - Status: ❌

---

## Phase 3: Security & Authentication Core
- Task: Implement password hashing (Werkzeug) in User model/service
  - Status: ❌
- Task: Session login/logout endpoints (`/api/v1/auth/login`, `/api/v1/auth/logout`)
  - Status: ❌
- Task: Protect session-only endpoints with login required
  - Status: ❌
- Task: (Planned) CSRF integration strategy finalized
  - Status: ❌

---

## Phase 4: Service Layer
- Task: `reservation_service.py` (create/update/cancel/list with conflict handling)
  - Status: ❌
- Task: `spot_service.py` (availability/filter logic by date/status)
  - Status: ❌
- Task: `user_service.py` (auth helpers, current user retrieval)
  - Status: ❌
- Task: `audit_service.py` (uniform action logging interface)
  - Status: ❌

---

## Phase 5: API Layer (Blueprint `api`)
- Task: Register `api` blueprint at `/api/v1`
  - Status: ❌
- Task: Health endpoint (`/api/v1/health`)
  - Status: ❌
- Task: Spots endpoints (`/api/v1/spots`, `/api/v1/spots/<id>`)
  - Status: ❌
- Task: Reservations endpoints (CRUD)
  - Status: ❌
- Task: User profile endpoint (`/api/v1/users/me`)
  - Status: ❌
- Task: Audit list endpoint (`/api/v1/actions` with pagination + admin check)
  - Status: ❌

---

## Phase 6: Validation & Error Handling
- Task: Choose schema library (Marshmallow or Pydantic) and integrate
  - Status: ❌
- Task: Implement request/response schemas (reservations, spots, auth)
  - Status: ❌
- Task: Add `ApiError` base + global JSON error handler mapping codes
  - Status: ❌
- Task: Map IntegrityError → `RESERVATION_CONFLICT`
  - Status: ❌

---

## Phase 7: Frontend Shell & Hydration
- Task: Create base templates (`base.html`, `index.html`, `login.html`)
  - Status: ❌
- Task: Implement `static/js/main.js` and per-feature modules (spots/reservations)
  - Status: ❌
- Task: Add minimal CSS scaffold (Bootstrap inclusion)
  - Status: ❌
- Task: Client-side fetch + DOM population for spots list
  - Status: ❌

---

## Phase 8: Logging & Audit Enhancements
- Task: Structured logging fields (request_id, user_id) injection middleware
  - Status: ❌
- Task: Implement action logging on reservation create/update/delete & auth events
  - Status: ❌
- Task: Add retention plan placeholder (archival interface)
  - Status: ❌

---

## Phase 9: Testing Infrastructure
- Task: `pytest` configuration & `conftest.py` fixtures (app, client, db, factories)
  - Status: ❌
- Task: Factory classes for each model (factory-boy)
  - Status: ❌
- Task: API integration tests (happy + failure paths for each endpoint)
  - Status: ❌
- Task: Coverage threshold enforcement (>=80%)
  - Status: ❌
- Task: Conflict scenario test (double-book attempt)
  - Status: ❌

---

## Phase 10: Tooling & Quality Gates
- Task: Add `.pre-commit-config.yaml` (black, isort, flake8, mypy, trailing whitespace)
  - Status: ❌
- Task: Add `mypy.ini` (incremental strictness)
  - Status: ❌
- Task: Lint + type-check integration into CI
  - Status: ❌

---

## Phase 11: Rate Limiting & Security Hardening
- Task: Integrate Flask-Limiter (login + reservation create)
  - Status: ❌
- Task: Add Flask-Talisman (dev relaxed / prod strict CSP & HSTS)
  - Status: ❌
- Task: Tests for 429 after threshold exceeded
  - Status: ❌

---

## Phase 12: OpenAPI Documentation
- Task: Add generator (flask-smorest or apispec integration)
  - Status: ❌
- Task: Expose `/api/v1/openapi.json` & Swagger UI/ReDoc
  - Status: ❌
- Task: Snapshot contract test (schema drift detection)
  - Status: ❌

---

## Phase 13: CLI & Data Seeding
- Task: Implement CLI group for seeding (`flask seed admin`, `flask seed demo-data`)
  - Status: ❌
- Task: Idempotency tests for seed commands
  - Status: ❌

---

## Phase 14: Deployment & CI/CD
- Task: GitHub Actions workflow (`ci.yml`: install, lint, type, test, coverage)
  - Status: ❌
- Task: Dockerfile + docker-compose (app + SQLite/Postgres option)
  - Status: ❌
- Task: Gunicorn config file (`gunicorn_conf.py`)
  - Status: ❌
- Task: Healthcheck integration (Docker compose)
  - Status: ❌

---

## Phase 15: Performance & Observability
- Task: Query count tests (avoid N+1 on reservations list)
  - Status: ❌
- Task: Add correlation/request ID middleware
  - Status: ❌
- Task: (Optional) Sentry integration toggle via env
  - Status: ❌

---

## Phase 16: Internationalization & Accessibility (Future)
- Task: Evaluate Flask-Babel integration plan
  - Status: ⏳
- Task: Accessibility pass (ARIA roles, focus states, contrast)
  - Status: ⏳

---

## Phase 17: Policy Enforcement
- Task: Template policy lint script (detect large JSON blocks)
  - Status: ❌
- Task: Add script to CI pipeline
  - Status: ❌

---

## Phase 18: Legal & Contribution
- Task: Add MIT `LICENSE`
  - Status: ❌
- Task: Add PR & issue templates
  - Status: ❌
- Task: Update README statuses as features complete
  - Status: ❌

---

## Stretch Goals (Backlog)
- PWA manifest & offline shell
- WebSocket push (spot updates)
- Redis caching layer for availability queries
- Metrics endpoint (Prometheus exporter)
- Idempotency keys for reservation creation

---

## Cross-Cutting Test Requirements Summary
- Every API endpoint: success + failure + permission test
- Services: logic + conflict simulation
- Models: constraints + relationship integrity
- Auth: invalid credentials, session persistence, logout
- Validation: 422 on malformed inputs
- Logging: verify structured fields present
- Rate limiting: 429 after limit
- OpenAPI: contract snapshot stays stable
- Performance: query count threshold (optional gate)
- Policy: template linter passes

---

## Update Process
1. When a task starts: change status to 🚧.
2. On completion: mark ✅ and, if applicable, update README status markers.
3. If scope changes: append clarification below the task.
4. Keep this file in sync with actual implementation state in each PR.

---

## Recent Changes Log
*(Add dated entries as tasks move to Done)*

---

## Notes
This file is a living implementation tracker. The authoritative functional specification remains `README.md`; discrepancies should be resolved immediately.
