from django.core.cache import cache
from django.conf import settings
import hashlib
import json

# Cache timeout in seconds (15 minutes)
CACHE_TIMEOUT = getattr(settings, 'HOTEL_SEARCH_CACHE_TIMEOUT', 60 * 15)

def get_cache_key(prefix, **kwargs):
    """
    Generate a cache key based on the search parameters.
    This creates a deterministic hash from the search parameters.
    """
    # Sort the kwargs to ensure consistent key generation
    sorted_kwargs = sorted(kwargs.items())
    # Convert to JSON string for hashing
    kwargs_str = json.dumps(sorted_kwargs)
    # Create an MD5 hash of the parameters
    hash_obj = hashlib.md5(kwargs_str.encode())
    # Return a cache key with prefix
    return f"{prefix}:{hash_obj.hexdigest()}"

def cache_search_results(func):
    """
    Decorator to cache search results.
    """
    def wrapper(*args, **kwargs):
        # Generate a cache key based on the function name and arguments
        cache_key = get_cache_key(func.__name__, **kwargs)
        
        # Try to get results from cache
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            return cached_results
        
        # If not in cache, call the original function
        results = func(*args, **kwargs)
        
        # Store results in cache
        cache.set(cache_key, results, CACHE_TIMEOUT)
        
        return results
    return wrapper

def invalidate_hotel_cache(hotel_id=None):
    """
    Invalidate cache for a specific hotel or all hotels.
    Call this when hotels or rooms are updated.
    """
    if hotel_id:
        # Create a pattern that matches all keys related to this hotel
        cache_pattern = f"*:{hotel_id}:*"
        keys = cache.keys(cache_pattern)
        for key in keys:
            cache.delete(key)
    else:
        # Clear all hotel-related cache
        cache_pattern = "search_hotels_*"
        keys = cache.keys(cache_pattern)
        for key in keys:
            cache.delete(key)