from django.core.management.base import BaseCommand

class BaseSeeder(BaseCommand):
    """
    Base class for all seeders.
    """
    help = 'Base class for all seeders'

    def handle(self, *args, **options):
        try:
            self.seed()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
            raise

    def seed(self):
        """
        Override this method in your seeder class.
        """
        raise NotImplementedError("Subclasses must implement seed()")

    def undo_seed(self):
        """
        Override this method in your seeder class to implement unseeding
        """
        raise NotImplementedError("Subclasses must implement undo_seed()") 