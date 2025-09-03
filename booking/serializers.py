from rest_framework import serializers
from .models import Hotel, Room, Booking
from django.core.exceptions import ValidationError

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address', 'description']

class RoomSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'hotel', 'hotel_name', 'room_number', 'room_type', 'room_type_display', 'price', 'is_available', 'capacity']

class BookingSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'room', 'room_details', 'guest_name', 'guest_email', 'check_in_date', 'check_out_date', 'booking_date', 'is_cancelled']
        read_only_fields = ['booking_date']
    
    def validate(self, data):
        # Ensure check-out date is after check-in date
        if data.get('check_in_date') and data.get('check_out_date'):
            if data['check_out_date'] < data['check_in_date']:
                raise serializers.ValidationError("Check-out date must be after check-in date")
        
        # Check for double booking
        room = data.get('room')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        booking_id = self.instance.id if self.instance else None
        
        if room and check_in_date and check_out_date:
            overlapping_bookings = Booking.objects.filter(
                room=room,
                is_cancelled=False,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            # Exclude current booking when updating
            if booking_id:
                overlapping_bookings = overlapping_bookings.exclude(id=booking_id)
            
            if overlapping_bookings.exists():
                raise serializers.ValidationError("This room is already booked for the selected dates")
        
        return data