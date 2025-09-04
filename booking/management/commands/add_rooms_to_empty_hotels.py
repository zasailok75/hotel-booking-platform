"""
Django management command to add rooms to hotels that don't have any.
Usage: python manage.py add_rooms_to_empty_hotels
"""

from django.core.management.base import BaseCommand
from booking.models import Hotel, Room
import random


class Command(BaseCommand):
    help = 'Add rooms to hotels that don\'t have any rooms'

    def handle(self, *args, **options):
        # Find hotels with no rooms
        hotels_without_rooms = []
        for hotel in Hotel.objects.all():
            room_count = Room.objects.filter(hotel=hotel).count()
            if room_count == 0:
                hotels_without_rooms.append(hotel)
        
        self.stdout.write(f"Found {len(hotels_without_rooms)} hotels without rooms")
        
        # Add 2-4 rooms to each hotel without rooms
        for hotel in hotels_without_rooms:
            num_rooms = random.randint(2, 4)
            room_types = ['SINGLE', 'DOUBLE', 'SUITE']
            
            for i in range(num_rooms):
                room_number = str(random.randint(100, 999))
                room_type = random.choice(room_types)
                price = random.randint(1000, 5000)
                
                # Make sure room number is unique for this hotel
                while Room.objects.filter(hotel=hotel, room_number=room_number).exists():
                    room_number = str(random.randint(100, 999))
                
                room = Room.objects.create(
                    hotel=hotel,
                    room_number=room_number,
                    room_type=room_type,
                    price=price,
                    capacity=1 if room_type == 'SINGLE' else 2 if room_type == 'DOUBLE' else 4
                )
                
                self.stdout.write(f"Added room {room_number} ({room_type}) to {hotel.name}")
        
        self.stdout.write(f"Successfully added rooms to {len(hotels_without_rooms)} hotels")
