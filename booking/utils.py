import random
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Hotel, Room, Booking, ROOM_TYPES

def generate_mock_data(num_hotels=1000000, rooms_per_hotel=3):
    """
    Generate mock data for testing the hotel booking system with large datasets.
    
    Args:
        num_hotels (int): Number of hotels to generate
        rooms_per_hotel (int): Number of rooms per hotel
    """
    # List of cities for random generation
    cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "San Francisco", "Charlotte", "Indianapolis",
        "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
        "Detroit", "Portland", "Memphis", "Oklahoma City", "Las Vegas", "Louisville",
        "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
        "Mesa", "Kansas City", "Atlanta", "Long Beach", "Colorado Springs", "Raleigh",
        "Miami", "Omaha", "Minneapolis", "Tulsa", "Cleveland", "Wichita", "Arlington",
        "New Orleans", "Bakersfield", "Tampa", "Honolulu", "Aurora", "Anaheim",
        "Santa Ana", "St. Louis", "Riverside", "Corpus Christi", "Lexington",
        "Pittsburgh", "Anchorage", "Stockton", "Cincinnati", "St. Paul", "Toledo",
        "Greensboro", "Newark", "Plano", "Henderson", "Lincoln", "Buffalo", "Jersey City",
        "Chula Vista", "Fort Wayne", "Orlando", "St. Petersburg", "Chandler", "Laredo",
        "Norfolk", "Durham", "Madison", "Lubbock", "Irvine", "Winston-Salem", "Glendale",
        "Garland", "Hialeah", "Reno", "Chesapeake", "Gilbert", "Baton Rouge", "Irving",
        "Scottsdale", "North Las Vegas", "Fremont", "Boise City", "Richmond", "San Bernardino"
    ]
    
    # List of hotel name prefixes and suffixes for random generation
    hotel_prefixes = [
        "Grand", "Royal", "Imperial", "Luxury", "Elite", "Premium", "Comfort", "Cozy",
        "Pleasant", "Tranquil", "Serene", "Majestic", "Regal", "Elegant", "Exquisite",
        "Splendid", "Deluxe", "Superior", "Prime", "Select", "Choice", "Quality",
        "Prestige", "Exclusive", "Distinguished", "Eminent", "Prominent", "Renowned",
        "Famous", "Celebrated", "Esteemed", "Respected", "Admired", "Valued", "Treasured"
    ]
    
    hotel_suffixes = [
        "Hotel", "Inn", "Suites", "Lodge", "Resort", "Retreat", "Hideaway", "Haven",
        "Sanctuary", "Oasis", "Paradise", "Palace", "Mansion", "Castle", "Tower",
        "Plaza", "Court", "Pavilion", "Residency", "Quarters", "Accommodations",
        "Lodging", "Dwelling", "Abode", "Habitat", "Domicile", "Establishment",
        "Complex", "Compound", "Enclave", "Estate", "Manor", "Villa", "Chateau", "Cottage"
    ]
    
    print(f"Generating {num_hotels} hotels with {rooms_per_hotel} rooms each...")
    
    # Batch creation for better performance
    batch_size = 1000
    hotels_created = 0
    
    while hotels_created < num_hotels:
        # Determine batch size for this iteration
        current_batch_size = min(batch_size, num_hotels - hotels_created)
        
        # Create hotels in batch
        hotels_batch = []
        for _ in range(current_batch_size):
            prefix = random.choice(hotel_prefixes)
            suffix = random.choice(hotel_suffixes)
            city = random.choice(cities)
            hotel = Hotel(
                name=f"{prefix} {city} {suffix}",
                city=city,
                address=f"{random.randint(100, 9999)} Main St, {city}",
                description=f"A {prefix.lower()} hotel in {city}"
            )
            hotels_batch.append(hotel)
        
        # Bulk create hotels
        created_hotels = Hotel.objects.bulk_create(hotels_batch)
        
        # Create rooms for each hotel in batch
        rooms_batch = []
        for hotel in created_hotels:
            for i in range(rooms_per_hotel):
                room_type = random.choice([t[0] for t in ROOM_TYPES])
                price = random.randint(50, 500)
                rooms_batch.append(Room(
                    hotel=hotel,
                    room_number=f"{random.randint(1, 9)}{random.randint(0, 9)}{random.randint(0, 9)}",
                    room_type=room_type,
                    price=price,
                    is_available=random.choice([True, True, True, False]),  # 75% available
                    capacity=random.randint(1, 4)
                ))
        
        # Bulk create rooms
        Room.objects.bulk_create(rooms_batch)
        
        hotels_created += current_batch_size
        print(f"Created {hotels_created}/{num_hotels} hotels")
    
    print("Mock data generation complete!")

def generate_test_bookings(num_bookings=100):
    """
    Generate test bookings for existing rooms.
    
    Args:
        num_bookings (int): Number of bookings to generate
    """
    # Get random rooms
    rooms = list(Room.objects.all().order_by('?')[:num_bookings])
    
    if not rooms:
        print("No rooms available for booking generation")
        return
    
    bookings = []
    today = timezone.now().date()
    
    for i in range(num_bookings):
        # Generate random dates within the next 90 days
        start_offset = random.randint(1, 60)
        duration = random.randint(1, 10)
        
        check_in_date = today + timedelta(days=start_offset)
        check_out_date = check_in_date + timedelta(days=duration)
        
        booking = Booking(
            room=rooms[i % len(rooms)],
            guest_name=f"Guest {i+1}",
            guest_email=f"guest{i+1}@example.com",
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            is_cancelled=random.random() < 0.1  # 10% chance of cancellation
        )
        bookings.append(booking)
    
    Booking.objects.bulk_create(bookings)
    print(f"Created {len(bookings)} test bookings")