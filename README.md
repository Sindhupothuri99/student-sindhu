# EduPrime Student Management System

An extensible Flask-based academic administration starter for schools, colleges and multi-campus education groups. This project expands the supplied Student Management System documentation while retaining its Python/Flask and AWS deployment direction.

## Included modules

- Institution-scoped accounts and roles: Admin, Faculty, Student (plus a reserved Super Admin role)
- Password hashing, login sessions, CSRF protection and role checks
- User/account directory and student profile basics
- Course catalogue
- Attendance register
- Assignment publishing and student text submissions
- Examination calendar and result entry/viewing
- Institution notices
- Responsive dashboard and web UI

## Important scope and production note

This is a working starter application, not a certified or fully production-hardened enterprise SIS. It does not yet include fee/payment gateway integration, timetable scheduling, transport, hostel, library, parent portal, LMS content, online proctoring, biometric attendance, bulk imports, audit-log UI, SSO/SAML, or full multi-tenant Super Admin provisioning. These require institution-specific requirements, testing and integrations before a large school/college rollout.

The app currently uses SQLAlchemy with SQLite by default for easy local testing. For a production deployment, configure PostgreSQL (recommended for the relational academic data model). DynamoDB/Boto3 are included in dependencies to preserve the AWS extension path, but this starter's CRUD models currently use SQLAlchemy and do not write to DynamoDB. Do not claim DynamoDB integration until an adapter and tests are implemented.

## Requirements

- Python 3.10+
- pip
- For production: PostgreSQL and a supported Linux server

## Run locally (Windows PowerShell)

```powershell
cd eduprime_sms
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py -m app.seed
py run.py
```

Open http://127.0.0.1:5000

## Run locally (Linux/macOS)

```bash
cd eduprime_sms
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
python run.py
```

Open http://127.0.0.1:5000

## Demo account

- Email: `admin@eduprime.local`
- Password: `ChangeMeNow!2026`

Change this immediately. Use a unique high-entropy SECRET_KEY in `.env`, and never expose demo credentials on a public deployment.

## Production configuration

Set at least:
- `SECRET_KEY`: long random secret from a secret manager
- `DATABASE_URL`: PostgreSQL connection string, e.g. `postgresql+psycopg://user:password@host:5432/eduprime`
- `COOKIE_SECURE=1` behind HTTPS
- `FLASK_DEBUG=0`

Run behind Nginx + Gunicorn; do not expose Flask's development server to the internet. Use an EC2 instance profile / IAM role for AWS permissions rather than embedding AWS keys. Restrict security groups, enable HTTPS, configure backups, monitoring, log retention and database migrations.

## Suggested AWS deployment shape

Browser -> Route 53 / ACM HTTPS -> Nginx on EC2 or ALB -> Gunicorn/Flask -> PostgreSQL (RDS recommended). Use private subnets for the database, least-privilege IAM roles, S3 for controlled file storage, CloudWatch for logs/metrics, and automated backups. For high availability, deploy multiple app instances behind an ALB and use managed database backups/failover.

## Before using with real institutions

1. Confirm privacy, retention, consent and student-data requirements applicable to each institution and jurisdiction.
2. Add automated tests, migrations (Alembic/Flask-Migrate), audit logging and account recovery.
3. Add tenant provisioning and enforce tenant isolation in every query and background job.
4. Add file upload malware scanning and private object storage before accepting student documents.
5. Add rate limiting, security headers, password reset/MFA and administrative approval workflows.
6. Conduct security review, load testing, disaster recovery testing and accessibility review.

## Project structure

```text
eduprime_sms/
  app/
    __init__.py
    models.py
    auth.py
    core.py
    academics.py
    templates/
    static/
  config.py
  run.py
  requirements.txt
  .env.example
  README.md
```
