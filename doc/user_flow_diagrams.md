# User Flow Diagrams

All flows reconstructed strictly from existing route logic (`auth.py`, `main.py`, `api.py`, `admin.py`). Gaps are explicitly noted.

## Legend

| Symbol | Meaning |
|--------|---------|
| Rectangle | UI Page / Form |
| Parallelogram | User Input / Data Entry |
| Diamond | Decision / Branch |
| Cylinder | Database Persistence |
| Rounded | Start / End |

## Registration Flow

```mermaid
flowchart TD
  A([Start]) --> B[GET /register]
  B --> C{Authenticated?}
  C -- Yes --> D[Redirect /dashboard]
  C -- No --> E[Display Registration Form]
  E --> F[POST /register]
  F --> G{Form Valid?}
  G -- No --> E
  G -- Yes --> H[AuthService.create_user]
  H --> I{User Created?}
  I -- No --> E
  I -- Yes --> J[login_user]
  J --> K[Redirect /dashboard]
  K --> L([End])
```

## Login Flow

```mermaid
flowchart TD
  A([Start]) --> B[GET /login]
  B --> C{Authenticated?}
  C -- Yes --> D[Redirect /dashboard]
  C -- No --> E[Show Login Form]
  E --> F[POST /login]
  F --> G[Lookup user by username/email]
  G --> H{User Found?}
  H -- No --> E
  H -- Yes --> I[Verify Password]
  I --> J{Valid?}
  J -- No --> E
  J -- Yes --> K[login_user]
  K --> L[Redirect next or /dashboard]
  L --> M([End])
```

## Reservation Lifecycle (Create / Edit / Cancel)

```mermaid
flowchart TD
  A([Start]) --> B[User navigates /reservations/new]
  B --> C{Permission: can_make_reservation?}
  C -- No --> Z[Flash error + Redirect dashboard]
  C -- Yes --> D[Form Submission]
  D --> E[ReservationService.create_reservation]
  E --> F{Created?}
  F -- No --> D
  F -- Yes --> G[Redirect /reservations]
  G --> H[User views list]
  H --> I[Click Edit]
  I --> J[GET /reservations/<id>/edit]
  J --> K{Ownership OR Admin?}
  K -- No --> H
  K -- Yes --> L{Can be modified?}
  L -- No --> H
  L -- Yes --> M[POST update]
  M --> N[ReservationService.update_reservation]
  N --> O{Success?}
  O -- Yes --> H
  O -- No --> J
  H --> P[Click Cancel]
  P --> Q[POST /reservations/<id>/cancel]
  Q --> R{Authorized?}
  R -- No --> H
  R -- Yes --> S[ReservationService.cancel_reservation]
  S --> T{Success?}
  T -- Yes --> H
  T -- No --> H
  Z --> U([End])
```

## Carpool Create Flow

```mermaid
flowchart TD
  A([Start]) --> B[GET /carpools/new]
  B --> C{can_organize_carpool?}
  C -- No --> X[Flash error + Redirect dashboard]
  C -- Yes --> D[Display Carpool Form]
  D --> E[POST /carpools/new]
  E --> F[CarpoolService.create_carpool]
  F --> G{Created?}
  G -- No --> D
  G -- Yes --> H[Redirect /carpools]
  H --> I([End])
```

## Carpool Join / Leave Flow (API)

NOTE: Passenger membership model not implemented; service logic uses counters only.

```mermaid
flowchart TD
  A([Start]) --> B[POST /api/carpool/{id}/join]
  B --> C[Get carpool]
  C --> D{Exists?}
  D -- No --> Z[404]
  D -- Yes --> E{carpool.can_join()?}
  E -- No --> Z[400]
  E -- Yes --> F[CarpoolService.join_carpool]
  F --> G{Success?}
  G -- No --> Z[400]
  G -- Yes --> H[Return JSON success + seats]
  H --> I([End])
  A --> J[POST /api/carpool/{id}/leave]
  J --> K[Get carpool]
  K --> L{Exists?}
  L -- No --> Z
  L -- Yes --> M[CarpoolService.leave_carpool]
  M --> N{Success?}
  N -- No --> Z
  N -- Yes --> O[Return JSON success + seats]
  O --> I
```

## Admin Parking Management Flow

```mermaid
flowchart TD
  A([Start]) --> B[GET /admin/parking-spots]
  B --> C{Admin?}
  C -- No --> X[Redirect /dashboard]
  C -- Yes --> D[View Spots + Stats]
  D --> E[Create Spot Modal]
  E --> F[POST /admin/parking-spots/new]
  F --> G{Creation Success?}
  G -- No --> D
  G -- Yes --> D
  D --> H[Edit Spot]
  H --> I[POST /admin/parking-spots/<id>/edit]
  I --> J{Update Success?}
  J -- No --> D
  J -- Yes --> D
  D --> K[Delete Spot]
  K --> L[POST /admin/parking-spots/<id>/delete]
  L --> M{Deletion Success?}
  M -- No --> D
  M -- Yes --> D
  X --> N([End])
```

## Dashboard Data Refresh (AJAX)

```mermaid
sequenceDiagram
  autonumber
  participant U as Browser
  participant API as /api endpoints
  participant DB as Database
  U->>API: GET /api/dashboard-stats
  API->>DB: Aggregate reservations/carpools
  DB-->>API: Counts & user-specific data
  API-->>U: JSON stats
  U->>API: GET /api/reservations-chart-data
  API->>DB: Count per day (7 days)
  DB-->>API: Aggregated list
  API-->>U: JSON chart payload
```

## Identified Flow Gaps

| Flow | Gap | Impact |
|------|-----|--------|
| Carpool passenger membership | No explicit table or relationship in model | Data integrity & seat tracking risk |
| Carpool cancel | Deletes entire record immediately | Potential audit loss beyond Action log |
| Reservation cancel | Depends on service (status vs delete) | Inconsistent historical reporting |

All diagrams and notes grounded in observed code; no speculative endpoints added.
