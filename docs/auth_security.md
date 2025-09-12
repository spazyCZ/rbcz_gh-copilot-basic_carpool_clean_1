## Authentication & Security

### Authentication Methods
- Session-based authentication via Flask-Login.
- Users authenticate with username OR email + password at `/auth/login`.
- Passwords hashed using bcrypt (`gensalt` + `hashpw`).
- "Remember Me" optional persistent session.

### Authorization Model
| Role | Capabilities |
| ---- | ------------ |
| administrator | All operations (user mgmt, parking mgmt, statistics, delete) |
| user | Create/update/cancel own reservations, create/manage own carpools, view dashboards |
| guest | (Future extension; currently limited if assigned) |
| anonymous | Public index, login, registration, forgot-password |

- Route protection via `@login_required` + custom `admin_required` decorator.
- Ownership checks enforced in service layer for modifying reservations/carpools.

### Security Measures
- CSRF Protection: Enabled globally (disabled in testing).
- Content Security Policy (Talisman) with restrictive `default-src 'self'` and selective CDNs.
- Session Cookie: HTTPOnly (default Flask), recommend secure + SameSite=strict in production.
- Password Hashing: bcrypt (strong computational cost).
- Input Validation: WTForms field validators + custom uniqueness checks.
- Error Handling: Uniform login failure messages mitigate enumeration.

### Session Management
- Session cookie identifies logged-in user.
- Logout route manually clears session and logs action.
- No idle timeout or explicit rotation currently implemented.
- Recommended enhancement: session invalidation on password change.

### Password Policy
- Minimum length: 6 characters (forms).
- No complexity enforcement (recommend enhancement).
- Forgot password route placeholder (no token/email reset implemented).
- Password change logs administrative `Action`.

### Security Configuration & Environment
- `SECRET_KEY` for signing sessions (must override default in production).
- `SECURITY_PASSWORD_SALT` present but unused (future token workflows).
- `WTF_CSRF_ENABLED` toggled off in tests for simplicity.
- HTTPS Enforcement: `force_https=False` currently (must enable in production).
- CSP reduces XSS surface; inline allowances limited to necessary libs.

### Sensitive Data Handling
- Passwords only stored as bcrypt hash.
- Emails in plaintext (acceptable; consider encryption if regulatory need).
- No tokens / API keys at rest.

### Logging & Audit
- Action model captures critical events.
- Gaps: Failure events (e.g., invalid login attempts) only logged at warning-level, not persisted as Action—limits forensic analysis.

### Threat Considerations & Mitigations
| Threat | Mitigation | Gap |
| ------ | ---------- | --- |
| CSRF | Flask-WTF tokens | API endpoints relying on JS POSTs must ensure token inclusion |
| Brute Force Login | None explicit | Add rate limiting / exponential backoff |
| Session Fixation | Fresh login creates new session | Force session regeneration recommended |
| XSS | CSP + templating autoescape | Inline script allowances narrow but present (`'unsafe-inline'`) |
| SQL Injection | SQLAlchemy ORM usage | Raw SQL only in health check (safe) |
| Privilege Escalation | Role checks in services + decorators | Centralized policy docs needed |
| Race Double Booking | Application-level check | Add unique composite index `(spot_id, reservation_date)` |

### Recommended Enhancements
- Implement password reset token flow.
- Add multi-factor optional support.
- Introduce structured rate limits (e.g., Flask-Limiter).
- Store per-action metadata (IP, user agent) with schema migration.
- Harden CSP by eliminating `'unsafe-inline'` (migrate inline scripts to static files).
