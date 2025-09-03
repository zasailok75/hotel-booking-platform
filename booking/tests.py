from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import uuid

from .models import Hotel, Room, Booking
from .search import search_hotels_optimized

class HotelModelTests(TestCase):
    def test_hotel_creation(self):
        hotel = Hotel.objects.create(
            name="Test Hotel",
            city="Test City",
            address="123 Test Street",
            description="A test hotel"
        )
        self.assertEqual(hotel.name, "Test Hotel")
        self.assertEqual(hotel.city, "Test City")

class RoomModelTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            city="Test City",
            address="123 Test Street"
        )
    
    def test_room_creation(self):
        room = Room.objects.create(
            hotel=self.hotel,
            room_number="101",
            room_type="SINGLE",
            price=100.00,
            capacity=1
        )
        self.assertEqual(room.room_number, "101")
        self.assertEqual(room.room_type, "SINGLE")
        self.assertEqual(room.hotel, self.hotel)

class BookingTests(TransactionTestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            city="Test City",
            address="123 Test Street"
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_number="101",
            room_type="SINGLE",
            price=100.00,
            capacity=1
        )
        
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.day_after_tomorrow = self.today + timedelta(days=2)
    
    def test_successful_booking(self):
        booking = Booking.objects.create(
            room=self.room,
            guest_name="Test Guest",
            guest_email="test@example.com",
            check_in_date=self.today,
            check_out_date=self.tomorrow
        )
        self.assertEqual(booking.guest_name, "Test Guest")
        self.assertEqual(booking.room, self.room)
    
    def test_double_booking_prevention(self):
        # Create first booking
        Booking.objects.create(
            room=self.room,
            guest_name="First Guest",
            guest_email="first@example.com",
            check_in_date=self.today,
            check_out_date=self.tomorrow
        )
        
        # Try to create overlapping booking
        with self.assertRaises(Exception):
            Booking.objects.create(
                room=self.room,
                guest_name="Second Guest",
                guest_email="second@example.com",
                check_in_date=self.today,
                check_out_date=self.tomorrow
            )
    
    def test_booking_edge_case(self):
        # Book for today to tomorrow
        Booking.objects.create(
            room=self.room,
            guest_name="First Guest",
            guest_email="first@example.com",
            check_in_date=self.today,
            check_out_date=self.tomorrow
        )
        
        # Book for tomorrow to day after (should succeed as it's not overlapping)
        booking2 = Booking.objects.create(
            room=self.room,
            guest_name="Second Guest",
            guest_email="second@example.com",
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow
        )
        
        self.assertEqual(booking2.guest_name, "Second Guest")

class SimultaneousBookingTests(TransactionTestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            city="Test City",
            address="123 Test Street"
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_number="101",
            room_type="SINGLE",
            price=100.00,
            capacity=1
        )
        
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        
        self.client = APIClient()
    
    def book_room(self):
        return self.client.post(
            reverse('booking-list'),
            {
                'room': str(self.room.id),
                'guest_name': 'Test Guest',
                'guest_email': 'test@example.com',
                'check_in_date': self.today,
                'check_out_date': self.tomorrow
            },
            format='json'
        )
    
    def test_simultaneous_booking(self):
        # Use ThreadPoolExecutor to simulate concurrent requests
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit two booking requests for the same room and date range
            future1 = executor.submit(self.book_room)
            future2 = executor.submit(self.book_room)
            
            # Get the results
            response1 = future1.result()
            response2 = future2.result()
            
            # One should succeed (201 Created) and one should fail (400 Bad Request)
            self.assertTrue(
                (response1.status_code == status.HTTP_201_CREATED and response2.status_code == status.HTTP_400_BAD_REQUEST) or
                (response1.status_code == status.HTTP_400_BAD_REQUEST and response2.status_code == status.HTTP_201_CREATED)
            )

class SearchTests(TestCase):
    def setUp(self):
        # Create test hotels
        self.hotel1 = Hotel.objects.create(
            name="Oceanview Resort",
            city="Miami",
            address="123 Beach Blvd"
        )
        
        self.hotel2 = Hotel.objects.create(
            name="Mountain Inn",
            city="Denver",
            address="456 Mountain Rd"
        )
        
        self.hotel3 = Hotel.objects.create(
            name="City Center Hotel",
            city="New York",
            address="789 Broadway"
        )
    
    def test_search_by_city(self):
        results = search_hotels_optimized(city="Miami")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Oceanview Resort")
    
    def test_search_by_name(self):
        results = search_hotels_optimized(name="Mountain")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].city, "Denver")
    
    def test_search_no_results(self):
        results = search_hotels_optimized(city="Chicago")
        self.assertEqual(len(results), 0)
    
    def test_search_multiple_results(self):
        # Create another hotel in Miami
        Hotel.objects.create(
            name="Beachside Hotel",
            city="Miami",
            address="321 Ocean Drive"
        )
        
        results = search_hotels_optimized(city="Miami")
        self.assertEqual(len(results), 2)
