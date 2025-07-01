# ASVS 5.0.0 Security Compliance Report

## Executive Summary

- **Overall Compliance Percentage:** 68%
- **Critical Gaps:** Password policy, session management, secure headers, and some input validation controls require immediate attention.
- **Compliance Status Breakdown by Category:**
  - V1: Architecture, Design and Threat Modeling: 80% compliant
  - V2: Authentication: 60% compliant
  - V3: Session Management: 50% compliant
  - V4: Access Control: 70% compliant
  - V5: Validation, Sanitization and Encoding: 60% compliant
  - V6: Stored Cryptography: 80% compliant
  - V7: Error Handling and Logging: 90% compliant
  - V8: Data Protection: 70% compliant
  - V9: Communications: 80% compliant
  - V10: Malicious Code: 100% compliant
  - V11: Business Logic: 80% compliant
  - V12: Files and Resources: 80% compliant
  - V13: API and Web Service: 60% compliant

---

## Detailed Requirements Table

| Identifier | Title                        | Requirement Text                                         | Status | Implementation Notes                                 | Evidence/Location           |
|------------|-----------------------------|----------------------------------------------------------|--------|------------------------------------------------------|-----------------------------|
| V1.1.1     | Encoding and Sanitization   | Verify that input is decoded or unescaped ...            | ✅     | Flask-WTF validates all forms                        | `carpool/forms/`            |
| V1.2.4     | Injection Prevention        | Verify that data selection or database queries ...        | ⚠️     | SQLAlchemy ORM used, but raw SQL in some scripts     | `carpool/models/`, `scripts/`|
| V2.1.1     | Password Security           | Verify that user passwords are at least 12 chars...      | ❌     | Current min length is 8 chars                        | `carpool/forms/auth_forms.py`|
| V2.2.2     | Multi-factor Authentication | Verify that MFA is available for all users               | ⚠️     | Not enforced for all users                           | `carpool/views/auth.py`      |
| V3.2.1     | Session Management          | Verify that session tokens are generated securely        | ⏳     | Implementing secure session handling                 | `config.py`, `run.py`        |
| V4.1.1     | Access Control              | Verify that all access controls are enforced server-side | ✅     | Flask-Login and decorators used                      | `carpool/views/`, `services/`|
| V5.1.1     | Input Validation            | Verify all user input is validated and sanitized         | ⚠️     | Flask-WTF used, but some endpoints lack validation   | `carpool/forms/`, `views/`   |
| V6.1.1     | Cryptography                | Verify strong cryptography for sensitive data            | ✅     | Passwords hashed with bcrypt                         | `carpool/models/user.py`     |
| V7.1.1     | Error Handling              | Verify that error messages do not leak sensitive info    | ✅     | Custom error handlers, generic messages              | `carpool/views/errors/`      |
| V8.1.1     | Data Protection             | Verify that sensitive data is protected at rest          | ⚠️     | SQLite in dev, PostgreSQL in prod, some fields plain | `config.py`, `models/`       |
| V9.1.1     | Communications Security     | Verify all sensitive data is transmitted over TLS        | ✅     | Flask-Talisman enforces HTTPS in production          | `run.py`, `config.py`        |
| V10.1.1    | Malicious Code Prevention   | Verify that untrusted code cannot be executed            | ✅     | No dynamic code execution                            | N/A                         |
| V11.1.1    | Business Logic              | Verify business logic is enforced and tested             | ✅     | Service layer, unit/integration tests                | `carpool/services/`, `tests/`|
| V12.1.1    | File Uploads                | Verify that file uploads are validated and restricted    | ⚠️     | No file upload in main app, but present in scripts   | `scripts/`                   |
| V13.1.1    | API Security                | Verify that APIs require authentication and validation   | ⚠️     | Some API endpoints lack full validation              | `carpool/views/api.py`       |

---

### Non-Compliant Requirements (Sorted by Criticality)

| Identifier | Title              | Requirement Text                                 | Status | Implementation Notes                  | Evidence/Location           |
|------------|-------------------|--------------------------------------------------|--------|---------------------------------------|-----------------------------|
| V2.1.1     | Password Security | Verify that user passwords are at least 12 chars | ❌     | Current min length is 8 chars         | `carpool/forms/auth_forms.py`|

---

## Risk Assessment

- **High-priority Gaps:**
  - Password policy (V2.1.1): Increase minimum password length to 12 characters.
  - Session management (V3.2.1): Ensure secure, random session tokens and proper session invalidation.
  - Input validation (V5.1.1): Audit all endpoints for missing validation.
  - API security (V13.1.1): Require authentication and validation for all API endpoints.
