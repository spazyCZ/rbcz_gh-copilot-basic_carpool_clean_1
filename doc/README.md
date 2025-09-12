# Documentation Hub

Central index for all generated project documentation. All files derived strictly from repository source at generation time.

## Index

| Doc | Purpose |
|-----|---------|
| `architecture.md` | High-level system architecture, layers, dependencies |
| `business_logic.md` | Core use cases, rules, lifecycles |
| `domain_model.md` | Entity descriptions & relationships |
| `database_structure.md` | Physical schema, migrations, integrity notes |
| `api_spec.yaml` | OpenAPI 3.0 spec for JSON endpoints |
| `auth_security.md` | Authentication, authorization, security posture |
| `user_flow_diagrams.md` | End-to-end user interaction flows |

## Quick Start

1. Create virtual environment (Python 3.9+).
2. Install dependencies from `requirements.txt`.
3. Set environment variables (see below).
4. Run database migrations (Flask-Migrate or manual create_all if bootstrap phase).
5. Launch app with `FLASK_APP=run.py flask run` or `python run.py` (if factory wrapper present).

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session & CSRF secret | `change-me-prod` |
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite:///carpool.db` |
| `FLASK_ENV` | Environment mode | `development` |
| `FLASK_DEBUG` | Enable debugger (dev only) | `1` |

## Testing

Run pytest (unit + integration). New endpoints must include tests under `tests/` per contribution guidelines.

## Notable Gaps / Technical Debt Summary

| Area | Gap | Reference Doc |
|------|-----|---------------|
| Carpool passenger model | Missing join table & logic mismatch | `domain_model.md`, `user_flow_diagrams.md` |
| Reservation uniqueness | No unique (spot_id, date) constraint | `database_structure.md` |
| Security hardening | Missing rate limiting, CSRF on JSON | `auth_security.md` |
| Consistent cancellation semantics | Reservation status vs delete | `business_logic.md` |

## Suggested Next Steps

| Priority | Action | Benefit |
|----------|--------|---------|
| High | Implement passenger membership schema | Accurate capacity & audit |
| High | Add DB uniqueness + indexes | Prevent double booking |
| High | Harden session & CSRF for JSON writes | Reduce attack surface |
| Medium | Add API test coverage (mutation endpoints) | Reliability & regression safety |
| Medium | Normalize cancellation audit strategy | Consistent reporting |
| Low | Add observability (structured logs) | Easier diagnostics |

## Conventions

* Service layer encapsulates business logic (`carpool/services/`).
* Blueprints separate domain concerns (`views/`).
* Forms handle validation (WTForms) for HTML flows.
* JSON endpoints return uniform `{success: bool, ...}` or arrays.

## Changelog (Docs)

| Date | Change |
|------|--------|
| 2025-09-12 | Initial comprehensive documentation generation |

## Contact / Ownership

Maintain internal ownership mapping separately; not stored in code. Update this hub when structural changes occur (new model, service, or security control).

All documentation sections are synchronized to code realities at generation; revisit after each schema or route change.
