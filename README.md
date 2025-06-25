# rbcz_gh-copilot-basic_carpool
Flask GUI application for parking reservations

## Context:
Create ultra modern fancy gui
for parking reservations using Flask and SQLite. The application allows users to manage parking spots, make reservations, and view available parking places.




## Key Features:

Database reservation and parking places store to SQLite

Simple GUI for managing parking reservations

List available parking places

Create, update, and delete reservations

Avoid double-booking

Simple authentication


# Datový model

Diagram níže znázorňuje strukturu databáze

```mermaid
erDiagram
    ParkingSpot {
        string id PK "e.g., A1, B2"
        string status "free or reserved"
        string location "e.g., Level A"
    }
    Reservation {
        string spot_id FK "e.g., A1, B2"
        string name "Name of person making reservation"
        date reservation_date "Date of reservation"
    }
    User {
        string username PK "e.g., admin, user1"
        string password "Plain text password (security issue)"
        string role "administrator, user, or guest"
        string email "User's email address"
    }
    Action {
        string action_type "e.g., backup"
        datetime timestamp "When the action occurred"
    }
    
    ParkingSpot ||--o{ Reservation : "is_reserved_by"
    User ||--o{ Reservation : "can_make"
    User ||--o{ Action : "performs"
```

Hlavní entity v aplikaci:
- **ParkingSpot** - Parkovací místa definovaná v SQLite databázi
- **Reservation** - Rezervace uložené v SQLite databázi s parkovacím místem jako klíčem
- **User** - Uživatelské účty uložené v SQLite databázi
- **Action** - Systémové akce zaznamenané v SQLite databázi


