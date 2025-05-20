#!/bin/bash

# Parse DATABASE_URL
DB_URL=${DATABASE_URL}
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

# Function to get the latest backup for a specific version
get_backup_for_version() {
    local version=$1
    local backup_file=$(gsutil ls "gs://${GCS_BUCKET}/database-backups/backup_${version}_*.sql" | sort -r | head -n 1)
    echo "$backup_file"
}

# Function to get the backup metadata
get_backup_metadata() {
    local backup_file=$1
    local metadata_file=$(echo "$backup_file" | sed 's/\.sql$/.json/')
    gsutil cat "$metadata_file"
}

# Get the version to rollback to
VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Error: Version parameter is required"
    exit 1
fi

# Get the backup file for the specified version
BACKUP_FILE=$(get_backup_for_version "$VERSION")
if [ -z "$BACKUP_FILE" ]; then
    echo "Error: No backup found for version $VERSION"
    exit 1
fi

# Download the backup file
LOCAL_BACKUP="/app/backups/restore_${VERSION}.sql"
gsutil cp "$BACKUP_FILE" "$LOCAL_BACKUP"

# Get backup metadata
METADATA=$(get_backup_metadata "$BACKUP_FILE")
APP_VERSION=$(echo "$METADATA" | jq -r '.app_version')

echo "Restoring database to version $VERSION (App version: $APP_VERSION)"

# Restore the database
PGPASSWORD="${DB_PASSWORD}" pg_restore \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -c \
    -v \
    "$LOCAL_BACKUP"

# Clean up
rm "$LOCAL_BACKUP"

echo "Database restore completed for version $VERSION" 