from rest_framework import serializers
from accounts.models import User
from bookings.models import Booking
from hotels.views import STATIC_HOTELS


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'mobile', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'mobile', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            mobile=validated_data.get('mobile', ''),
        )
        return user


class HotelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    location = serializers.CharField()
    city = serializers.CharField()
    price = serializers.IntegerField()
    image = serializers.CharField()
    rating = serializers.FloatField()
    reviews = serializers.IntegerField()
    stars = serializers.IntegerField()
    property_type = serializers.CharField()
    room_types = serializers.ListField(child=serializers.CharField())
    facilities = serializers.ListField(child=serializers.CharField())
    is_featured = serializers.BooleanField()


class BookingSerializer(serializers.ModelSerializer):
    nights = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_ref', 'user_name', 'hotel_id', 'hotel_name',
            'hotel_location', 'room_type', 'check_in', 'check_out',
            'guests', 'price_per_night', 'total_price', 'status',
            'payment_status', 'nights', 'is_upcoming', 'created_at',
        ]
        read_only_fields = ['id', 'booking_ref', 'total_price', 'created_at']

    def get_user_name(self, obj):
        return obj.user.full_name


class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['hotel_id', 'hotel_name', 'hotel_location', 'hotel_image',
                  'room_type', 'check_in', 'check_out', 'guests',
                  'price_per_night', 'special_requests']

    def validate(self, data):
        from django.utils import timezone
        if data['check_in'] < timezone.now().date():
            raise serializers.ValidationError("Check-in cannot be in the past.")
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        booking = Booking.objects.create(user=user, **validated_data)
        return booking
