from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomViewSet, BookingViewSet, HomePageView, HotelRoomsView

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('hotel/<uuid:hotel_id>/rooms/', HotelRoomsView.as_view(), name='hotel_rooms'),
    path('api/', include(router.urls)),
]