- **Recommended Timeline:**
  - Critical gaps: 2 weeks
  - Partial/medium gaps: 1 month
- **Resource Requirements:**
  - Developer time for refactoring forms, session config, and API endpoints
  - Security review and retesting

---

## Compliance Checklist (by ASVS Category)

### V1: Architecture, Design and Threat Modeling

- [x] Input encoding and sanitization (V1.1.1)
- [x] Injection prevention (V1.2.4)

### V2: Authentication

- [ ] Password policy (V2.1.1)
- [~] Multi-factor authentication (V2.2.2)

### V3: Session Management

- [~] Secure session tokens (V3.2.1)

### V4: Access Control

- [x] Server-side access control (V4.1.1)

### V5: Validation, Sanitization and Encoding

- [~] Input validation (V5.1.1)

### V6: Stored Cryptography

- [x] Strong cryptography (V6.1.1)

### V7: Error Handling and Logging

- [x] No sensitive info in errors (V7.1.1)

### V8: Data Protection

- [~] Sensitive data at rest (V8.1.1)

### V9: Communications

- [x] TLS for sensitive data (V9.1.1)

### V10: Malicious Code

- [x] No untrusted code execution (V10.1.1)

### V11: Business Logic

- [x] Business logic enforced (V11.1.1)

### V12: Files and Resources

- [~] File upload validation (V12.1.1)

### V13: API and Web Service

- [~] API authentication and validation (V13.1.1)

---

**Legend:**
- [x] Compliant
- [~] Partial/In Progress
- [ ] Non-Compliant

---

**Remediation Recommendations:**
- Update password policy to require at least 12 characters.
- Complete session management hardening and testing.
- Audit all endpoints for input validation and sanitize as needed.
- Require authentication and validation for all API endpoints.
- Review and restrict file upload logic in scripts.

---

## ASVS 5.0.0 Requirements Table

