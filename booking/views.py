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
    
    def get_queryset(self):
        from .search import search_hotels_optimized
        
        # Get query parameters
        city = self.request.query_params.get('city', None)
        name = self.request.query_params.get('name', None)
        unfilled_only = self.request.query_params.get('unfilled_only', 'false').lower() == 'true'
        check_in_date = self.request.query_params.get('check_in_date', None)
        check_out_date = self.request.query_params.get('check_out_date', None)
        
        # If unfilled_only is requested, use the optimized search function
        if unfilled_only and check_in_date and check_out_date:
            return search_hotels_optimized(
                city=city,
                name=name,
                unfilled_only=True,
                check_in_date=check_in_date,
                check_out_date=check_out_date
            )
        
        # Otherwise, use the default queryset
        queryset = Hotel.objects.all()
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset
    
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
    
    def get_queryset(self):
        queryset = Booking.objects.all()
        room_id = self.request.query_params.get('room', None)
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
            
        return queryset
    
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
