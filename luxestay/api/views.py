from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q

from accounts.models import User
from bookings.models import Booking
from hotels.views import STATIC_HOTELS
from .serializers import (
    UserSerializer, RegisterSerializer, HotelSerializer,
    BookingSerializer, CreateBookingSerializer
)


# ─── Auth Endpoints ───────────────────────────────────────────────────────────

class RegisterAPIView(generics.CreateAPIView):
    """POST /api/auth/register/ — Create a new user account"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """POST /api/auth/login/ — Authenticate and get token"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password required.'}, status=400)
        user = authenticate(request, username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': f'Welcome back, {user.first_name or user.email}!'
            })
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    """POST /api/auth/logout/ — Invalidate token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully.'})


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/ — View or update profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── Hotel Endpoints ──────────────────────────────────────────────────────────

class HotelListAPIView(APIView):
    """GET /api/hotels/ — List and filter hotels"""
    permission_classes = [AllowAny]

    def get(self, request):
        hotels = list(STATIC_HOTELS)

        # Query params
        q = request.query_params.get('q', '')
        city = request.query_params.get('city', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        stars = request.query_params.getlist('stars')
        property_type = request.query_params.get('property_type', '')
        featured = request.query_params.get('featured')
        sort = request.query_params.get('sort', 'featured')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        if q:
            hotels = [h for h in hotels if q.lower() in h['name'].lower() or q.lower() in h['location'].lower()]
        if city:
            hotels = [h for h in hotels if city.lower() in h['city'].lower()]
        if min_price:
            hotels = [h for h in hotels if h['price'] >= int(min_price)]
        if max_price:
            hotels = [h for h in hotels if h['price'] <= int(max_price)]
        if stars:
            star_ints = [int(s) for s in stars]
            hotels = [h for h in hotels if h['stars'] in star_ints]
        if property_type:
            hotels = [h for h in hotels if h['property_type'] == property_type]
        if featured:
            hotels = [h for h in hotels if h.get('is_featured')]

        # Sort
        if sort == 'price_low':
            hotels.sort(key=lambda x: x['price'])
        elif sort == 'price_high':
            hotels.sort(key=lambda x: -x['price'])
        elif sort == 'rating':
            hotels.sort(key=lambda x: -x['rating'])

        total = len(hotels)
        start = (page - 1) * page_size
        paginated = hotels[start:start + page_size]

        return Response({
            'count': total,
            'page': page,
            'total_pages': (total + page_size - 1) // page_size,
            'results': HotelSerializer(paginated, many=True).data
        })


class HotelDetailAPIView(APIView):
    """GET /api/hotels/<id>/ — Hotel details"""
    permission_classes = [AllowAny]

    def get(self, request, hotel_id):
        hotel = next((h for h in STATIC_HOTELS if h['id'] == hotel_id), None)
        if not hotel:
            return Response({'error': 'Hotel not found.'}, status=404)

        rooms = [
            {'id': hotel_id * 10 + 1, 'type': 'Standard', 'price': hotel['price'], 'capacity': 2, 'available': True},
            {'id': hotel_id * 10 + 2, 'type': 'Deluxe', 'price': int(hotel['price'] * 1.4), 'capacity': 2, 'available': True},
            {'id': hotel_id * 10 + 3, 'type': 'Suite', 'price': int(hotel['price'] * 2.2), 'capacity': 4, 'available': hotel['stars'] >= 4},
        ]
        data = HotelSerializer(hotel).data
        data['rooms'] = rooms
        return Response(data)


class HotelAvailabilityAPIView(APIView):
    """GET /api/hotels/<id>/availability/ — Check availability"""
    permission_classes = [AllowAny]

    def get(self, request, hotel_id):
        hotel = next((h for h in STATIC_HOTELS if h['id'] == hotel_id), None)
        if not hotel:
            return Response({'error': 'Hotel not found.'}, status=404)
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        return Response({
            'hotel_id': hotel_id,
            'hotel_name': hotel['name'],
            'available': True,
            'available_rooms': 8,
            'check_in': check_in,
            'check_out': check_out,
        })


class FeaturedHotelsAPIView(APIView):
    """GET /api/hotels/featured/ — Featured hotels"""
    permission_classes = [AllowAny]

    def get(self, request):
        featured = [h for h in STATIC_HOTELS if h.get('is_featured')][:6]
        return Response({'results': HotelSerializer(featured, many=True).data})


class DealsAPIView(APIView):
    """GET /api/hotels/deals/ — Deal hotels sorted by price"""
    permission_classes = [AllowAny]

    def get(self, request):
        deals = sorted(STATIC_HOTELS, key=lambda x: x['price'])[:6]
        return Response({'results': HotelSerializer(deals, many=True).data})


# ─── Booking Endpoints ────────────────────────────────────────────────────────

class BookingListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/bookings/ — List user's bookings
    POST /api/bookings/ — Create a new booking
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBookingSerializer
        return BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateBookingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response({
            'booking': BookingSerializer(booking).data,
            'message': f'Booking confirmed! Reference: {booking.booking_ref}'
        }, status=status.HTTP_201_CREATED)


class BookingDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/bookings/<ref>/ — Get booking details
    DELETE /api/bookings/<ref>/ — Cancel booking
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_ref'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        return Response({'message': f'Booking {booking.booking_ref} cancelled.'})


# ─── Misc Endpoints ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """GET /api/health/ — Health check"""
    return Response({
        'status': 'ok',
        'service': 'LuxeStay API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'hotels': '/api/hotels/',
            'bookings': '/api/bookings/',
            'docs': '/api/docs/',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def cities_list(request):
    """GET /api/cities/ — List all cities"""
    cities = sorted(set(h['city'] for h in STATIC_HOTELS))
    return Response({'cities': cities})
