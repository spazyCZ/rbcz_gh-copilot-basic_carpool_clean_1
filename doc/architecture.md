# Architecture

## Overview
The system is a monolithic Flask web application providing:
* Parking spot reservation management
* Carpool trip organization
* Administrative dashboards & system monitoring
* User authentication & role-based access control
* REST-style JSON endpoints for dashboard widgets & AJAX interactions

Primary layers observed:
1. Presentation Layer: Flask blueprints (`main`, `auth`, `admin`, `api`) + Jinja2 templates under `carpool/templates/` and static assets.
2. Service Layer: Business logic in `carpool/services/*_service.py` (reservation, carpool, auth, admin).
3. Data Layer: SQLAlchemy models in `carpool/models/*` with Alembic migrations.
4. Infrastructure: App factory (`carpool/__init__.py`), configuration (`config.py`), extension wiring (`extensions.py`), CLI bootstrap (`run.py`).

## Technology Stack
* Python / Flask
* Flask-Login (session authentication)
* SQLAlchemy ORM + Alembic migrations
* Flask-Migrate integration
* Bcrypt for password hashing (via `bcrypt` library)
* CSRF protection (`flask_wtf.csrf`)
* Security headers (`flask_talisman` – activated when not in debug)
* Moment.js integration (`flask_moment`)
* SQLite database by default (configurable through `DATABASE_URL`)

## Module & Responsibility Map
| Module | Responsibility |
|--------|----------------|
| `carpool/__init__.py` | App factory, blueprint registration, default admin bootstrap |
| `config.py` | Environment-based configuration classes |
| `extensions.py` | Instantiate & initialize Flask extensions |
| `run.py` | Entry script, CLI commands, database seed helpers |
| `carpool/models/*` | Persistence models: `User`, `ParkingSpot`, `Reservation`, `Carpool`, `Action` (audit) |
| `carpool/services/auth_service.py` | Authentication, hashing, session login/logout, user CRUD helpers |
| `carpool/services/reservation_service.py` | Reservation lifecycle logic, validation, stats |
| `carpool/services/carpool_service.py` | Carpool lifecycle, passenger capacity & state checks |
| `carpool/services/admin_service.py` | Administrative operations, user & parking management, system analytics |
| `carpool/views/main.py` | User dashboards, reservations & carpool HTML views |
| `carpool/views/auth.py` | Login, registration, password & account views |
| `carpool/views/admin.py` | Administrative HTML interfaces |
| `carpool/views/api.py` | JSON endpoints for stats, charts, AJAX actions |
| `migrations/` | Alembic migration scripts |
| `tests/` | Unit & integration tests (models & auth views) |

## Request Flow
1. Client sends HTTP request (browser or AJAX) to route.
2. Flask blueprint route handler executes.
3. Handler delegates business rules to a corresponding Service class.
4. Service performs validation/business logic, interacts with SQLAlchemy models via `db.session`.
5. Service may log an action through the `Action` model helpers.
6. Response is rendered template (HTML) or JSON (API blueprint).

## Cross-Cutting Concerns
| Concern | Implementation |
|---------|----------------|
| Authentication | Flask-Login + `User` model integration |
| Authorization | Role checks via `User.is_admin()`, custom decorator `admin_required` |
| Auditing | `Action` model + static log_* methods invoked in services/views |
| Input Validation | WTForms (forms in `carpool/forms/*`) (forms themselves not fully listed here) |
| Security Headers | Talisman (only when `app.debug` is False) |
| CSRF | WTForms CSRF + `CSRFProtect` |
| Password Hashing | Bcrypt (direct usage in `AuthService`) |
| Migrations | Alembic via Flask-Migrate |

## Logical Architecture Diagram
```mermaid
flowchart TD
	Browser[Browser / Client] -->|HTTP / HTML| MainViews
	Browser -->|HTTP / HTML| AuthViews
	Browser -->|HTTP / HTML| AdminViews
	Browser -->|XHR / JSON| APIViews

	subgraph Presentation[Presentation Layer]
		MainViews[Blueprint: main]
		AuthViews[Blueprint: auth]
		AdminViews[Blueprint: admin]
		APIViews[Blueprint: api]
	end

	subgraph Services[Service Layer]
		AuthSvc[AuthService]
		ResSvc[ReservationService]
		CarSvc[CarpoolService]
		AdmSvc[AdminService]
	end

	subgraph Data[Data Layer]
		UserModel[(User)]
		ParkingModel[(ParkingSpot)]
		ReservationModel[(Reservation)]
		CarpoolModel[(Carpool)]
		ActionModel[(Action Log)]
	end

	APIViews --> ResSvc
	APIViews --> CarSvc
	APIViews --> AdmSvc
	MainViews --> ResSvc
	MainViews --> CarSvc
	AdminViews --> AdmSvc
	AuthViews --> AuthSvc

	AuthSvc --> UserModel
	ResSvc --> ReservationModel & ParkingModel & UserModel & ActionModel
	CarSvc --> CarpoolModel & UserModel & ActionModel
	AdmSvc --> UserModel & ParkingModel & ReservationModel & CarpoolModel & ActionModel

	subgraph Infra[Infrastructure]
		AppFactory[create_app()]
		Extensions[extensions.py]
		Config[config.py]
	end

	AppFactory --> Extensions --> Data
	AppFactory --> Config
	AppFactory --> Presentation
```

## Deployment & Runtime
* Launched via `run.py` (development) using `app.run()`.
* CLI commands (Flask app context) support migrations & data setup.
* Default SQLite DB file `carpool.db` (unless `DATABASE_URL` overrides).

## Notable Design Choices
* Clear separation of concerns: routes thin; heavy logic in services.
* Audit logging centralized through `Action` static methods.
* Role-based checks performed close to entry points (views) plus some duplication inside services for defense-in-depth.
* Statistics aggregation executed on-demand (no caching observed).

## Potential Improvement Areas (Observed Gaps Only)
* Missing explicit passenger association model for carpools (code references `passengers` in `main.py` but `Carpool` model lacks relationship) — likely a future enhancement or legacy residue.
* Some duplication of logging & validation between views and services (could consolidate).
* Lack of rate limiting or brute-force protection on auth endpoints.
* No pagination on large list endpoints (admin logs, reservations, carpools capped by limit but manual slicing).
* Single migration present — additional migrations may be needed as schema evolves.

## Evidence Sources
* `carpool/__init__.py` for factory & blueprint wiring
* `carpool/views/*.py` for routing & layer boundaries
* `carpool/services/*.py` for business orchestration
* `carpool/models/*.py` for persistence schema
* `config.py`, `extensions.py`, `run.py` for environment/runtime patterns

Sections with assumptions are explicitly noted; no undocumented external services observed.
