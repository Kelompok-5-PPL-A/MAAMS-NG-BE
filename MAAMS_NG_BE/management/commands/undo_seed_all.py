from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Undoes all seeded data in the correct order'

    def handle(self, *args, **options):
        try:
            # Undo in reverse order to maintain referential integrity
            self.stdout.write('Undoing causes...')
            call_command('undo_seed_causes')
            
            self.stdout.write('Undoing questions...')
            call_command('undo_seed_questions')
            
            self.stdout.write('Undoing tags...')
            call_command('undo_seed_tags')
            
            self.stdout.write(self.style.SUCCESS('Successfully undone all seeded data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error undoing seeded data: {str(e)}'))
            raise 