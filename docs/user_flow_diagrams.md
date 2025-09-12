## User Flow Diagrams

### Mapping Table (Flows → Views/Templates)
| Flow | Blueprint Route(s) | Template(s) |
| ---- | ------------------ | ----------- |
| Registration | /auth/register | `auth/register.html` |
| Login | /auth/login | `auth/login.html` |
| Dashboard Overview | /dashboard | `dashboard.html` |
| Make Reservation | /reservations/new | `reservations/make.html` |
| Edit Reservation | /reservations/{id}/edit | `reservations/edit.html` |
| Cancel Reservation | /reservations/{id}/cancel (POST) | Redirect to `reservations/list.html` |
| List Reservations | /reservations | `reservations/list.html` |
| Create Carpool | /carpools/new | `carpools/create.html` |
| Carpool Detail | /carpools/{id} | `carpools/detail.html` |
| Admin Users | /admin/users | `admin/users.html` |
| Admin Parking | /admin/parking-spots | `admin/parking.html` |
| Admin Dashboard | /admin/ | `admin/dashboard.html` |

### Flow: User Registration
```mermaid
flowchart TD
    A[🚀 <strong>Start</strong><br/>Visit /auth/register] --> B[📄 Form:<br/><a href='../templates/auth/register.html'><em>register.html</em></a>]
    B -->|Submit valid data| C[🔗 Endpoint:<br/>POST /auth/register]
    C --> D{Username/Email Unique?}
    D -->|No| E[❌ Show validation errors]
    E --> B
    D -->|Yes| F[🔐 Hash Password & Persist]
    F --> G[🧾 Auto Login Attempt]
    G --> H[✅ Redirect /dashboard<br/><a href='../templates/dashboard.html'><em>dashboard.html</em></a>]
```

### Flow: User Login
```mermaid
flowchart TD
    L1[🚀 Visit /auth/login] --> L2[📄 <a href='../templates/auth/login.html'><em>login.html</em></a>]
    L2 -->|Submit| L3[🔗 POST /auth/login]
    L3 --> L4{Credentials Valid?}
    L4 -->|No| L5[❌ Flash error & re-render]
    L5 --> L2
    L4 -->|Yes| L6[🧠 Session Created + Audit Log]
    L6 --> L7[✅ Redirect next or /dashboard]
```

### Flow: Make Reservation
```mermaid
flowchart TD
    R1[🚀 /reservations/new] --> R2[📄 Form:<br/><a href='../templates/reservations/make.html'><em>make.html</em></a><br/>Load available spots]
    R2 -->|Submit| R3[🔗 POST /reservations/new]
    R3 --> R4{Spot Available & Not Double Booked?}
    R4 -->|No| R5[❌ Error Flash]
    R5 --> R2
    R4 -->|Yes| R6[💾 Create Reservation + Log]
    R6 --> R7[✅ Redirect /reservations<br/><a href='../templates/reservations/list.html'><em>list.html</em></a>]
```

### Flow: Edit Reservation
```mermaid
flowchart TD
    ER1[🚀 /reservations/{id}/edit] --> ER2[🔎 Load Reservation]
    ER2 --> ER3{Ownership/Admin?}
    ER3 -->|No| ER4[❌ Flash Permission Error]
    ER4 --> ER8[↩ Redirect /reservations]
    ER3 -->|Yes| ER5[📄 <a href='../templates/reservations/edit.html'><em>edit.html</em></a>]
    ER5 -->|Submit| ER6[🔗 POST Edit]
    ER6 --> ER7{New Spot/Date Valid?}
    ER7 -->|No| ER5
    ER7 -->|Yes| ER9[💾 Update + Log]
    ER9 --> ER8[✅ Redirect /reservations]
```

### Flow: Create Carpool
```mermaid
flowchart TD
    C1[🚀 /carpools/new] --> C2[📄 <a href='../templates/carpools/create.html'><em>create.html</em></a>]
    C2 -->|Submit| C3[🔗 POST /carpools/new]
    C3 --> C4{Departure Future?}
    C4 -->|No| C5[❌ Error Flash]
    C5 --> C2
    C4 -->|Yes| C6{Return After Departure?}
    C6 -->|No| C5
    C6 -->|Yes| C7[💾 Save + Log]
    C7 --> C8[✅ Redirect /carpools]
```

### Flow: Admin User Creation
```mermaid
flowchart TD
    AU1[🚀 /admin/users] --> AU2[🛂 Admin Check]
    AU2 -->|Fail| AU3[❌ Redirect /dashboard]
    AU2 -->|Pass| AU4[📄 Users List + Create Modal:<br/><a href='../templates/admin/users.html'><em>users.html</em></a>]
    AU4 -->|Submit Form| AU5[🔗 POST /admin/users/new]
    AU5 --> AU6{Unique Username/Email?}
    AU6 -->|No| AU7[❌ Validation Errors]
    AU7 --> AU4
    AU6 -->|Yes| AU8[💾 Create User + Log admin_action]
    AU8 --> AU4[✅ Refresh List]
```

### Flow: Dashboard Data (AJAX)
```mermaid
flowchart TD
    D1[👁 View dashboard.html] --> D2[🧠 JS requests /api/dashboard-stats]
    D2 --> D3[📊 Stats JSON]
    D3 --> D4[📈 Render charts via charts.js]
```

### Flow: Quick Reservation (API)
```mermaid
flowchart TD
    Q1[🖱 UI Trigger Quick Reserve] --> Q2[🔗 POST /api/quick-reservation JSON]
    Q2 --> Q3{Permission + Availability?}
    Q3 -->|No| Q4[❌ Error Toast]
    Q3 -->|Yes| Q5[💾 Create + Log]
    Q5 --> Q6[✅ Update UI Spots List]
```

### Flow: Error Handling (Auth Protected Route)
```mermaid
flowchart TD
    E1[🔐 Visit /dashboard unauth] --> E2[Flask-Login Intercept]
    E2 --> E3[Redirect /auth/login?next=/dashboard]
    E3 --> E4[User Logs In]
    E4 --> E5[Redirect to original /dashboard]
```

### Notes & Visual Legend
- 🚀 START / entry
- ✅ Success path
- ❌ Error path
- 🔗 Endpoint interaction
- 📄 Template rendering
- 💾 Persistence + Audit log
- 🔎 Authorization / ownership validation

### Identified Gaps
- Carpool passenger identity not represented in flows (counter-only).
- Action logging fields mismatch for profile update (ip/user_agent).
