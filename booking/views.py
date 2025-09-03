from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Hotel, Room, Booking
from .serializers import HotelSerializer, RoomSerializer, BookingSerializer
from .throttling import (BookingUserRateThrottle, BookingAnonRateThrottle,
                        SearchUserRateThrottle, SearchAnonRateThrottle)


class HomePageView(TemplateView):
    template_name = 'booking/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_hotels'] = Hotel.objects.all()[:3]
        return context

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city']
    throttle_classes = [SearchUserRateThrottle, SearchAnonRateThrottle]
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        hotel = self.get_object()
        rooms = Room.objects.filter(hotel=hotel)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['room_type', 'hotel__name', 'hotel__city']
    throttle_classes = [SearchUserRateThrottle, SearchAnonRateThrottle]
    
    def get_queryset(self):
        queryset = Room.objects.all()
        hotel_id = self.request.query_params.get('hotel_id', None)
        room_type = self.request.query_params.get('room_type', None)
        is_available = self.request.query_params.get('is_available', None)
        
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        if is_available:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
            
        return queryset

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    throttle_classes = [BookingUserRateThrottle, BookingAnonRateThrottle]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get room and check if it's available
        room_id = serializer.validated_data.get('room').id
        check_in_date = serializer.validated_data.get('check_in_date')
        check_out_date = serializer.validated_data.get('check_out_date')
        
        # Use select_for_update to lock the room record during the transaction
        try:
            room = Room.objects.select_for_update().get(id=room_id)
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=room,
                is_cancelled=False,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            if overlapping_bookings.exists():
                return Response(
                    {"error": "This room is already booked for the selected dates"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the booking
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.is_cancelled = True
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
