# System Documentation Hub

## About

This is a carpool and parking spot management system for organizations. It enables users to organize carpools, reserve parking spots, and manage their trips efficiently. The application provides user authentication, role-based access control, an admin dashboard, and RESTful APIs for integrations. It is designed for secure, auditable, and user-friendly operation in both small and large organizations.

## Quick Start

1. Clone the repository and install dependencies (`pip install -r requirements.txt`).
2. Set up a `.env` file with required environment variables (see `config.py`).
3. Run database migrations (`flask db upgrade`).
4. Start the application (`flask run` or `python run.py`).
5. Access the app at `http://localhost:5000`.

## Documentation Links

- [Architecture Overview](architecture.md)
- [Business Logic & Functional Requirements](business_logic.md)
- [Domain Data Model](domain_model.md)
- [API Specification (OpenAPI)](api_spec.yaml)
- [Authentication & Security](auth_security.md)

## Diagram Index (Mermaid)

- Architecture: flowchart (system-overview)
- Reservation lifecycle: stateDiagram-v2 (reservation-states)
- Domain model: erDiagram (entities-relationships)

## Key Features

- User authentication and role-based access control
- Carpool trip organization and management
- Parking spot reservation system
- Admin dashboard for user, carpool, and reservation management
- Audit logging of all admin actions
- Responsive UI with Chart.js data visualizations
- RESTful API endpoints for AJAX and integrations

## Configuration

- All secrets and environment variables must be set in `.env`
  - `SECRET_KEY`, `DATABASE_URL`, `SECURITY_PASSWORD_SALT`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`
- See `config.py` for all configurable options.

## Change Log

- v1.0.0: Initial release with user authentication, carpool management, parking spot reservation, admin dashboard, and audit logging.
- v1.1.0: Added RESTful API endpoints for AJAX and integrations.
- v1.2.0: Improved security with Flask-Talisman and environment-based secrets.
- v1.3.0: Enhanced UI with Chart.js visualizations and responsive design.
- v1.4.0: Refactored business logic into service layer and improved test coverage.

<!-- Reference implemented stories/changes in project management system as needed. -->
