from django.core.management.base import BaseCommand
from tag.models import Tag

class Command(BaseCommand):
    help = 'Undoes tag seeding'

    def handle(self, *args, **options):
        try:
            Tag.objects.filter(name__in=[
                'economy',
                'climate',
                'social',
                'tech',
                'health',
                'edu',
                'politics',
                'culture'
            ]).delete()
            self.stdout.write(self.style.SUCCESS('Successfully removed seeded tags'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error removing seeded tags: {str(e)}'))
            raise 