# Script for manual triggering in production
import os

def seed_and_migrate():
    # Perform migrations
    os.system("python manage.py migrate")
    
    # Perform data seeding for question and cause models
    os.system("python manage.py seed question --number=2")
    os.system("python manage.py seed cause --number=3")

    # Perform Load data from Fixtures
    # os.system("python manage.py loaddata cause/fixtures/data.json")
    # os.system("python manage.py loaddata question/fixtures/data.json")

if __name__ == "__main__":
    seed_and_migrate()