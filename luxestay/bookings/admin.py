from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_ref', 'user', 'hotel_name', 'check_in', 'check_out', 'status', 'payment_status', 'total_price']
    list_filter = ['status', 'payment_status', 'check_in']
    search_fields = ['booking_ref', 'hotel_name', 'user__email']
    readonly_fields = ['booking_ref', 'created_at', 'updated_at']
    ordering = ['-created_at']
