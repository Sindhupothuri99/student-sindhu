#!/bin/bash
set -euo pipefail

BUCKET="s3://eduprime-db-backups-sindhu-2026-1114/eduprime"
RESTORE_DIR="$HOME/eduprime-restore"

mkdir -p "$RESTORE_DIR"

echo "Available database backups:"
aws s3 ls "$BUCKET/"

read -rp "Enter backup filename: " BACKUP_FILE

DESTINATION="$RESTORE_DIR/$BACKUP_FILE"

aws s3 cp "$BUCKET/$BACKUP_FILE" "$DESTINATION"

python3 - "$DESTINATION" <<'PY'
import sqlite3
import sys

path = sys.argv[1]

with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
    result = db.execute("PRAGMA integrity_check").fetchone()[0]

if result != "ok":
    raise SystemExit("Database integrity check failed")

print("Restore file integrity: OK")
PY

echo "Backup downloaded safely to: $DESTINATION"
echo "Live database has NOT been changed."
