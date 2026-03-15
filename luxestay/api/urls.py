from django.urls import path
from . import views

urlpatterns = [
    # Health
    path('health/', views.api_health, name='api_health'),
    path('cities/', views.cities_list, name='api_cities'),

    # Auth
    path('auth/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('auth/profile/', views.ProfileAPIView.as_view(), name='api_profile'),

    # Hotels
    path('hotels/', views.HotelListAPIView.as_view(), name='api_hotel_list'),
    path('hotels/featured/', views.FeaturedHotelsAPIView.as_view(), name='api_featured'),
    path('hotels/deals/', views.DealsAPIView.as_view(), name='api_deals'),
    path('hotels/<int:hotel_id>/', views.HotelDetailAPIView.as_view(), name='api_hotel_detail'),
    path('hotels/<int:hotel_id>/availability/', views.HotelAvailabilityAPIView.as_view(), name='api_availability'),

    # Bookings
    path('bookings/', views.BookingListCreateAPIView.as_view(), name='api_bookings'),
    path('bookings/<str:booking_ref>/', views.BookingDetailAPIView.as_view(), name='api_booking_detail'),
]
