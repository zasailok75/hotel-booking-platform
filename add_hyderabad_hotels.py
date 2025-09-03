from booking.models import Hotel, Room, ROOM_TYPES
import random
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_booking.settings')
django.setup()

# Create 5 hotels in Hyderabad
hotel_names = [
    'Grand Hyderabad Hotel',
    'Royal Hyderabad Resort',
    'Luxury Hyderabad Suites',
    'Elite Hyderabad Inn',
    'Premium Hyderabad Palace'
]

for name in hotel_names:
    # Create hotel
    hotel = Hotel.objects.create(
        name=name,
        city='Hyderabad',
        address=f'{random.randint(100, 9999)} Main St, Hyderabad',
        description=f'A beautiful hotel in Hyderabad'
    )
    
    # Create 3 rooms for each hotel
    for i in range(3):
        room_type = random.choice([t[0] for t in ROOM_TYPES])
        price = random.randint(50, 500)
        Room.objects.create(
            hotel=hotel,
            room_number=i+1,
            room_type=room_type,
            price=price
        )
    
    print(f'Created {name} with 3 rooms')

print('\nAll Hyderabad hotels created successfully!')