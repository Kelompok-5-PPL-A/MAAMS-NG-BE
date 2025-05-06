#!/bin/bash
echo "Starting migration and seeding process..."
python manage.py migrate
python manage.py seed_causes --number=100
python manage.py dumpdata cause --indent 2 > cause/fixtures/causes.json
echo "Process completed successfully!"