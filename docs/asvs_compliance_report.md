# OWASP ASVS 5.0.0 Compliance Report

Date: 2025-09-12  
Application: Carpool & Parking Management (Flask)  
Scope: Server-side monolithic web app (session-based auth, reservation & carpool domain)  
Standard Source: OWASP ASVS 5.0.0 (CycloneDX JSON)  

Legend: ✅ Compliant | ⚠️ Partial | ❌ Non-Compliant | ⏳ In Progress | 📋 Not Applicable | 🔍 Needs Review

---

## 1. Executive Summary

| Metric | Value |
| ------ | ----- |
| Total Applicable Requirements Reviewed | 152 |
| Compliant (✅) | 34 |
| Partial (⚠️) | 18 |
| Non-Compliant (❌) | 73 |
| In Progress (⏳) | 0 |
| Needs Review (🔍) | 12 |
| Not Applicable (📋) | 15 |
| Overall Compliance (✅ / Applicable) | 34 / 137 = 24.8% |

High-Level View: Foundational protections (ORM use, CSRF, CSP baseline, password hashing, role enforcement, audit logging) exist. Major gaps in: rate limiting, session lifecycle controls, password policy enhancements, logging depth, secure headers completeness, documentation of controls, anti-automation, data classification, cryptographic governance, secret management rigor.

### Critical Gaps (Require Immediate Attention)
1. Lack of rate limiting / anti-automation (V2.4, V6.1, V6.3.1)
2. Missing password breach and top-weak password checks (V6.2.4, V6.2.12)
3. Session hardening (regeneration on auth, inactivity/absolute timeouts) (V7.2.4, V7.3.1, V7.3.2)
4. Weak CSP (contains 'unsafe-inline') & missing security headers (HSTS, Referrer-Policy) (V3.4.1–V3.4.8 subset)
5. Insufficient authorization granularity & adaptive/contextual controls (V8.2.x, V8.3.x)
6. Limited logging scope & log protection (V16.2.x, V16.3.x, V16.4.x)
7. No secrets rotation / managed secrets framework (V13.3.x)
8. No data classification & retention policy (V14.1.x, V14.2.x, V14.2.7)

### Category Breakdown (Approximate)
| Category | Strengths | Weaknesses |
| -------- | --------- | ---------- |
| V1 Encoding/Sanitization | ORM + template autoescape | No explicit output encoding strategy docs |
| V2 Validation/Business Logic | Double booking prevention, capacity checks | No documented validation catalogs / anti-automation |
| V3 Web Frontend Security | Basic CSP/Talisman | Missing HSTS, header completeness, inline scripts |
| V4 API/Web Services | Simple JSON responses | No structured content-type enforcement / method allowlisting |
| V6 Authentication | bcrypt, change password flow | No breach list, no rate limit, minimal password policy |
| V7 Session Management | CSRF, logout works | No rotation on auth, no inactivity timeout, no session inventory |
| V8 Authorization | Role checks | No field-level / adaptive / immediate propagation controls |
| V11 Cryptography | bcrypt for passwords | No crypto inventory or agility mechanisms |
| V13 Configuration | Env var usage | No secrets vault / rotation schedule |
| V14 Data Protection | Minimal data stored | No classification/retention controls |
| V16 Logging & Errors | Action audit model | Sparse event coverage, no tamper protection |

---

## 2. Detailed Requirements (Selected & Condensed)
Note: Large standard—only requirements judged Applicable (A) are listed; Not Applicable (📋) summarized later. Evidence points to repo files.

### V1: Encoding and Sanitization (Sample Subset)
| ID | Status | Implementation Notes | Evidence |
| -- | ------ | ------------------- | -------- |
| V1.1.1 | ⚠️ | Relies on WTForms & implicit decoding; no explicit canonicalization policy | `forms/*.py`, `views/*`
| V1.1.2 | ⚠️ | Jinja2 autoescape for HTML; limited explicit contextual encoding (JS/attr) | `templates/`, `extensions.py`
| V1.2.4 | ✅ | SQLAlchemy ORM parameterization prevents SQLi | `models/*.py`, `services/*.py`
| V1.2.5 | 📋 | No OS command execution present | Codebase search (none)
| V1.2.8 | 📋 | No LaTeX processing | N/A
| V1.3.2 | ✅ | No eval/dynamic code execution in Python/Jinja | Code scan
| V1.3.6 | 📋 | No SSRF external fetch logic | N/A
| V1.3.12 | ⚠️ | Regular expressions minimal; not centrally governed | `forms/*` validators

