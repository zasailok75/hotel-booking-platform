from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BookingUserRateThrottle(UserRateThrottle):
    """
    Rate limiting for authenticated users making booking requests.
    Limits users to 30 booking requests per hour to prevent abuse.
    """
    rate = '30/hour'
    scope = 'booking_user'

class BookingAnonRateThrottle(AnonRateThrottle):
    """
    Rate limiting for anonymous users making booking requests.
    Limits anonymous users to 10 booking requests per hour to prevent abuse.
    """
    rate = '10/hour'
    scope = 'booking_anon'

class SearchUserRateThrottle(UserRateThrottle):
    """
    Rate limiting for authenticated users making search requests.
    Limits users to 100 search requests per hour.
    """
    rate = '100/hour'
    scope = 'search_user'

class SearchAnonRateThrottle(AnonRateThrottle):
    """
    Rate limiting for anonymous users making search requests.
    Limits anonymous users to 50 search requests per hour.
    """
    rate = '50/hour'
    scope = 'search_anon'