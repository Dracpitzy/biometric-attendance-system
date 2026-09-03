## Staff Attendance System

A Django REST Framework backend for tracking staff attendance via fingerprint-scan check-in/check-out, with department management and automated weekly email reports.

## Features

- **Department & Staff management** — full CRUD via DRF `ModelViewSet`s
- **Fingerprint enrollment** — associate a device fingerprint (`device_user_id` / `fingerprint_template`) with a staff member, or remove it
- **Attendance scanning** — a single `/scan` endpoint that automatically determines whether a fingerprint scan is a check-in or check-out for the day
- **Live presence tracking** — see which staff are currently checked in
- **Automated weekly reports** — generates a plain-text attendance summary for the past 7 days and emails it to an admin address
- **Scheduled reporting** — a Django management command designed to run via Windows Task Scheduler

## Tech Stack

- Python / Django
- Django REST Framework
- SQL database (via Django ORM — swap in Postgres/MySQL/SQLite as configured)
- Django's `EmailMessage` for report delivery


## Data Models

### `Department`
| Field | Type | Notes |
|---|---|---|
| `name` | CharField | unique |

### `Staff`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `staff_id` | CharField | unique, indexed |
| `first_name`, `last_name` | CharField | |
| `phone_number` | CharField | validated format |
| `gender` | CharField | `M` / `F` |
| `department` | ForeignKey → Department | nullable |
| `position` | CharField | |
| `fingerprint_template` | BinaryField | raw fingerprint data |
| `device_user_id` | PositiveIntegerField | unique, maps to the fingerprint device's user ID |
| `status` | CharField | `active` / `suspended` / `terminated` |
| `date_joined`, `is_active`, `created_at`, `updated_at` | | |

### `AttendanceLog`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `staff` | ForeignKey → Staff | |
| `log_type` | CharField | `check_in` / `check_out` |
| `timestamp` | DateTimeField | auto-set on creation |

## API Endpoints

### Staff app
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/departments/` | List / create departments |
| GET/PUT/PATCH/DELETE | `/departments/{id}/` | Retrieve / update / delete a department |
| GET/POST | `/staff/` | List / create staff |
| GET/PUT/PATCH/DELETE | `/staff/{id}/` | Retrieve / update / delete a staff member |
| POST | `/staff/{id}/enroll-fingerprint/` | Attach a `device_user_id` and/or `fingerprint_template` to a staff member |
| POST | `/staff/{id}/remove-fingerprint/` | Clear a staff member's fingerprint enrollment |

### Attendance app
| Method | Endpoint | Description |
|---|---|---|
| GET | `/logs/` | List attendance logs (read-only) |
| GET | `/logs/{id}/` | Retrieve a single log |
| POST | `/logs/scan/` | Record a check-in or check-out from a `device_user_id` (auto-detects which) |
| GET | `/logs/currently-in/` | List staff who are checked in but not yet checked out today |

## Weekly Email Report

`attendance/services.py` provides:
- `generate_weekly_attendance_report()` — builds a plain-text summary of all attendance logs from the last 7 days
- `send_weekly_attendance_email()` — sends that summary to `settings.ADMIN_EMAIL` via `settings.DEFAULT_FROM_EMAIL`

Run manually:
```bash
python manage.py send_weekly_report
```

### Scheduling (Windows Task Scheduler)

The command is set up to run automatically on a weekly schedule:
- **Program:** path to the project's virtual environment `python.exe`
- **Arguments:** `manage.py send_weekly_report`
- **Start in:** the project root directory

## Setup

1. Clone the repository and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure email and admin settings in `settings.py` / environment variables:
   ```python
   EMAIL_HOST = "..."
   EMAIL_HOST_USER = "..."
   EMAIL_HOST_PASSWORD = "..."
   DEFAULT_FROM_EMAIL = "..."
   ADMIN_EMAIL = "..."
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Notes

- `device_user_id` is the link between a fingerprint scanner device and a `Staff` record; the `/scan` endpoint expects this ID from the scanning device/hardware integration.
- Staff must have `is_active=True` and a matching `device_user_id` to be recognized by `/scan`.
