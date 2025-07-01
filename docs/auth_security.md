## Authentication & Security

### Authentication Methods

- **User login**: Username/email and password via login form.
- **Session management**: Flask-Login with secure session cookies.
- **Password storage**: Passwords hashed (see `password_hash` in User model).

### Authorization Model

- **Roles**: `administrator`, `user`, `guest` (role field in User model).
- **Access control**: Role checks in service layer and blueprints (e.g., `is_admin()`).
- **Admin routes**: Restricted to users with `administrator` role.

### Security Measures

- **CSRF protection**: Flask-WTF enabled (`WTF_CSRF_ENABLED = True`).
- **Input validation**: All forms use Flask-WTF validators.
- **Secure headers**: Flask-Talisman recommended for production.
- **Audit logging**: All admin actions logged in Action model.

### Session Management

- **Session cookies**: Secure, HTTP-only, with configurable timeout.
- **Session invalidation**: On logout or password change.

### Password Policy

- **Hashing**: Passwords stored as hashes.
- **Reset**: (Assumed) via email or admin action; not detailed in code.

### Security Configuration

- **Environment variables**: All secrets (SECRET_KEY, DB URI, etc.) loaded from `.env` via `python-dotenv`.
- **No hardcoded secrets**: All sensitive data is environment-driven.
- **Admin credentials**: Set via environment or config, not hardcoded.
