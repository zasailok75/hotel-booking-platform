"""
Django management command to debug room issues.
Usage: python manage.py debug_rooms
"""

from django.core.management.base import BaseCommand
from booking.models import Hotel, Room


class Command(BaseCommand):
    help = 'Debug room and hotel data'

    def handle(self, *args, **options):
        self.stdout.write("=== Database Debug Info ===")
        self.stdout.write(f"Total Hotels: {Hotel.objects.count()}")
        self.stdout.write(f"Total Rooms: {Room.objects.count()}")

        self.stdout.write("\n=== Hotels in Hyderabad ===")
        hyderabad_hotels = Hotel.objects.filter(city__icontains='hyderabad')
        self.stdout.write(f"Count: {hyderabad_hotels.count()}")
        for hotel in hyderabad_hotels:
            self.stdout.write(f"- {hotel.name} (ID: {hotel.id})")
            rooms_count = Room.objects.filter(hotel=hotel).count()
            self.stdout.write(f"  Rooms: {rooms_count}")

        self.stdout.write("\n=== All Hotels ===")
        for hotel in Hotel.objects.all()[:5]:  # Show first 5
            rooms_count = Room.objects.filter(hotel=hotel).count()
            self.stdout.write(f"- {hotel.name} in {hotel.city} (ID: {hotel.id}) - Rooms: {rooms_count}")

        self.stdout.write("\n=== All Rooms ===")
        for room in Room.objects.all()[:5]:  # Show first 5
            self.stdout.write(f"- {room.room_number} in {room.hotel.name} (Hotel ID: {room.hotel.id})")
