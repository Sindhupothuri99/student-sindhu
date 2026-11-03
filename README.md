# EduPrime — Student Management System

EduPrime is a role-based Student Management System built with Python Flask, SQLAlchemy and PostgreSQL. It provides Admin, Faculty and Student workspaces and is structured for deployment on AWS EC2 using Gunicorn and Nginx.

## Features
- Secure login, hashed passwords, CSRF protection and role-based authorization.
- Admin: create accounts, student/faculty profiles, courses, publish notices and enable/disable accounts.
- Faculty: view students, mark attendance for assigned courses, publish assignments, schedule exams and enter results.
- Student: view attendance, assignments, exam schedule and results; submit assignments.
- SQLAlchemy relational models: users, students, faculty, courses, attendance, assignments, submissions, exams, results and notices.
- Responsive Bootstrap UI; SQLite fallback for local development.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```
Edit `.env` and set a strong unique `SECRET_KEY`, `ADMIN_PASSWORD` (10+ characters), and `DATABASE_URL`. For local SQLite set `DATABASE_URL=sqlite:///eduprime.db`.
```bash
set -a && source .env && set +a
python -m app.seed
python run.py
```
Open http://127.0.0.1:5000. The seed script refuses to create a default password.

## PostgreSQL
```env
DATABASE_URL=postgresql+psycopg://eduprime:YOUR_PASSWORD@127.0.0.1:5432/eduprime
```
Create the database/user in PostgreSQL, then run `python -m app.seed`.

## AWS EC2 deployment
1. Launch Ubuntu EC2 and allow inbound 80/443; restrict SSH to your IP. Keep PostgreSQL private (prefer RDS).
2. Install Python, PostgreSQL client/server as required, Nginx and Git; clone this repository to `/opt/eduprime`.
3. Create a virtualenv, install requirements, and configure `.env` with PostgreSQL URL and a long random secret.
4. Run `python -m app.seed` once to create tables and the first administrator.
5. Run Gunicorn: `gunicorn --workers 3 --bind 127.0.0.1:8000 'app:create_app()'`.
6. Configure Nginx as reverse proxy to 127.0.0.1:8000 and enable HTTPS with Certbot or an AWS load balancer/ACM. Set `COOKIE_SECURE=1` after HTTPS is active.

Example systemd ExecStart:
`/opt/eduprime/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 'app:create_app()'`

## Project layout
```text
app/
  __init__.py   # Flask app factory, SQLAlchemy models and role-protected routes
  seed.py       # Database initialization and first admin account
config.py
run.py
requirements.txt
.env.example
```

## Production checklist
This is a functional starter, not a certified enterprise SIS. Before real student data is used, add Alembic/Flask-Migrate migrations, audit logging, password reset/MFA, rate limiting, backups and restore tests, tenant isolation, monitoring, accessibility and security reviews. Use HTTPS, rotate secrets, never commit `.env`, and use unique strong passwords. Review authorization and operational controls for your institution before production rollout.
