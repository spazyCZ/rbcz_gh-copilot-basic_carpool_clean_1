# Database Structure

All content derived from SQLAlchemy models & Alembic migration present in repo. Default DB is SQLite (configurable via `DATABASE_URL`).

## Engine & Configuration

| Setting | Source | Default |
|---------|--------|---------|
| SQLALCHEMY_DATABASE_URI | `Config.SQLALCHEMY_DATABASE_URI` | `sqlite:///carpool.db` |
| TRACK_MODIFICATIONS | `Config.SQLALCHEMY_TRACK_MODIFICATIONS` | False |
| SECRET_KEY | Env / fallback | dev placeholder (not for prod) |

## Tables

### users

| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | Integer | PK | Yes (implicit) |
| username | String(80) | NOT NULL UNIQUE | Yes |
| email | String(120) | NOT NULL UNIQUE | Yes |
| password_hash | String(255) | NOT NULL | No |
| role | String(20) | NOT NULL DEFAULT 'user' | No |
| created_at | DateTime | NOT NULL DEFAULT utcnow | No |

### parking_spots

| Column | Type | Constraints |
|--------|------|-------------|
| id | String(10) | PK |
| status | String(20) | NOT NULL DEFAULT 'available' |
| location | String(100) | NOT NULL |
| description | Text | NULLABLE |
| created_at | DateTime | NOT NULL DEFAULT utcnow |

### reservations

| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | Integer | PK | Yes |
| spot_id | String(10) | FK→parking_spots.id NOT NULL | Yes |
| user_id | Integer | FK→users.id NOT NULL | Yes |
| name | String(100) | NOT NULL | No |
| reservation_date | Date | NOT NULL | Yes |
| status | String(20) | NOT NULL DEFAULT 'active' (migration adds) | No |
| created_at | DateTime | NOT NULL DEFAULT utcnow | No |
| updated_at | DateTime | NOT NULL DEFAULT/ONUPDATE utcnow | No |

### carpools

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| name | String(100) | NOT NULL |
| origin | String(200) | NOT NULL |
| destination | String(200) | NOT NULL |
| departure_time | DateTime | NOT NULL |
| return_time | DateTime | NULLABLE |
| max_passengers | Integer | NOT NULL DEFAULT 4 |
| current_passengers | Integer | NOT NULL DEFAULT 0 |
| notes | Text | NULLABLE |
| organizer_id | Integer | FK→users.id NOT NULL INDEX |
| created_at | DateTime | NOT NULL DEFAULT utcnow |
| updated_at | DateTime | NOT NULL DEFAULT/ONUPDATE utcnow |

### actions

| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | Integer | PK | Yes |
| action_type | String(50) | NOT NULL | Yes |
| username | String(80) | NOT NULL | Yes |
| timestamp | DateTime | NOT NULL DEFAULT utcnow | Yes |
| details | Text | NULLABLE | No |

## Foreign Keys & Cardinality

| Child Table | Column | Parent Table | On Delete Behavior | Noted |
|-------------|--------|-------------|--------------------|-------|
| reservations | spot_id | parking_spots.id | Application-level cascade (relationship) | delete-orphan in model |
| reservations | user_id | users.id | Application-level cascade | delete-orphan |
| carpools | organizer_id | users.id | Application-level cascade | delete-orphan |

`actions` table intentionally has no FK (username denormalized string) to preserve logs after user deletion.

## ER Diagram

```mermaid
erDiagram
	USER ||--o{ RESERVATION : makes
	USER ||--o{ CARPOOL : organizes
	PARKINGSPOT ||--o{ RESERVATION : allocates
	ACTION }o..o{ USER : username_copy

	USER { int id PK; string username; string email; string role; datetime created_at }
	PARKINGSPOT { string id PK; string status; string location; datetime created_at }
	RESERVATION { int id PK; string spot_id FK; int user_id FK; date reservation_date; string status }
	CARPOOL { int id PK; string name; datetime departure_time; int max_passengers; int current_passengers }
	ACTION { int id PK; string action_type; string username; datetime timestamp }
```

## Migration History

| Revision | Date | Summary |
|----------|------|---------|
| bf20dc5ca70c | 2025-06-26 | Add `status` column to `reservations` (server_default 'active') |

Only one migration present; base schema likely auto-created before versioning. Future evolution should formalize baseline migration.

## Seeding & Initial Data

* `run.py` creates admin user (`admin`) and sample users if absent.
* Sample parking spots (A1..D1) inserted with varied statuses.
* App factory also creates default admin using config-provided credentials if missing.

## Performance Considerations (Observed Potential)

| Area | Observation | Mitigation Idea |
|------|-------------|-----------------|
| Count queries in dashboards | Multiple aggregate queries per request | Precompute or cache metrics |
| Reservation double-book check | Point SELECT per create/update | Add unique index (spot_id, reservation_date) for enforcement |
| Carpool statistics | Iterates all carpools to sum capacity | Maintain denormalized counters |

## Suggested Index Additions (Not in Code)

* Composite index `(spot_id, reservation_date)` on `reservations` to enforce uniqueness & accelerate lookups.
* Index on `carpools.departure_time` (queries filter by future & date windows).

## Data Integrity Gaps

| Gap | Impact |
|-----|--------|
| No unique constraint for reservation spot/date | Race condition possible |
| Action.username not FK | Potential orphan naming inconsistency |
| Carpool passenger membership table missing | Cannot track actual user joins beyond counters |

## Compliance / Security Notes

* Passwords stored as bcrypt hashes (secure hashing, salt embedded).
* Secrets currently allow fallback development defaults — must override in production env.
* No PII beyond email; no encryption at rest.

All statements above sourced directly from model/migration code; no speculative schema added.
