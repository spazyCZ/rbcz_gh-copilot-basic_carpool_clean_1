# User Flow Diagrams

This document provides user flow diagrams for the main user journeys in the carpool application. These diagrams illustrate the steps users take to accomplish common tasks, supporting both development and onboarding.

---

## Mapping User Flows to Flask Views and Templates

| User Flow                    | Blueprint / View Module         | Example Endpoint(s)                                                            | Template(s) Used                                               |
|------------------------------|---------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------|
| User Registration and Login  | `auth` blueprint                | `[ /register ](/register)`, `[ /login ](/login)`                                | `[auth/register.html](auth/register.html)`, `[auth/login.html](auth/login.html)`          |
| Carpool Creation             | `main` or `carpool` blueprint   | `[ /carpools/create ](/carpools/create)`                                        | `[carpool/create.html](carpool/create.html)`                            |
| Reservation Booking          | `main` or `reservation` blueprint | `[ /carpools/<id>/reserve ](/carpools/<id>/reserve)`                            | `[reservation/create.html](reservation/create.html)`                        |
| Admin: User Management       | `admin` blueprint               | `[ /admin/users ](/admin/users)`, `[ /admin/users/<id> ](/admin/users/<id>)`      | `[admin/users.html](admin/users.html)`, `[admin/user_edit.html](admin/user_edit.html)`       |

---

## 1. User Registration and Login

```mermaid
flowchart TD
    Start(["<strong>🚀 START</strong>"]) --> Register["<strong>1. Registration Page</strong><br/>📄 Template: <a href='../carpool/templates/auth/register.html'><em>carpool/templates/auth/register.html</em></a>"]
    Register --> FillForm["<strong>2. Fill Registration Form</strong><br/>📝 User Input<br/>📄 Template: <a href='../carpool/templates/auth/register.html'><em>carpool/templates/auth/register.html</em></a>"]
    FillForm --> SubmitReg["<strong>3. Submit Registration</strong><br/>🔗 Endpoint: <em>auth.register</em>"]
    SubmitReg --> ValidateReg["<strong>4. System Validation</strong><br/>✅ Validate Input Data"]
    ValidateReg -- Valid --> CreateUser["<strong>5. Create User Account</strong><br/>💾 Save to Database"]
    CreateUser --> LoginPage["<strong>6. Redirect to Login</strong><br/>📄 Template: <a href='../carpool/templates/auth/login.html'><em>carpool/templates/auth/login.html</em></a>"]
    ValidateReg -- Invalid --> ShowError["<strong>❌ Show Validation Errors</strong><br/>📄 Template: <a href='../carpool/templates/auth/register.html'><em>carpool/templates/auth/register.html</em></a>"]
    LoginPage --> FillLogin["<strong>7. Enter Credentials</strong><br/>🔐 Username & Password<br/>📄 Template: <a href='../carpool/templates/auth/login.html'><em>carpool/templates/auth/login.html</em></a>"]
    FillLogin --> SubmitLogin["<strong>8. Submit Login</strong><br/>🔗 Endpoint: <em>auth.login</em>"]
    SubmitLogin --> ValidateLogin["<strong>9. Validate Credentials</strong><br/>🔍 Authentication Check"]
    ValidateLogin -- Success --> Dashboard["<strong>✅ Success: User Dashboard</strong><br/>📄 Template: <a href='../carpool/templates/main/dashboard.html'><em>carpool/templates/main/dashboard.html</em></a>"]
    ValidateLogin -- Failure --> LoginError["<strong>❌ Login Error</strong><br/>📄 Template: <a href='../carpool/templates/auth/login.html'><em>carpool/templates/auth/login.html</em></a>"]
```

---

## 2. Carpool Creation