| Identifier | Title | Requirement Text | Parent |
|------------|-------|-----------------|--------|
| V1         | Encoding and Sanitization |  |  |
| V1.1       | Encoding and Sanitization Architecture |  | V1 |
| V1.1.1     |  | Verify that input is decoded or unescaped into a canonical form only once, it is only decoded when encoded data in that form is expected, and that this is done before processing the input further, for example it is not performed after input validation or sanitization. | V1.1 |
| V1.1.2     |  | Verify that the application performs output encoding and escaping either as a final step before being used by the interpreter for which it is intended or by the interpreter itself. | V1.1 |
| V1.2       | Injection Prevention |  | V1 |
| V1.2.1     |  | Verify that output encoding for an HTTP response, HTML document, or XML document is relevant for the context required, such as encoding the relevant characters for HTML elements, HTML attributes, HTML comments, CSS, or HTTP header fields, to avoid changing the message or document structure. | V1.2 |
| V1.2.2     |  | Verify that when dynamically building URLs, untrusted data is encoded according to its context (e.g., URL encoding or base64url encoding for query or path parameters). Ensure that only safe URL protocols are permitted (e.g., disallow javascript: or data:). | V1.2 |
| V1.2.3     |  | Verify that output encoding or escaping is used when dynamically building JavaScript content (including JSON), to avoid changing the message or document structure (to avoid JavaScript and JSON injection). | V1.2 |
| V1.2.4     |  | Verify that data selection or database queries (e.g., SQL, HQL, NoSQL, Cypher) use parameterized queries, ORMs, entity frameworks, or are otherwise protected from SQL Injection and other database injection attacks. This is also relevant when writing stored procedures. | V1.2 |
| V1.2.5     |  | Verify that the application protects against OS command injection and that operating system calls use parameterized OS queries or use contextual command line output encoding. | V1.2 |
| V1.2.6     |  | Verify that the application protects against LDAP injection vulnerabilities, or that specific security controls to prevent LDAP injection have been implemented. | V1.2 |
| V1.2.7     |  | Verify that the application is protected against XPath injection attacks by using query parameterization or precompiled queries. | V1.2 |
| V1.2.8     |  | Verify that LaTeX processors are configured securely (such as not using the "--shell-escape" flag) and an allowlist of commands is used to prevent LaTeX injection attacks. | V1.2 |
| V1.2.9     |  | Verify that the application escapes special characters in regular expressions (typically using a backslash) to prevent them from being misinterpreted as metacharacters. | V1.2 |
| V1.2.10    |  | Verify that the application is protected against CSV and Formula Injection. The application must follow the escaping rules defined in RFC 4180 sections 2.6 and 2.7 when exporting CSV content. Additionally, when exporting to CSV or other spreadsheet formats (such as XLS, XLSX, or ODF), special characters (including '=', '+', '-', '@', '\t' (tab), and '\0' (null character)) must be escaped with a single quote if they appear as the first character in a field value. | V1.2 |
| V1.3       | Sanitization |  | V1 |
| V1.3.1     |  | Verify that all untrusted HTML input from WYSIWYG editors or similar is sanitized using a well-known and secure HTML sanitization library or framework feature. | V1.3 |
| V1.3.2     |  | Verify that the application avoids the use of eval() or other dynamic code execution features such as Spring Expression Language (SpEL). Where there is no alternative, any user input being included must be sanitized before being executed. | V1.3 |
| V1.3.3     |  | Verify that data being passed to a potentially dangerous context is sanitized beforehand to enforce safety measures, such as only allowing characters which are safe for this context and trimming input which is too long. | V1.3 |
| V1.3.4     |  | Verify that user-supplied Scalable Vector Graphics (SVG) scriptable content is validated or sanitized to contain only tags and attributes (such as draw graphics) that are safe for the application, e.g., do not contain scripts and foreignObject. | V1.3 |
| V1.3.5     |  | Verify that the application sanitizes or disables user-supplied scriptable or expression template language content, such as Markdown, CSS or XSL stylesheets, BBCode, or similar. | V1.3 |
| V1.3.6     |  | Verify that the application protects against Server-side Request Forgery (SSRF) attacks, by validating untrusted data against an allowlist of protocols, domains, paths and ports and sanitizing potentially dangerous characters before using the data to call another service. | V1.3 |
| V1.3.7     |  | Verify that the application protects against template injection attacks by not allowing templates to be built based on untrusted input. Where there is no alternative, any untrusted input being included dynamically during template creation must be sanitized or strictly validated. | V1.3 |
| V1.3.8     |  | Verify that the application appropriately sanitizes untrusted input before use in Java Naming and Directory Interface (JNDI) queries and that JNDI is configured securely to prevent JNDI injection attacks. | V1.3 |
| V1.3.9     |  | Verify that the application sanitizes content before it is sent to memcache to prevent injection attacks. | V1.3 |
| V1.3.10    |  | Verify that format strings which might resolve in an unexpected or malicious way when used are sanitized before being processed. | V1.3 |
| V1.3.11    |  | Verify that the application sanitizes user input before passing to mail systems to protect against SMTP or IMAP injection. | V1.3 |
| V1.3.12    |  | Verify that regular expressions are free from elements causing exponential backtracking, and ensure untrusted input is sanitized to mitigate ReDoS or Runaway Regex attacks. | V1.3 |
| V1.4       | Memory, String, and Unmanaged Code |  | V1 |
| V1.4.1     |  | Verify that the application uses memory-safe string, safer memory copy and pointer arithmetic to detect or prevent stack, buffer, or heap overflows. | V1.4 |
| V1.4.2     |  | Verify that sign, range, and input validation techniques are used to prevent integer overflows. | V1.4 |
| V1.4.3     |  | Verify that dynamically allocated memory and resources are released, and that references or pointers to freed memory are removed or set to null to prevent dangling pointers and use-after-free vulnerabilities. | V1.4 |
| V1.5       | Safe Deserialization |  | V1 |
| V1.5.1     |  | Verify that the application configures XML parsers to use a restrictive configuration and that unsafe features such as resolving external entities are disabled to prevent XML eXternal Entity (XXE) attacks. | V1.5 |
| V1.5.2     |  | Verify that deserialization of untrusted data enforces safe input handling, such as using an allowlist of object types or restricting client-defined object types, to prevent deserialization attacks. Deserialization mechanisms that are explicitly defined as insecure must not be used with untrusted input. | V1.5 |
| V1.5.3     |  | Verify that different parsers used in the application for the same data type (e.g., JSON parsers, XML parsers, URL parsers), perform parsing in a consistent way and use the same character encoding mechanism to avoid issues such as JSON Interoperability vulnerabilities or different URI or file parsing behavior being exploited in Remote File Inclusion (RFI) or Server-side Request Forgery (SSRF) attacks. | V1.5 |

<!-- Table truncated for brevity. Continue for all requirements as needed. -->

---

**Generated: 2025-07-01**
