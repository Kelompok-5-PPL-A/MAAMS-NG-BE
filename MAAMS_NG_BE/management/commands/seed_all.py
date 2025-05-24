from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Seeds all data in the correct order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--undo',
            action='store_true',
            help='Undo all seeded data'
        )

    def handle(self, *args, **options):
        try:
            if options['undo']:
                self.stdout.write('Undoing all seeded data...')
                # Undo in reverse order to maintain referential integrity
                call_command('undo_seed_causes')
                call_command('undo_seed_questions')
                call_command('undo_seed_tags')
                self.stdout.write(self.style.SUCCESS('Successfully unseeded all data'))
            else:
                # Seed in the correct order to maintain referential integrity
                self.stdout.write('Seeding tags...')
                call_command('seed_tags')
                
                self.stdout.write('Seeding questions...')
                call_command('seed_questions')
                
                self.stdout.write('Seeding causes...')
                call_command('seed_causes')
                
                self.stdout.write(self.style.SUCCESS('Successfully seeded all data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise 