#!/bin/bash
set -euo pipefail
umask 077

DB="/home/ubuntu/student-sindhu/instance/eduprime.db"
BACKUP_DIR="/home/ubuntu/eduprime-backups"
BUCKET="s3://eduprime-db-backups-sindhu-2026-1114/eduprime"

mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/eduprime-$(date -u +%Y%m%dT%H%M%SZ).db"

python3 - "$DB" "$BACKUP_FILE" <<'PY'
import sqlite3
import sys

source, destination = sys.argv[1:3]

with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src:
    with sqlite3.connect(destination) as dst:
        src.backup(dst)
        result = dst.execute("PRAGMA integrity_check").fetchone()[0]

if result != "ok":
    raise SystemExit("Database integrity check failed")

print("Database backup integrity: OK")
PY

aws s3 cp "$BACKUP_FILE" "$BUCKET/" --only-show-errors

echo "Backup uploaded successfully: $BACKUP_FILE"
