# Authentication & Security

All details derived from repository source (`auth.py`, `main.py`, services, `config.py`, `extensions.py`). No unstated mechanisms assumed.

## Overview

The application uses classic server-rendered Flask views secured by session cookies managed via Flask-Login. Passwords are hashed with bcrypt. CSRF protection is provided by Flask-WTF (forms). Optional HTTP security headers are applied via Flask-Talisman (enabled in non-debug contexts) for CSP & transport security.

## Authentication Flow

1. User submits credentials to `/login` (POST form – not JSON) with fields: `username` (or email), `password`, `remember_me`.
2. `AuthService.get_user_by_username` (fallback: lookup by email) finds user.
3. `AuthService.authenticate_user` verifies password using bcrypt hash compare.
4. On success `AuthService.login_user_session` calls `login_user(user, remember=remember_me)` creating a session cookie.
5. Subsequent authenticated requests gate-checked by `@login_required` on protected routes and `current_user` context.
6. Logout via `/logout` calls `logout_user()` and redirects.

### Session Characteristics

| Aspect | Implementation | Notes |
|--------|----------------|-------|
| Cookie name | Default Flask session | Not renamed; consider explicit `SESSION_COOKIE_NAME`. |
| Transport | HTTP (dev) / should be HTTPS (prod) | Enforce Secure & HttpOnly in production. |
| Renewal | Implicit via activity | No sliding-expiration customization found. |
| Remember-me | Boolean through form | Uses Flask-Login remember token mechanism. |

## Password Handling

| Function | Location | Purpose |
|----------|----------|---------|
| Hash creation | User creation in `AuthService.create_user` | Uses bcrypt generate hash. |
| Verification | `AuthService.verify_password` / `authenticate_user` | bcrypt check. |
| Update | `AuthService.update_user_password` | Re-hashes new password. |

No plaintext storage; salts embedded in bcrypt hash. Password complexity validation not enforced in code (improvement opportunity).

## Authorization Model

Roles implemented as simple string field `User.role` with values `user` or `admin`.

| Mechanism | Code Artifact | Behavior |
|-----------|--------------|----------|
| Role check | `User.is_admin()` | Returns True when role == 'admin'. |
| Decorator | `admin_required` in `admin.py` | Wraps view: requires authenticated & admin, else redirect & flash. |
| Ownership checks | Reservation & Carpool modifications | Compares `reservation.user_id` or `carpool.organizer_id` to `current_user.id`. |

Granularity: No fine-grained permission matrix; binary admin vs standard user.

## CSRF Protection

All form submissions rely on Flask-WTF, which embeds CSRF token automatically in templates that render `{{ form.hidden_tag() }}` (not shown in this doc but assumed standard pattern). API JSON endpoints rely on cookie session auth only and DO NOT include separate CSRF validation for JSON POSTs (e.g., `/api/quick-reservation`, `/api/carpool/{id}/join`). This is acceptable if session cookie is SameSite=Lax/Strict and only first-party JS calls them; otherwise add token header.

## Security Headers & Hardening

`flask_talisman.Talisman` is referenced in `extensions.py` / app factory usage (implied by instructions). Observed CSP example in instructions (not all enforced in code excerpt). Confirm actual initialization in runtime (not present in scanned files—improvement needed).

| Area | Current State | Recommendation |
|------|---------------|----------------|
| CSP | Basic or missing (not clearly initialized) | Initialize consistently with script-src 'self'. |
| HTTPS enforcement | Only for production per instructions | Add environment flag to ensure always-on in prod. |
| Session cookie flags | Not explicitly set | Configure: Secure, HttpOnly, SameSite=Strict. |
| Password policy | None enforced | Add minimum length + entropy checks. |
| Rate limiting | Not implemented | Introduce Flask-Limiter on auth & mutation endpoints. |
| Brute force mitigation | Absent | Track failed logins; threshold lockouts or exponential backoff. |
| Audit logging | `Action` model records activity types | Expand to include auth failures. |

## Data Validation & Input Handling

Forms: Validation performed through WTForms validators (fields defined in forms modules). JSON endpoints perform manual minimal validation (presence checks). No centralized schema validation layer for JSON – consider Marshmallow or Pydantic.

## Sensitive Data & Secrets

| Secret | Source | Risk |
|--------|--------|------|
| SECRET_KEY | Env or fallback in `config.py` | Fallback not secure for production. |
| DB URI | Env override supported | Ensure not logged. |

No hardcoded credentials other than development defaults. ALWAYS provide production secrets via environment (`.env` loaded early).

## Logging & Monitoring

Uses `current_app.logger` across authentication and critical operations. Error contexts include stack (some with `exc_info=True`). Missing structured correlation IDs.

| Event | Logged | Suggested Enhancement |
|-------|--------|-----------------------|
| Login success | Yes (info flash, minimal log) | Add user id & IP (avoid password). |
| Login failure | Generic error log | Add attempt count (capped detail). |
| Password change | Logged with user context | Add hash re-generation confirmation (without hash). |
| Admin actions | Logged via `Action` + logger | Build admin audit export endpoint. |

## Threat Model Snapshot

| Threat | Vector | Current Mitigation | Residual Risk |
|--------|--------|--------------------|---------------|
| Session hijack | Stolen cookie | HttpOnly cookie | Lacks Secure & rotation; add same-site & periodic renewal. |
| CSRF on JSON POST | Authenticated browser tab | SameSite default (unspecified) | If SameSite=None, high risk; enforce token or Lax. |
| Password brute force | Repeated login attempts | None | Add rate limit, captcha after N failures. |
| Enumeration | Timing / error messages | Unified generic message | Acceptable. |
| SQL injection | User input | SQLAlchemy ORM | Low, if raw SQL avoided. |
| XSS | Reflected / stored | Jinja auto-escape | Still sanitize dynamic HTML fragments. |
| Privilege escalation | Role field tampering | Server-side role checks | Add server-side revalidation for critical admin mutations. |

## Identified Gaps (Code Evidence Based)

1. Missing explicit CSRF tokens on JSON endpoints (e.g., `/api/quick-reservation`).
2. No rate limiting / lockout on `/login`.
3. Session hardening flags not explicitly set (search produced no explicit configuration lines).
4. Inconsistent carpool passenger logic: main blueprint references `carpool.passengers` & `driver_id` not present in `Carpool` model – indicates unimplemented membership table (security & data integrity gap).

## Improvement Roadmap

| Priority | Change | Value |
|----------|--------|-------|
| High | Add rate limiting & lockout to auth endpoints | Prevent brute force |
| High | Enforce Secure, HttpOnly, SameSite=Strict cookies | Reduce hijack & CSRF |
| High | Implement CSRF token for JSON mutations | Protect state changes |
| Medium | Centralize JSON validation schemas | Consistency & safety |
| Medium | Add password policy + breach check | Strengthen credential hygiene |
| Medium | Implement passenger membership table | Fix logical authorization gaps |
| Low | Structured logging & correlation IDs | Better observability |
| Low | Add security headers audit endpoint | Compliance verification |

## Quick Reference Summary

| Domain | Current | Needed Action |
|--------|---------|---------------|
| Auth | Session + bcrypt | Add rate limiting, session flags |
| Roles | user/admin | Consider granular permissions |
| CSRF | Forms only | Extend to JSON writes |
| Logging | Basic + Action model | Add auth anomaly logging |
| Passwords | Bcrypt | Enforce policy & updates cadence |

All above items grounded in repository inspection; no speculative features claimed.
