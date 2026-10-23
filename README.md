# Luxury Wheels Desktop

**Version:** 1.0.0  
**Status:** Final course project — desktop edition  
**Technology:** Python 3, CustomTkinter, SQLite

## About the Project

Luxury Wheels Desktop is a vehicle rental management application developed in Python as a final course project. It provides a desktop interface for managing vehicles, clients, reservations, and payment methods, with an overview dashboard and CSV exports.

This desktop edition replaces the Flask web interface with a CustomTkinter interface. The earlier Flask implementation may remain in the development folder for reference, but it is not required to launch the desktop application.

## Technologies Used

- Python 3
- CustomTkinter and Tkinter/ttk
- SQLite (`sqlite3`)
- tkcalendar (calendar date selectors)
- Werkzeug (password hashing and verification)
- Pillow (image support)
- Git and GitHub (version control)

## Features

### User Authentication

- Login and logout
- Password hashing and verification
- Access to management pages after authentication

### Vehicle Management

- Create, view, update, search, and delete vehicles
- Manage categories, types, transmission, capacity, daily prices, and status
- Track revision, inspection, and legalization dates
- Choose optional dates from a calendar or leave them blank
- Prevent deletion of vehicles with associated reservations
- Export vehicle records to CSV

### Client Management

- Create, view, update, search, and delete clients
- Store contact information and NIF
- Prevent duplicate NIF values
- Prevent deletion of clients with associated reservations
- Export client records to CSV

### Reservation Management

- Create, view, update, search, and delete reservations
- Select rental start and end dates using calendars
- Validate date ranges and prevent overlapping reservations
- Prevent reservations for vehicles under maintenance
- Calculate rental prices automatically
- Associate clients, vehicles, and payment methods with reservations
- Export reservation records to CSV

### Payment Method Management

- Create, view, update, search, and delete payment methods
- Prevent duplicate names
- Prevent deletion of methods associated with reservations
- Export payment methods to CSV

### Dashboard

- Monthly reservation and revenue summary
- Currently rented vehicles and remaining rental days
- Reservation overview
- Recently registered clients
- Available vehicles by category and type
- Upcoming revision and inspection alerts

### Additional Features

- Dark-themed desktop interface with gold accents
- Data validation and error messages
- SQLite foreign-key relationships
- CSV exports for the four management modules

## Project Structure

```text
Luxury_Wheels_Desktop/
├── images/
│   └── logo.png
├── main.py
├── database.py
├── models.py
├── vehicles_page.py
├── clients_page.py
├── reservations_page.py
├── payment_methods_page.py
├── table_style.py
├── requirements.txt
├── README.md
├── tests/                  # Include only tests applicable to this edition
├── luxury_wheels.db        # Created locally; do not publish real customer data
└── venv/                   # Local virtual environment; do not commit
```

The earlier `app.py`, Flask templates, and static files are not needed to run the desktop edition. Keep them separately if they are required for coursework or historical reference.

## Installation

### 1. Get the Project

Clone the repository, or extract the submitted project folder:

```bash
git clone <repository-url>
cd Luxury_Wheels_Desktop
```

Replace `<repository-url>` with the actual repository address. If using a ZIP file, open a terminal in the extracted folder instead.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The supplied `requirements.txt` may still include Flask dependencies from the original web version. They are not required for the desktop interface, provided no retained code imports them.

## Database Setup

Before the first run, initialize the SQLite database:

```bash
python database.py
```

This creates the required tables and, if absent, a demonstration administrator account.

The database contains five main tables:

- `users`
- `vehicles`
- `clients`
- `payment_methods`
- `reservations`

**Important:** Back up an existing `luxury_wheels.db` before replacing files or preparing the submission. Do not commit a database containing real personal information.

## Demonstration Administrator

The current database initialization script creates these **local demonstration** credentials if the account does not already exist:

- **Email:** `admin@luxurywheels.com`
- **Password:** `Luxury123`
- **Role:** `admin`

These credentials are for course demonstrations only. The hard-coded password and any prefilled login fields must be removed or replaced with a secure setup procedure before production use.

## Running the Desktop Application

Start the application from the project directory:

```bash
python main.py
```

The application opens in a desktop window; no web browser or Flask server is required.

## Testing

The desktop interface has been manually checked for navigation and common management operations, including creation, editing, deletion, search, CSV exports, date selection, and reservation validation.

If the `tests/` directory contains automated tests compatible with the current desktop models, run them with:

```bash
python -m unittest discover -s tests -v
```

Automated test results from the earlier Flask version should not be reported as results for this desktop edition without rerunning and verifying them.

## Logging

A `luxury_wheels.log` file may be present from the earlier Flask implementation. Logging in the desktop edition should be described as an active feature only after verifying that the current application writes to it.

## Notes for Submission

- Include the application source code, `requirements.txt`, README, and required image assets.
- Exclude the `venv/` folder, `__pycache__/`, temporary files, and logs.
- Decide whether to provide a clean demonstration database or require the evaluator to run `python database.py`.
- Do not include real client data or personal credentials.
