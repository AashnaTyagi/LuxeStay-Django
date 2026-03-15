from django.contrib import admin
from .models import Hotel, Room, Review, Amenity


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'stars', 'rating', 'is_featured', 'is_deal']
    list_filter = ['stars', 'is_featured', 'is_deal', 'property_type']
    search_fields = ['name', 'location', 'city']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_type', 'price', 'is_available', 'capacity']
    list_filter = ['room_type', 'is_available']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'rating', 'created_at']
    list_filter = ['rating']
