from django.db import models
from django.utils import timezone
import uuid


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    PAYMENT_STATUS = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )

    booking_ref = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookings')
    hotel_id = models.IntegerField()
    hotel_name = models.CharField(max_length=200)
    hotel_location = models.CharField(max_length=200, blank=True)
    hotel_image = models.CharField(max_length=200, blank=True)
    room = models.ForeignKey('hotels.Room', on_delete=models.SET_NULL, null=True, blank=True)
    room_type = models.CharField(max_length=50, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_ref} - {self.hotel_name}"

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = 'LX' + str(uuid.uuid4()).upper()[:8]
        if self.check_in and self.check_out and self.price_per_night:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.price_per_night * nights
        super().save(*args, **kwargs)

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def is_upcoming(self):
        return self.check_in >= timezone.now().date() and self.status == 'confirmed'