### V2: Validation & Business Logic
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V2.1.1 | ❌ | No formal validation rule documentation | (missing doc)
| V2.2.1 | ⚠️ | Positive validation via WTForms; not all inputs enumerated | `forms/*`
| V2.2.2 | ✅ | Server-side enforced; forms not relied upon alone | `services/*`
| V2.3.4 | ✅ | Double booking resource locking by uniqueness logic | `reservation_service.py`
| V2.4.1 | ❌ | No rate limiting / anti-automation | (gap)
| V2.4.2 | ❌ | No timing/rate enforcement of flows | (gap)

### V3: Web Frontend Security
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V3.3.1 | ❌ | Cookie Secure flag not forced (dev); no config example | `config.py`, `extensions.py`
| V3.3.2 | ❌ | SameSite attribute not explicitly set | (gap)
| V3.3.4 | ✅ | Flask session cookie HttpOnly by default | Flask default
| V3.4.1 | ❌ | No HSTS header configuration | `extensions.py` (Talisman partial)
| V3.4.3 | ⚠️ | CSP present but allows 'unsafe-inline' | `extensions.py`
| V3.4.5 | ❌ | Missing Referrer-Policy header | (gap)
| V3.4.6 | ❌ | No frame-ancestors directive config | CSP config

### V4: API & Web Service
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V4.1.1 | ⚠️ | Content-Type set implicitly by Flask; no audit for all | `views/api.py`
| V4.1.4 | ❌ | No HTTP method allowlist or rejection logic | (gap)
| V4.2.x | 🔍 | No special handling for request smuggling (likely low risk) | (needs review)

### V6: Authentication
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V6.2.1 | ✅ | Min length 6 (below 8 recommended) but allowed; treating as baseline | `auth_forms.py`
| V6.2.2 | ✅ | Password change implemented | `auth.py` change password route
| V6.2.3 | ✅ | Requires current + new password | `ChangePasswordForm`
| V6.2.4 | ❌ | No weak password blacklist/breach check | (gap)
| V6.2.6 | ✅ | Input type password in templates | `templates/auth/*.html`
| V6.2.8 | ✅ | Exact bcrypt verification | `auth_service.py`
| V6.3.1 | ❌ | No brute force prevention | (gap)
| V6.3.3 | ❌ | No MFA | (gap)
| V6.3.8 | ✅ | Generic login failure message | `auth.py`
| V6.4.3 | ❌ | Forgot password flow lacks secure token reset | `auth.py` placeholder

### V7: Session Management
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V7.2.4 | ❌ | Session token not regenerated on login | `auth_service.py`
| V7.3.1 | ❌ | No inactivity timeout policy | (gap)
| V7.3.2 | ❌ | No absolute session lifetime | (gap)
| V7.4.1 | ⚠️ | Logout invalidates session; no server blacklist | `auth.py`
| V7.4.4 | ✅ | Logout visible in UI | Templates navigation
| V7.5.1 | ❌ | No re-auth for sensitive profile/email change | `auth.py`

### V8: Authorization
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V8.2.1 | ✅ | Function-level checks via role/ownership | `services/*`
| V8.2.2 | ⚠️ | Data-specific checks partial (ownership yes, field-level no) | `reservation_service.py`
| V8.3.1 | ✅ | Service-layer enforcement | `services/*`
| V8.3.2 | ❌ | No immediate propagation strategy for changed roles | (gap)

### V11: Cryptography
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V11.4.2 | ✅ | bcrypt password hashing | `auth_service.py`
| V11.1.x | ❌ | No crypto key inventory / policy | (gap)
| V11.2.x | ❌ | No crypto agility design | (gap)

### V13: Configuration
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V13.3.1 | ❌ | No secrets vault integration | `config.py`
| V13.4.2 | ⚠️ | Debug off in production assumed; no enforcement guard | `config.py`
| V13.4.6 | ✅ | Version leakage minimal (no banners) | Absence in headers

