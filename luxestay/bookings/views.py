from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking
from .forms import BookingForm
from hotels.views import STATIC_HOTELS
from decimal import Decimal, InvalidOperation


@login_required
def booking_view(request, hotel_id):
    hotel = next((h for h in STATIC_HOTELS if h['id'] == hotel_id), None)
    if not hotel:
        messages.error(request, "Hotel not found.")
        return redirect('hotel_list')

    room_id = request.GET.get('room_id')
    room_type = request.GET.get('room_type', 'Standard')
    price = request.GET.get('price', hotel['price'])

    rooms = [
        {'id': hotel_id * 10 + 1, 'type': 'Standard', 'price': hotel['price'], 'capacity': 2, 'bed': 'King Bed', 'area': 280, 'available': True},
        {'id': hotel_id * 10 + 2, 'type': 'Deluxe',   'price': int(hotel['price'] * 1.4), 'capacity': 2, 'bed': 'King Bed', 'area': 380, 'available': True},
        {'id': hotel_id * 10 + 3, 'type': 'Suite',    'price': int(hotel['price'] * 2.2), 'capacity': 4, 'bed': '2x Queen Beds', 'area': 580, 'available': hotel['stars'] >= 4},
    ]
    selected_room = next((r for r in rooms if str(r['id']) == str(room_id)), rooms[0])

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel_id = hotel_id
            booking.hotel_name = hotel['name']
            booking.hotel_location = hotel['location']
            booking.hotel_image = hotel['image']
            booking.room_type = request.POST.get('room_type', 'Standard')

            # ── Fix: safely convert price to Decimal ──
            raw_price = request.POST.get('price_per_night', str(hotel['price']))
            try:
                booking.price_per_night = Decimal(str(raw_price).strip())
            except (InvalidOperation, ValueError):
                booking.price_per_night = Decimal(str(hotel['price']))

            booking.status = 'confirmed'
            booking.save()
            messages.success(request, f"🎉 Booking confirmed! Your reference: {booking.booking_ref}")
            return redirect('booking_confirmation', booking_ref=booking.booking_ref)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = BookingForm()

    return render(request, 'bookings/booking.html', {
        'hotel': hotel,
        'form': form,
        'rooms': rooms,
        'selected_room': selected_room,
    })


@login_required
def booking_confirmation_view(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    hotel = next((h for h in STATIC_HOTELS if h['id'] == booking.hotel_id), None)
    return render(request, 'bookings/confirmation.html', {
        'booking': booking,
        'hotel': hotel,
    })


@login_required
def cancel_booking_view(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.info(request, f"Booking {booking_ref} has been cancelled.")
        return redirect('dashboard')
    return render(request, 'bookings/cancel.html', {'booking': booking})


@login_required
def payment_view(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    hotel = next((h for h in STATIC_HOTELS if h['id'] == booking.hotel_id), None)

    if request.method == 'POST':
        card_number = request.POST.get('card_number', '')
        cvv = request.POST.get('cvv', '')
        if card_number and cvv:
            booking.payment_status = 'paid'
            booking.save()
            messages.success(request, "Payment successful! Enjoy your stay. ✨")
            return redirect('booking_confirmation', booking_ref=booking.booking_ref)
        else:
            messages.error(request, "Payment failed. Please check your card details.")

    return render(request, 'bookings/payment.html', {
        'booking': booking,
        'hotel': hotel,
    })