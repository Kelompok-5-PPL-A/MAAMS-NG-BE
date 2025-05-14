import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections


class Command(BaseCommand):
    help = 'Provides options for rolling back data seeding operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'rollback_type',
            type=str,
            choices=['flush', 'reset_db'],
            help='Type of rollback: "flush" to clear all data while preserving tables, "reset_db" to reset entire database including tables'
        )
        parser.add_argument(
            '--app',
            type=str,
            help='App name for reset_db operation (required when using reset_db)',
            required=False
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Skip confirmation prompts',
            required=False
        )

    def handle(self, *args, **options):
        rollback_type = options['rollback_type']
        app_name = options.get('app', None)
        noinput = options.get('noinput', False)
        
        # Validate inputs
        if rollback_type == 'reset_db' and not app_name:
            raise CommandError('App name is required when using reset_db option')
            
        # Confirm dangerous operation
        if not noinput:
            confirmation_message = (
                f"You are about to perform a {rollback_type} operation "
                f"{'on app ' + app_name if app_name else 'on all apps'}. "
                "This will delete data and cannot be undone."
            )
            self.stdout.write(self.style.WARNING(confirmation_message))
            confirm = input("Are you sure you want to continue? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.SUCCESS("Operation cancelled."))
                return
        
        try:
            if rollback_type == 'flush':
                self._perform_flush()
            elif rollback_type == 'reset_db':
                self._perform_reset_db(app_name)
                
            self.stdout.write(self.style.SUCCESS(
                f"Successfully performed {rollback_type} operation "
                f"{'on app ' + app_name if app_name else 'on all apps'}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during operation: {str(e)}"))
            raise CommandError(f"Failed to perform {rollback_type} operation")

    def _perform_flush(self):
        """Clear all data while preserving database tables"""
        self.stdout.write("Flushing all data from database...")
        os.system("python manage.py flush --noinput")
        
        # Ensure migrations are up-to-date
        self.stdout.write("Checking migrations...")
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        
        self.stdout.write(self.style.SUCCESS("Database data cleared while preserving structure"))

    def _perform_reset_db(self, app_name):
        """Reset specific app's database tables"""
        self.stdout.write(f"Resetting database tables for app: {app_name}")
        
        # Use django-extensions reset_db command if available
        try:
            # First, we try with django-extensions reset_db command for the specific app
            self.stdout.write("Attempting to use django-extensions reset_db...")
            reset_result = os.system(f"python manage.py reset_db --database default --noinput")
            
            if reset_result != 0:
                self.stdout.write(self.style.WARNING(
                    "django-extensions reset_db failed or not available. "
                    "Falling back to manual migration reset."
                ))
                raise Exception("reset_db command failed")
                
        except Exception:
            # Fallback: manually remove and recreate migrations
            self.stdout.write("Using manual migration reset method...")
            
            # Remove migration files for the specific app
            migrations_path = os.path.join(settings.BASE_DIR, app_name, 'migrations')
            if os.path.exists(migrations_path):
                self.stdout.write(f"Removing migration files for {app_name}...")
                # Keep __init__.py file
                for file in os.listdir(migrations_path):
                    if file != '__init__.py' and file.endswith('.py'):
                        os.remove(os.path.join(migrations_path, file))
        
        # After resetting database or migrations, recreate app structure
        self.stdout.write(f"Creating new migrations for {app_name}...")
        os.system(f"python manage.py makemigrations {app_name}")
        
        self.stdout.write("Applying migrations...")
        os.system("python manage.py migrate")
        
        # Specific app migrations
        self.stdout.write(f"Ensuring {app_name} migrations are applied...")
        os.system(f"python manage.py migrate {app_name}")
        
        self.stdout.write(self.style.SUCCESS(f"Reset complete for app: {app_name}"))