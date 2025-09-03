from django.core.management.base import BaseCommand
from booking.utils import generate_mock_data, generate_test_bookings

class Command(BaseCommand):
    help = 'Generate mock data for performance testing'

    def add_arguments(self, parser):
        parser.add_argument('--hotels', type=int, default=1000, help='Number of hotels to generate')
        parser.add_argument('--rooms-per-hotel', type=int, default=3, help='Number of rooms per hotel')
        parser.add_argument('--bookings', type=int, default=100, help='Number of test bookings to generate')

    def handle(self, *args, **options):
        num_hotels = options['hotels']
        rooms_per_hotel = options['rooms_per_hotel']
        num_bookings = options['bookings']
        
        self.stdout.write(self.style.SUCCESS(f'Starting mock data generation: {num_hotels} hotels with {rooms_per_hotel} rooms each'))
        
        generate_mock_data(num_hotels, rooms_per_hotel)
        
        if num_bookings > 0:
            self.stdout.write(self.style.SUCCESS(f'Generating {num_bookings} test bookings'))
            generate_test_bookings(num_bookings)
        
        self.stdout.write(self.style.SUCCESS('Mock data generation completed successfully!'))