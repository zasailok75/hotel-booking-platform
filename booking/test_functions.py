"""
Functions to support the test cases for the hotel booking platform.
These functions provide the interface expected by the test cases.
"""

from datetime import date
from django.db import transaction
from .models import Hotel, Room, Booking


def book_room(room, check_in_date, check_out_date, guest_name="Test Guest", guest_email="test@example.com"):
    """
    Book a room for the specified date range.
    
    Args:
        room: Room object to book
        check_in_date: Check-in date (string in YYYY-MM-DD format or date object)
        check_out_date: Check-out date (string in YYYY-MM-DD format or date object)
        guest_name: Name of the guest (optional, defaults to "Test Guest")
        guest_email: Email of the guest (optional, defaults to "test@example.com")
    
    Returns:
        Booking object if successful, None if booking fails
    """
    # Convert string dates to date objects if needed
    if isinstance(check_in_date, str):
        check_in_date = date.fromisoformat(check_in_date)
    if isinstance(check_out_date, str):
        check_out_date = date.fromisoformat(check_out_date)
    
    # Validate dates
    if check_out_date <= check_in_date:
        return None
    
    try:
        with transaction.atomic():
            # Use select_for_update to prevent race conditions
            room = Room.objects.select_for_update().get(id=room.id)
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=room,
                is_cancelled=False,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            if overlapping_bookings.exists():
                return None
            
            # Create the booking
            booking = Booking.objects.create(
                room=room,
                guest_name=guest_name,
                guest_email=guest_email,
                check_in_date=check_in_date,
                check_out_date=check_out_date
            )
            
            return booking
            
    except Exception:
        # Return None if any error occurs
        return None


def search_hotels(hotels, city=None, name=None):
    """
    Search for hotels by city and/or name.
    
    Args:
        hotels: List of Hotel objects to search through
        city: City name to filter by (optional)
        name: Hotel name to filter by (optional)
    
    Returns:
        List of Hotel objects matching the criteria
    """
    results = []
    
    for hotel in hotels:
        match = True
        
        # Filter by city if provided
        if city and city.lower() not in hotel.city.lower():
            match = False
        
        # Filter by name if provided
        if name and name.lower() not in hotel.name.lower():
            match = False
        
        if match:
            results.append(hotel)
    
    return results


# Alternative implementation using Django ORM for better performance
def search_hotels_orm(city=None, name=None):
    """
    Search for hotels using Django ORM (more efficient for large datasets).
    
    Args:
        city: City name to filter by (optional)
        name: Hotel name to filter by (optional)
    
    Returns:
        QuerySet of Hotel objects matching the criteria
    """
    queryset = Hotel.objects.all()
    
    if city:
        queryset = queryset.filter(city__icontains=city)
    
    if name:
        queryset = queryset.filter(name__icontains=name)
    
    return queryset