```mermaid
flowchart TD
    Start(["<strong>🚀 START</strong>"]) --> Dashboard["<strong>1. User Dashboard</strong><br/>🏠 Main Interface<br/>📄 Template: <a href='../carpool/templates/main/dashboard.html'><em>carpool/templates/main/dashboard.html</em></a>"]
    Dashboard --> CreateCarpoolBtn["<strong>2. Click 'Create Carpool'</strong><br/>➕ Action Button"]
    CreateCarpoolBtn --> CarpoolForm["<strong>3. Fill Carpool Details</strong><br/>📝 Route, Date, Time, Seats<br/>📄 Template: <a href='../carpool/templates/carpool/create.html'><em>carpool/templates/carpool/create.html</em></a>"]
    CarpoolForm --> SubmitCarpool["<strong>4. Submit Carpool Form</strong><br/>🔗 Endpoint: <em>carpool.create</em>"]
    SubmitCarpool --> ValidateCarpool["<strong>5. System Validation</strong><br/>✅ Validate Form Data"]
    ValidateCarpool -- Valid --> SaveCarpool["<strong>6. Save Carpool</strong><br/>💾 Store in Database"]
    SaveCarpool --> CarpoolList["<strong>✅ Success: Carpool List</strong><br/>📋 View All Carpools<br/>📄 Template: <a href='../carpool/templates/carpool/list.html'><em>carpool/templates/carpool/list.html</em></a>"]
    ValidateCarpool -- Invalid --> CarpoolError["<strong>❌ Show Validation Errors</strong><br/>📄 Template: <a href='../carpool/templates/carpool/create.html'><em>carpool/templates/carpool/create.html</em></a>"]
```

---

## 3. Reservation Booking

```mermaid
flowchart TD
    Start(["<strong>🚀 START</strong>"]) --> CarpoolList["<strong>1. Browse Available Carpools</strong><br/>📋 List View<br/>📄 Template: <a href='../carpool/templates/carpool/list.html'><em>carpool/templates/carpool/list.html</em></a>"]
    CarpoolList --> SelectCarpool["<strong>2. Select Carpool</strong><br/>🎯 Choose Desired Trip"]
    SelectCarpool --> BookBtn["<strong>3. Click 'Book Reservation'</strong><br/>🎫 Booking Action"]
    BookBtn --> ReservationForm["<strong>4. Fill Reservation Details</strong><br/>📝 Pickup Point, Notes<br/>📄 Template: <a href='../carpool/templates/reservation/create.html'><em>carpool/templates/reservation/create.html</em></a>"]
    ReservationForm --> SubmitReservation["<strong>5. Submit Reservation</strong><br/>🔗 Endpoint: <em>reservation.create</em>"]
    SubmitReservation --> ValidateReservation["<strong>6. System Validation</strong><br/>✅ Check Availability & Data"]
    ValidateReservation -- Valid --> SaveReservation["<strong>7. Save Reservation</strong><br/>💾 Confirm Booking"]
    SaveReservation --> Confirmation["<strong>✅ Success: Booking Confirmed</strong><br/>🎉 Confirmation Details<br/>📄 Template: <a href='../carpool/templates/reservation/confirmation.html'><em>carpool/templates/reservation/confirmation.html</em></a>"]
    ValidateReservation -- Invalid --> ReservationError["<strong>❌ Show Validation Errors</strong><br/>📄 Template: <a href='../carpool/templates/reservation/create.html'><em>carpool/templates/reservation/create.html</em></a>"]
```

---

## 4. Admin: User Management

```mermaid
flowchart TD
    Start(["<strong>🚀 START</strong>"]) --> AdminLogin["<strong>1. Admin Login</strong><br/>🔐 Administrator Access<br/>📄 Template: <a href='../carpool/templates/auth/login.html'><em>carpool/templates/auth/login.html</em></a>"]
    AdminLogin --> AdminDashboard["<strong>2. Admin Dashboard</strong><br/>⚙️ Control Panel<br/>📄 Template: <a href='../carpool/templates/admin/dashboard.html'><em>carpool/templates/admin/dashboard.html</em></a>"]
    AdminDashboard --> UserMgmt["<strong>3. Select 'User Management'</strong><br/>👥 User Administration"]
    UserMgmt --> ViewUsers["<strong>4. View User List</strong><br/>📋 All System Users<br/>📄 Template: <a href='../carpool/templates/admin/users.html'><em>carpool/templates/admin/users.html</em></a>"]
    ViewUsers --> SelectUser["<strong>5. Select User</strong><br/>👤 Choose Target User"]
    SelectUser --> EditOrDelete["<strong>6. Edit or Delete User</strong><br/>✏️ Modify User Data<br/>📄 Template: <a href='../carpool/templates/admin/user_edit.html'><em>carpool/templates/admin/user_edit.html</em></a>"]
    EditOrDelete --> ConfirmAction["<strong>7. Confirm Action</strong><br/>✅ System Confirmation"]
    ConfirmAction --> UserMgmt
```

---

*For additional user flows, extend this document as needed.*
