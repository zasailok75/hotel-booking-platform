from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

# Room type choices
ROOM_TYPES = [
    ('SINGLE', 'Single'),
    ('DOUBLE', 'Double'),
    ('SUITE', 'Suite'),
]

class Hotel(models.Model):
    """Model representing a hotel"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
        ]

class Room(models.Model):
    """Model representing a room in a hotel"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    capacity = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.get_room_type_display()})"
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        indexes = [
            models.Index(fields=['room_type']),
            models.Index(fields=['is_available']),
        ]

class Booking(models.Model):
    """Model representing a room booking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.guest_name} - {self.room} ({self.check_in_date} to {self.check_out_date})"
    
    def clean(self):
        # Ensure check-out date is after check-in date
        if self.check_in_date and self.check_out_date:
            if self.check_out_date < self.check_in_date:
                raise ValidationError("Check-out date must be after check-in date")
        
        # Check for double booking
        if not self.is_cancelled and self.id is None:  # Only check on new bookings
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                is_cancelled=False,
                check_in_date__lt=self.check_out_date,
                check_out_date__gt=self.check_in_date
            )
            
            if overlapping_bookings.exists():
                raise ValidationError("This room is already booked for the selected dates")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['is_cancelled']),
        ]
