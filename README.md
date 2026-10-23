# Real-Time College Library Seat Reservation Management System

A web application for managing library seat reservations in real-time for a college library. Built with **Python (Flask)**, **SQLite**, and **Tailwind CSS**.

---

## Features

- 🔐 **Student Login & Registration** using College Registration Number
- 🗺️ **Interactive Floor Plan** with a realistic top-down view of the library
  - Windows, aisles, and walkways rendered visually
  - Circular, rectangular, and cubicle seats placed as in real life
  - Dynamic adaptive layouts customized for Floor 1, Floor 2, and Floor 3
- 🟢 **Live Seat Availability** with color-coded status (Green = Available, Red = Occupied, Blue = Selected)
- ⏳ **Live Countdown Timer** in booking portal showing remaining time until 12:30 AM library closing
- 🌙 **Automatic 12:30 AM Night Expiry** that automatically updates booking records to 'Expired' and frees up seats
- 🕐 **Time-Slot Based Booking** (1-hour slots, 7:00 AM – 11:00 PM)
- 📅 **Same-Day Booking Only** (bookings open at 7:00 AM each day)
- 📋 **User Reservation History** with real-time active / expired indicators
- 📞 **Helpline & Issue Corner**
- 📖 **Library Info Page** with rules, timings, and floor directory

---

## Library Layout

| Floor | Cubicles | Circular Tables (8 seats) | Rectangular Tables (4 seats) |
|-------|----------|---------------------------|-------------------------------|
| 1st   | 30       | 10                        | 30                            |
| 2nd   | 15       | 2                         | 15                            |
| 3rd   | 15       | 2                         | 15                            |

**Ground Floor** (no reservations): Circulation Help Desk, Self Check-out, Periodical Section, Director's Office, Braille Section, WEB OPAC.

---

## Library Hours

| Session | Timings |
|---------|---------|
| Regular | 7:30 AM – 12:30 AM (All days) |
| Digital Library | 24×7 via campus network |
| Book Issue | Closes at 7:00 PM |
| Night Library | 9:00 PM – 12:30 AM (Not for 1st years) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Auth | Flask-Login, Werkzeug password hashing |
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JavaScript |

---

## Project Structure

```
library-system/
├── app/
│   ├── __init__.py        # App factory, DB & Login setup
│   ├── models.py          # User, Seat, Reservation models
│   ├── routes.py          # All routes, timer & auto-expiry API endpoints
│   ├── templates/
│   │   ├── base.html      # Shared layout & navbar
│   │   ├── index.html     # Home / Info page
│   │   ├── login.html     # Login page
│   │   ├── register.html  # Registration page
│   │   ├── dashboard.html # Live floor plan, booking & countdown timer
│   │   ├── history.html   # User reservation history
│   │   └── helpline.html  # Helpline & issue reporting
│   └── static/
├── run.py                 # App entry point
├── seed.py                # Seed DB with all library seats
├── requirements.txt       # Python dependencies
└── .gitignore
```

---

## Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/paularitra06-web/Real-Time-College-Library-Seat-Reservation-Management-System.git
cd Real-Time-College-Library-Seat-Reservation-Management-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed the database (first time only)
```bash
python seed.py
```

### 4. Run the application
```bash
python run.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## Usage

1. Go to `http://127.0.0.1:5000` and click **Register**
2. Create an account using your college registration number (e.g. `21BCE1234`)
3. Log in and navigate to the **Dashboard**
4. Select a **Floor**, **Time Slot**, and click **Check Availability**
5. Click a **green seat** to select it, then click **Book Selected Seat**
6. Once booked, a **Live Countdown Timer** appears showing remaining hours/minutes until 12:30 AM closing
7. View all bookings and active status under **My History**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/seats?floor=1&date=YYYY-MM-DD&time=9` | Get seat availability |
| `POST` | `/api/book` | Book a seat |
| `GET` | `/api/active-booking` | Get current user's active reservation and seconds remaining until 12:30 AM |

---

## Notes

- Seat bookings are **same-day only** and open at **7:00 AM**
- Each booking can be used up to **12:30 AM** closing time of that night
- After **12:30 AM**, all active bookings automatically expire
- The `library.db` file is excluded from version control (`.gitignore`)
- Run `seed.py` once to populate the database with all seats
