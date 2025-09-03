# Hotel Room Booking Platform

A Django-based hotel room booking platform that allows users to create hotels and rooms, book rooms for specific date ranges, and search for hotels based on various criteria. The system is designed to handle large datasets efficiently and prevent double bookings.

## Core Features

1. **Hotel and Room Management**
   - Models for Hotel and Room with relationships
   - Room types (Single, Double, Suite) with availability status and pricing

2. **Booking System**
   - Book rooms for specific date ranges
   - Double booking prevention using transactions and locks
   - Validation for check-in/check-out dates

3. **Search Functionality**
   - Search hotels by city and name
   - Optimized for large datasets (1M+ hotel records)
   - Pagination support

4. **Performance Optimizations**
   - Database indexing for faster queries
   - Efficient search algorithms
   - Transaction-based booking to prevent race conditions

## Setup Instructions

### Prerequisites

- Python 3.8+
- Django 5.2+
- Django REST Framework 3.16+

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hotel-booking.git
   cd hotel-booking
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Generate mock data (optional):
   ```
   python manage.py generate_mock_data --hotels 100 --rooms 10 --bookings 50
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## API Endpoints

- **Hotels**
  - `GET /api/hotels/` - List all hotels
  - `GET /api/hotels/?city=CityName` - Search hotels by city
  - `GET /api/hotels/?name=HotelName` - Search hotels by name
  - `POST /api/hotels/` - Create a new hotel
  - `GET /api/hotels/{id}/` - Get hotel details

- **Rooms**
  - `GET /api/rooms/` - List all rooms
  - `GET /api/rooms/?hotel={hotel_id}` - Get rooms for a specific hotel
  - `POST /api/rooms/` - Create a new room
  - `GET /api/rooms/{id}/` - Get room details

- **Bookings**
  - `GET /api/bookings/` - List all bookings
  - `POST /api/bookings/` - Create a new booking
  - `GET /api/bookings/{id}/` - Get booking details

## Test Cases

The system includes comprehensive test cases to ensure functionality and prevent double bookings:

1. **Simultaneous Booking Test**
   - Tests that the system prevents double bookings when multiple requests are processed simultaneously

2. **Booking Edge Case Test**
   - Tests booking a room with adjacent check-in/check-out dates

3. **Search Test**
   - Tests the hotel search functionality with various criteria

Run tests with:
```
python manage.py test booking
```

## Project Structure

```
hotel_booking/
├── booking/                  # Main app
│   ├── models.py             # Hotel, Room, Booking models
│   ├── serializers.py        # API serializers
│   ├── views.py              # API views and viewsets
│   ├── urls.py               # API URL routing
│   ├── search.py             # Search functionality
│   ├── utils.py              # Utility functions
│   ├── tests.py              # Test cases
│   └── management/           # Management commands
│       └── commands/         # Custom commands
│           └── generate_mock_data.py  # Mock data generator
├── hotel_booking/           # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
└── README.md                # Project documentation
```

## Performance Considerations

- The system is designed to handle 1M+ hotel records efficiently
- Database indexes are used to optimize search queries
- Transactions and select_for_update are used to prevent race conditions during booking
- Pagination is implemented for large result sets

## Future Enhancements

- Caching layer for search results
- Rate limiting for booking requests
- User authentication and authorization
- Frontend UI/Dashboard