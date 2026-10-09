# Hostel Management System (HMS) — Team 3

A web-based Hostel Management System mini-project based on the supplied Team 3 SRS and Software Test Plan.

## Implemented starter modules
- Student records and registration status
- Room inventory and bed allocation records
- Fee invoices and payment records (manual/reference recording; no live payment gateway)
- Complaint and maintenance tracking
- Leave/outing requests
- Visitor entry/exit logs
- Mess meal attendance
- Notices
- Audit event records
- Admin console and summary dashboard
- Basic automated tests and GitHub Actions CI

## Technology
- Python 3.12+
- Django 5.x
- SQLite for local development
- Django Admin for authenticated management UI
- GitHub Actions for checks and tests

The SRS permits Django/Flask or Laravel and PostgreSQL/MySQL. This starter chooses Django and SQLite for easy local setup. A production or final evaluated deployment should use the stack and database approved by the team/guide.

## Run locally (Windows PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations hostel
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open `http://127.0.0.1:8000/` for the dashboard and `http://127.0.0.1:8000/admin/` for the administration console.

If Python 3.12 is not installed, use an installed Python version supported by the selected Django release.

## Tests
```powershell
python manage.py test
python manage.py check
```
GitHub Actions runs configuration checks, migrations and tests on pushes and pull requests.

## Important limitations / next steps
- This is a functional starter, not a claim that every SRS acceptance criterion has been fully implemented or verified.
- The dashboard uses Django Admin for CRUD workflows; a dedicated role-specific student portal is a future sprint task.
- Payment gateway, email/SMS and institutional SIS integrations are not connected. Payment records are only administrative records.
- Configure role groups and object-level permissions before real users or sensitive data are used.
- Production deployment needs environment-based secrets, HTTPS/TLS, database backups, logging/retention configuration and security review.
- Add migration files, tests and requirement-to-test traceability as features evolve.

## Documentation
Place the team's approved documents under `docs/`, for example:
- `docs/HMS_SRS.pdf`
- `docs/HMS_Software_Test_Plan.pdf`
- `docs/HMS_Software_Architecture_and_Design_Specification.docx`

## Team
Team 3 — Meghana P, B S Sharath Chandra Reddy, Adarsha V, Mohammadnoor Sirasgi.