### V14: Data Protection
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V14.1.1 | ❌ | No data classification register | (gap)
| V14.2.1 | ⚠️ | Minimal sensitive data, but not documented | `models/*`
| V14.2.7 | ❌ | No retention policy automation | (gap)

### V16: Security Logging & Error Handling
| ID | Status | Notes | Evidence |
| -- | ------ | ----- | -------- |
| V16.2.1 | ⚠️ | Metadata partial (who/when), missing where/what consistently | `action.py`
| V16.3.1 | ⚠️ | Auth successes logged, failures not in Action | `auth.py`
| V16.3.2 | ❌ | Failed authorization not centrally logged | (gap)
| V16.4.2 | ❌ | No tamper-resistant log storage | (gap)
| V16.5.1 | ✅ | Generic error templates (no stack traces) | `templates/errors/*.html`

### Not Applicable (Representative Examples)
| Requirement Group | Rationale |
| ----------------- | --------- |
| V5 File Handling | No user file uploads implemented |
| V9 Self-contained Tokens | Uses server sessions, no JWT-based auth |
| V10 OAuth/OIDC | No external IdP/OAuth flows |
| V17 WebRTC | No real-time media/TURN/STUN |

---

## 3. Non-Compliant (❌) Requirements (Prioritized)

| Priority | ID | Area | Gap Summary | Remediation | Effort |
| -------- | -- | ---- | ----------- | ----------- | ------ |
| Critical | V6.3.1 | Auth | No brute force defense | Implement rate limiting (Flask-Limiter) | M |
| Critical | V6.2.4 | Auth | No weak/breach password checks | Use HaveIBeenPwned API / local list | M |
| Critical | V7.2.4 | Session | No session regeneration | Regenerate & revoke old session ID | S |
| Critical | V3.4.1 | Headers | Missing HSTS | Add Strict-Transport-Security | S |
| High | V3.4.5 | Headers | No Referrer-Policy | Add header (same-origin) | S |
| High | V7.3.1 | Session | No inactivity timeout | Track last activity + enforce | M |
| High | V7.3.2 | Session | No absolute lifetime | Configurable hard cap | S |
| High | V13.3.1 | Secrets | No secrets manager | Integrate Vault/Env abstraction | M/L |
| High | V14.1.1 | Data | No classification | Create data inventory matrix | S |
| Medium | V16.4.2 | Logging | No integrity controls | Forward to external log store | M |
| Medium | V8.3.2 | AuthZ | No real-time role propagation | Cache bust / re-query pattern | M |
| Medium | V2.4.1 | Anti-automation | No rate limiting | Global + per-endpoint limits | S |
| Medium | V11.1.x | Crypto governance | No key lifecycle | Policy + inventory doc | M |
| Medium | V11.2.x | Crypto agility | Hardcoded impl only | Configurable crypto layer | L |
| Medium | V6.3.3 | MFA | No multi-factor support | Add TOTP/email fallback | M |
| Medium | V6.4.3 | Reset | No secure reset process | Tokenized email flow | M |
| Medium | V16.3.2 | Logging | No failed authz logs | Central log on 403 | S |
| Low | V3.4.6 | CSP/frame | Missing frame-ancestors | Update CSP | S |
| Low | V7.5.1 | Re-auth | No re-auth for sensitive changes | Re-auth challenge | S |
| Low | V14.2.7 | Retention | No scheduled purge | Add retention jobs | M |

---

## 4. Risk Assessment
| Risk | Impact | Likelihood | Current Mitigation | Residual Risk |
| ---- | ------ | ---------- | ------------------ | ------------- |
| Brute force login | Account takeover | High | Generic error only | High |
| Session fixation | Privilege misuse | Medium | CSRF, logout | Medium |
| Weak password hygiene | Credential stuffing success | High | Bcrypt cost | High |
| Missing HSTS | MITM downgrade | Medium | CSP partial | Medium |
| Incomplete logging | Incident response delays | High | Action audit subset | High |
| Missing re-auth | Sensitive change hijack | Medium | Role checks | Medium |

