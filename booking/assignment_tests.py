"""
Test cases for Hotel Room Booking Platform Assignment 3 & 4
These are the exact test cases provided in the assignment.
"""

from django.test import TestCase
from datetime import date
from .models import Hotel, Room
from .test_functions import book_room, search_hotels


class AssignmentTestCases(TestCase):
    """Test cases for the hotel booking platform assignment"""
    
    def test_simultaneous_booking(self):
        """Test Case 1: Simultaneous Booking"""
        # Setup: Create a hotel and rooms
        hotel = Hotel(name="Oceanview", city="Goa", address="123 Beach Road")
        hotel.save()
        
        room1 = Room(
            hotel=hotel, 
            room_type="SINGLE", 
            price=1000, 
            room_number="101",
            available_from=date(2025, 8, 1), 
            available_to=date(2025, 8, 5)
        )
        room1.save()
        
        # Attempt simultaneous booking
        booking1 = book_room(room1, "2025-08-02", "2025-08-04")
        booking2 = book_room(room1, "2025-08-03", "2025-08-04")  # Overlapping dates
        
        assert booking1 is not None, "Booking 1 should succeed"
        assert booking2 is None, "Booking 2 should fail due to overlap"
        
        print("✅ Test Case 1: Simultaneous Booking - PASSED")
    
    def test_search_hotels(self):
        """Test Case 2: Search by City and Hotel Name"""
        # Create hotels
        hotel1 = Hotel(name="Oceanview", city="Goa", address="123 Beach Road")
        hotel1.save()
        
        hotel2 = Hotel(name="Mountain Inn", city="Shimla", address="456 Hill Road")
        hotel2.save()
        
        # Add hotels to the search list
        hotels = [hotel1, hotel2]
        
        # Search for hotels by city and hotel name
        result_by_city = search_hotels(hotels, city="Goa")
        result_by_name = search_hotels(hotels, name="Oceanview")
        
        assert len(result_by_city) == 1, "Search by city should return 1 result"
        assert len(result_by_name) == 1, "Search by name should return 1 result"
        
        print("✅ Test Case 2: Search by City and Hotel Name - PASSED")


def run_assignment_tests():
    """
    Function to run the assignment test cases manually.
    This can be called from Django shell or management command.
    """
    print("🚀 Running Hotel Room Booking Platform Assignment Tests")
    print("=" * 60)
    
    # Create test instance
    test_instance = AssignmentTestCases()
    
    try:
        # Run Test Case 1
        print("\n📋 Test Case 1: Simultaneous Booking")
        test_instance.test_simultaneous_booking()
        
        # Run Test Case 2  
        print("\n📋 Test Case 2: Search by City and Hotel Name")
        test_instance.test_search_hotels()
        
        print("\n" + "=" * 60)
        print("🎉 All test cases PASSED! Your code is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    # This allows running the tests directly
    run_assignment_tests()
