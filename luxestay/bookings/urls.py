from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:hotel_id>/', views.booking_view, name='book_hotel'),
    path('confirmation/<str:booking_ref>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('cancel/<str:booking_ref>/', views.cancel_booking_view, name='cancel_booking'),
    path('payment/<str:booking_ref>/', views.payment_view, name='payment'),
]
