"""
Django management command to run the assignment test cases.
Usage: python manage.py run_assignment_tests
"""

from django.core.management.base import BaseCommand
from booking.assignment_tests import run_assignment_tests


class Command(BaseCommand):
    help = 'Run the Hotel Room Booking Platform Assignment test cases'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting assignment test cases...')
        )
        
        try:
            run_assignment_tests()
            self.stdout.write(
                self.style.SUCCESS('All tests completed successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Tests failed: {e}')
            )
            raise
