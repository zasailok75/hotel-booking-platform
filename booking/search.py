from django.db.models import Q
from .models import Hotel, Room
from .cache import cache_search_results

class HotelSearch:
    """
    A class to handle hotel search functionality optimized for large datasets.
    This implementation uses Django's ORM with optimized queries and indexing.
    """
    
    @staticmethod
    def search_hotels(filters=None, limit=None, offset=0):
        """
        Search for hotels based on filters.
        
        Args:
            filters (dict): Dictionary containing filter criteria
            limit (int): Maximum number of results to return
            offset (int): Offset for pagination
            
        Returns:
            QuerySet: Filtered hotel queryset
        """
        queryset = Hotel.objects.all()
        
        if not filters:
            filters = {}
        
        # Apply filters
        if 'city' in filters and filters['city']:
            queryset = queryset.filter(city__icontains=filters['city'])
        
        if 'name' in filters and filters['name']:
            queryset = queryset.filter(name__icontains=filters['name'])
        
        # Apply pagination
        if limit is not None:
            queryset = queryset[offset:offset+limit]
        
        return queryset
    
    @staticmethod
    def search_available_rooms(hotel_id=None, check_in_date=None, check_out_date=None, room_type=None):
        """
        Search for available rooms based on criteria.
        
        Args:
            hotel_id (UUID): Hotel ID to filter rooms
            check_in_date (date): Check-in date
            check_out_date (date): Check-out date
            room_type (str): Type of room
            
        Returns:
            QuerySet: Filtered room queryset
        """
        queryset = Room.objects.all()
        
        # Filter by hotel if provided
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        
        # Filter by room type if provided
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        # Filter for available rooms during the specified date range
        if check_in_date and check_out_date:
            # Exclude rooms with overlapping bookings
            queryset = queryset.exclude(
                bookings__is_cancelled=False,
                bookings__check_in_date__lt=check_out_date,
                bookings__check_out_date__gt=check_in_date
            )
        
        return queryset

# Optimized search function for large datasets
@cache_search_results
def search_hotels_optimized(city=None, name=None, limit=100, offset=0):
    """
    Optimized search function for large datasets.
    Uses indexed fields and query optimization.
    Results are cached for improved performance.
    
    Args:
        city (str): City name to filter by
        name (str): Hotel name to filter by
        limit (int): Maximum number of results
        offset (int): Offset for pagination
        
    Returns:
        list: List of matching hotels
    """
    query = Hotel.objects.all()
    
    # Build query filters
    filters = Q()
    
    if city:
        filters &= Q(city__icontains=city)
    
    if name:
        filters &= Q(name__icontains=name)
    
    # Apply filters if any exist
    if filters:
        query = query.filter(filters)
    
    # Use only() to select specific fields for better performance
    query = query.only('id', 'name', 'city')
    
    # Apply pagination
    query = query[offset:offset+limit]
    
    return query