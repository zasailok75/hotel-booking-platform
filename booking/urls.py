from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomViewSet, BookingViewSet, HomePageView

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('hotels/<uuid:hotel_id>/rooms/', HomePageView.as_view(template_name='booking/room_details.html'), name='room_details'),
    path('api/', include(router.urls)),
]