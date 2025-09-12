# Carpool & Parking Management – Documentation Hub

## About
A Flask-based monolithic application enabling users to reserve parking spots, organize carpools, and for administrators to manage users, infrastructure, and operational insights—backed by a service layer, role-based access control, and audit logging.

## Quick Start
```bash
# (Assumed environment)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask db upgrade
flask run
```

## Documentation Links
- [Architecture](./architecture.md)
- [Business Logic](./business_logic.md)
- [Domain Model](./domain_model.md)
- [Database Structure](./database_structure.md)
- [API Spec (OpenAPI)](./api_spec.yaml)
- [Authentication & Security](./auth_security.md)
- [User Flow Diagrams](./user_flow_diagrams.md)

## Diagram Index (Mermaid)
- Architecture: flowchart (system-overview)
- User flow: flowchart TD (user-journeys)
- Domain model: erDiagram (entities-relationships)
- Database structure: erDiagram (database-schema)
- Reservation lifecycle: stateDiagram-v2 (business_logic)
- Additional flowcharts: registration, login, reservation create/edit, admin operations

## Key Features
- Parking spot reservation with conflict prevention
- Carpool trip creation & capacity tracking
- Role-based admin console (users, parking, logs, analytics)
- Real-time dashboard statistics + charts (AJAX / JSON endpoints)
- Audit logging (actions table)
- Hardened CSP & CSRF protection
- Service layer enforcing business rules
- Modular Blueprints: auth, main, admin, api

## Configuration
| Variable | Purpose | Default |
| -------- | ------- | ------- |
| SECRET_KEY | Session signing | dev-secret-key-change-in-production |
| DATABASE_URL | SQLAlchemy URI | sqlite:///carpool.db |
| SECURITY_PASSWORD_SALT | Future token ops | salt-change-in-production |
| ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL | Bootstrap admin credentials | admin / admin123 / admin@carpool.com |

## API Overview
See `api_spec.yaml` for formal OpenAPI definition (session cookie auth). Provides endpoints for stats aggregation, spot availability, carpool membership, quick reservation, activity feeds, and admin monitoring.

## Security Highlights
- bcrypt password hashing
- CSRF enforcement
- CSP via Flask-Talisman
- Role-based route gating
- Audit logs for critical mutations

## Known Gaps / Future Enhancements
- Implement real passenger membership model for carpools
- Password reset token & email workflow
- Rate limiting on login attempts
- Improve Action schema (IP, user agent fields)
- Index optimization (composite spot/date)
- Eliminate `'unsafe-inline'` CSP exceptions

## Change Log
| Version | Date | Reference | Description |
| ------- | ---- | --------- | ----------- |
| 0.1.0 | 2025-06-26 | migration bf20dc5ca70c | Added reservation status column |
| 0.2.0 | 2025-07-xx | internal | Service layer consolidation & audit logging helpers |
| 0.3.0 | 2025-08-xx | internal | Dashboard chart endpoints expansion |
| 1.0.0 | 2025-09-xx | release | Documentation baseline & OpenAPI publication |

(Adjust dates/entries as releases formalize.)

## Maintenance Guidelines
- Add migrations for any model changes (Alembic).
- Keep service layer side-effect boundaries explicit.
- Expand test suite beyond authentication & user model to cover reservations, carpools, admin flows.
- Monitor audit log growth (consider archival strategy).

## Contact / Ownership
(Define engineering owner / team alias here.)

---
Generated from source inspection; discrepancies (e.g., carpool passenger handling) flagged in related docs.
