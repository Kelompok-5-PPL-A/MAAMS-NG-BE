#!/bin/bash

# Parse DATABASE_URL
DB_URL=${DATABASE_URL}
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

# Get current version from Django migrations
VERSION=$(python manage.py showmigrations MAAMS_NG_BE | grep -o '[0-9]\{4\}_[0-9]\{2\}_[0-9]\{2\}_[0-9]\{6\}' | tail -n 1)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/app/backups"
BACKUP_FILE="${BACKUP_DIR}/backup_${VERSION}_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database backup
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F c \
    -f "${BACKUP_FILE}"

# Store backup metadata
echo "{
    \"version\": \"${VERSION}\",
    \"timestamp\": \"${TIMESTAMP}\",
    \"backup_file\": \"${BACKUP_FILE}\",
    \"app_version\": \"$(python -c 'import setup; print(setup.version)')\"
}" > "${BACKUP_DIR}/backup_${VERSION}_${TIMESTAMP}.json"

# Upload backup to Google Cloud Storage
gsutil cp "${BACKUP_FILE}" "gs://${GCS_BUCKET}/database-backups/"
gsutil cp "${BACKUP_DIR}/backup_${VERSION}_${TIMESTAMP}.json" "gs://${GCS_BUCKET}/database-backups/"

echo "Backup completed: ${BACKUP_FILE}" 