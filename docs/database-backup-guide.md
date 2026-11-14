# EduPrime Database Backup and Restore Guide

## 1. Overview

EduPrime uses an SQLite database to store application data. Database backups are uploaded to an Amazon S3 bucket to protect data if the EC2 instance is lost.

## 2. AWS Services Used

- Amazon EC2 – Runs the EduPrime application.
- Amazon S3 – Stores database backups.
- AWS IAM Role – Allows EC2 to upload and download backups securely.
- Linux Cron – Runs automatic daily backups.

## 3. S3 Backup Configuration

S3 bucket: `eduprime-db-backups-sindhu-2026-1114`

Region: `ap-south-1`

Security settings:
- Block public access enabled.
- Bucket versioning enabled.
- Server-side encryption enabled.

## 4. Backup Process

The script `scripts/eduprime-backup.sh`:

1. Reads the live SQLite database.
2. Creates a consistent database backup.
3. Checks database integrity.
4. Uploads the backup to S3.

Run manually:

```bash
./scripts/eduprime-backup.sh
```

## 5. Automatic Backup

A Linux cron job runs the backup every day at 2:00 AM IST.

Cron configuration:

```bash
30 20 * * * /home/ubuntu/eduprime-backup.sh >> /home/ubuntu/eduprime-backup.log 2>&1
```

## 6. Restore Process

The script `scripts/restore-database.sh`:

1. Lists available S3 backups.
2. Downloads the selected backup.
3. Checks SQLite database integrity.
4. Saves the downloaded backup locally on EC2.

Run:

```bash
./scripts/restore-database.sh
```

The script does not overwrite the live database.

## 7. Security

- Database files are excluded from Git using `.gitignore`.
- Environment files and credentials are not committed to GitHub.
- EC2 accesses S3 through an IAM role.
- The S3 bucket is not publicly accessible.

## 8. Important Note

Before deleting the S3 bucket or terminating EC2, download a database backup to a separate trusted location and verify it.

## 9. Project Files

- `scripts/eduprime-backup.sh`
- `scripts/restore-database.sh`
- `docs/database-backup-guide.md`