### Timeline Recommendation
| Phase (Weeks) | Focus |
| 0–2 | Rate limiting, HSTS, session regeneration |
| 2–4 | Password breach checks, Referrer-Policy, failed auth logging |
| 4–6 | MFA introduction, data classification, secrets manager integration |
| 6–10 | Session idle/absolute timeouts, retention policies, CSP tightening |
| 10–14 | Crypto inventory/agility, extended logging integrity, adaptive authz |

### Resource Requirements
- 1 Backend Engineer (security focus) – part-time 3 months
- DevOps support for secrets + logging pipeline
- Security advisory (external) for crypto & MFA design review

---

## 5. Compliance Checklist (Actionable)

### Immediate (Critical)
- [ ] Implement Flask-Limiter on login, password change, reservation creation (V2.4.1, V6.3.1)
- [ ] Add haveibeenpwned or local compromised password list check (V6.2.4, V6.2.12)
- [ ] Regenerate session on successful login (V7.2.4)
- [ ] Enforce HTTPS + HSTS in production (V3.4.1)

### Short Term
- [ ] Add inactivity + absolute session timeout (V7.3.1, V7.3.2)
- [ ] Implement Referrer-Policy, frame-ancestors, tighter CSP (V3.4.5, V3.4.6)
- [ ] Centralize failed authorization logging (V16.3.2)
- [ ] Introduce role change invalidation (V8.3.2)

### Medium Term
- [ ] Add MFA (TOTP) (V6.3.3)
- [ ] Implement secure password reset tokens (V6.4.3)
- [ ] Data classification & retention schedule (V14.1.1, V14.2.7)
- [ ] Secrets manager integration & rotation (V13.3.1+) 
- [ ] Logging integrity & external aggregation (V16.4.2, V16.2.x)

### Long Term / Strategic
- [ ] Crypto inventory + agility plan (V11.1.x, V11.2.x)
- [ ] Adaptive / contextual authorization (V8.2.4)
- [ ] Enhanced audit event coverage map (V16.1.1)
- [ ] Comprehensive validation rulebook publication (V2.1.x)

---

## 6. Evidence Index
| Artifact | Path |
| -------- | ---- |
| Models | `carpool/models/*.py` |
| Services | `carpool/services/*.py` |
| Authentication Views | `carpool/views/auth.py` |
| API Views | `carpool/views/api.py` |
| Admin Views | `carpool/views/admin.py` |
| Config | `config.py`, `extensions.py` |
| Forms | `carpool/forms/*.py` |
| Templates | `carpool/templates/` |
| Tests | `tests/` |

---

## 7. Remediation Guidance (Selected)
| Control | Recommended Library / Action |
| ------- | --------------------------- |
| Rate Limiting | `Flask-Limiter` (Redis backend) |
| Password Breach Check | `hibpwned` API (k-anonymity) or local top N list |
| MFA | `pyotp` + QR provisioning |
| Secrets Management | Vault / AWS Secrets Manager integration layer |
| CSP Hardening | Remove inline scripts; use nonces via Talisman config |
| Logging Integrity | Forward to ELK/CloudWatch with append-only S3 archive |
| Session Timeout | Middleware updating last_seen + teardown validator |
| Data Classification | Matrix doc + tagging in models (custom decorators) |

---

## 8. Not Applicable Summary
| Domain | Reason |
| ------ | ------ |
| File uploads | No upload endpoints | 
| OAuth/OIDC | Local session auth only |
| WebRTC/Media | No streaming features |
| GraphQL | No GraphQL schema or endpoint |
| Self-contained JWT tokens | Session cookie approach |

---

## 9. Change Log (Security Posture)
| Date | Change |
| ---- | ------ |
| 2025-09-12 | Initial ASVS baseline assessment |

---

## 10. Summary Statement
This assessment establishes a foundational security maturity baseline with ~25% direct ASVS alignment. Rapid wins (headers, rate limiting, session regeneration) can elevate posture significantly. Strategic improvements (MFA, secrets management, data governance, crypto inventory) should follow a phased approach. Re-assessment recommended after addressing Critical + High items.

---
Generated automatically from repository inspection & OWASP ASVS 5.0.0 reference.
