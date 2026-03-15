from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min
from .models import Hotel, Room, Review, Amenity


# Static hotel data (same as Flask app, augmented)
STATIC_HOTELS = [
    {"id": 1, "name": "Hotel WK Comfort", "location": "New Delhi, India", "city": "New Delhi", "price": 4558, "image": "hotel1.jpg", "rating": 8.5, "reviews": 320, "stars": 4, "property_type": "hotel", "room_types": ["standard", "deluxe"], "facilities": ["wifi", "parking", "restaurant"], "is_featured": True},
    {"id": 2, "name": "FabHotel Atithi Residency", "location": "Mumbai, India", "city": "Mumbai", "price": 4544, "image": "hotel2.jpg", "rating": 8.2, "reviews": 280, "stars": 3, "property_type": "hotel", "room_types": ["standard", "family"], "facilities": ["wifi"], "is_featured": True},
    {"id": 3, "name": "Virasat Mahal Heritage Hotel", "location": "Jaipur, India", "city": "Jaipur", "price": 4664, "image": "hotel3.jpg", "rating": 9.1, "reviews": 450, "stars": 5, "property_type": "boutique", "room_types": ["deluxe", "suite"], "facilities": ["wifi", "spa", "pool"], "is_featured": True},
    {"id": 4, "name": "Hotel Calabash Luxury Villa", "location": "Delhi Airport, India", "city": "New Delhi", "price": 2477, "image": "hotel4.jpg", "rating": 7.8, "reviews": 190, "stars": 3, "property_type": "villa", "room_types": ["standard"], "facilities": ["wifi", "parking"], "is_featured": False},
    {"id": 5, "name": "The Grand Palace", "location": "Bangalore, India", "city": "Bangalore", "price": 5999, "image": "hotel5.jpg", "rating": 9.3, "reviews": 510, "stars": 5, "property_type": "hotel", "room_types": ["suite", "executive"], "facilities": ["wifi", "spa", "pool", "gym"], "is_featured": True},
    {"id": 6, "name": "Regal Residency", "location": "Chennai, India", "city": "Chennai", "price": 3899, "image": "hotel6.jpg", "rating": 8.0, "reviews": 220, "stars": 4, "property_type": "hotel", "room_types": ["standard", "deluxe"], "facilities": ["wifi", "restaurant"], "is_featured": False},
    {"id": 7, "name": "Ocean View Suites", "location": "Goa, India", "city": "Goa", "price": 7299, "image": "hotel7.jpg", "rating": 9.5, "reviews": 680, "stars": 5, "property_type": "resort", "room_types": ["suite", "family"], "facilities": ["wifi", "pool", "spa", "beach"], "is_featured": True},
    {"id": 8, "name": "Mountain Retreat", "location": "Manali, India", "city": "Manali", "price": 3299, "image": "hotel8.jpg", "rating": 8.7, "reviews": 340, "stars": 4, "property_type": "resort", "room_types": ["standard", "family"], "facilities": ["wifi", "restaurant", "fireplace"], "is_featured": False},
    {"id": 9, "name": "Luxury Stay Inn", "location": "Kolkata, India", "city": "Kolkata", "price": 4899, "image": "hotel9.jpg", "rating": 8.4, "reviews": 290, "stars": 4, "property_type": "hotel", "room_types": ["deluxe", "executive"], "facilities": ["wifi", "parking", "restaurant"], "is_featured": False},
    {"id": 10, "name": "Sunrise Hotel", "location": "Pune, India", "city": "Pune", "price": 4199, "image": "hotel10.jpg", "rating": 8.1, "reviews": 210, "stars": 3, "property_type": "hotel", "room_types": ["standard", "deluxe"], "facilities": ["wifi"], "is_featured": False},
    {"id": 11, "name": "Eiffel Panorama Hotel", "location": "Paris, France", "city": "Paris", "price": 18000, "image": "hotel3.jpg", "rating": 9.2, "reviews": 520, "stars": 5, "property_type": "hotel", "room_types": ["suite", "deluxe"], "facilities": ["wifi", "spa", "restaurant"], "is_featured": True},
    {"id": 12, "name": "Seine River Stay", "location": "Paris, France", "city": "Paris", "price": 12000, "image": "hotel4.jpg", "rating": 8.8, "reviews": 380, "stars": 4, "property_type": "hotel", "room_types": ["deluxe", "family"], "facilities": ["wifi", "restaurant"], "is_featured": False},
    {"id": 13, "name": "Historic Charm Hotel", "location": "Paris, France", "city": "Paris", "price": 15000, "image": "hotel5.jpg", "rating": 9.0, "reviews": 430, "stars": 5, "property_type": "boutique", "room_types": ["suite"], "facilities": ["wifi", "spa", "restaurant"], "is_featured": True},
    {"id": 14, "name": "Le Meurice", "location": "Paris, France", "city": "Paris", "price": 25000, "image": "hotel6.jpg", "rating": 9.7, "reviews": 620, "stars": 5, "property_type": "hotel", "room_types": ["suite", "presidential"], "facilities": ["wifi", "spa", "pool", "restaurant"], "is_featured": True},
    {"id": 15, "name": "Four Seasons George V", "location": "Paris, France", "city": "Paris", "price": 27000, "image": "hotel7.jpg", "rating": 9.8, "reviews": 700, "stars": 5, "property_type": "hotel", "room_types": ["suite", "presidential"], "facilities": ["wifi", "spa", "pool", "restaurant"], "is_featured": True},
    {"id": 16, "name": "La Réserve Paris Spa", "location": "Paris, France", "city": "Paris", "price": 30000, "image": "hotel8.jpg", "rating": 9.9, "reviews": 350, "stars": 5, "property_type": "boutique", "room_types": ["suite"], "facilities": ["wifi", "spa", "pool"], "is_featured": True},
]


def home_view(request):
    featured = [h for h in STATIC_HOTELS if h.get('is_featured')][:6]
    deals = sorted([h for h in STATIC_HOTELS], key=lambda x: x['price'])[:4]
    top_destinations = [
        {'name': 'Goa', 'tagline': 'Beach Paradise', 'image': 'goa.jpg', 'hotels': 47},
        {'name': 'Jaipur', 'tagline': 'Pink City Royals', 'image': 'jaipur.jpg', 'hotels': 62},
        {'name': 'Paris', 'tagline': 'City of Light', 'image': 'paris.jpg', 'hotels': 89},
        {'name': 'Manali', 'tagline': 'Mountain Magic', 'image': 'manali.jpg', 'hotels': 35},
        {'name': 'Mumbai', 'tagline': 'City of Dreams', 'image': 'mumbai.jpg', 'hotels': 115},
        {'name': 'Bangalore', 'tagline': 'Garden City', 'image': 'bangalore.jpg', 'hotels': 78},
    ]
    return render(request, 'hotels/home.html', {
        'featured_hotels': featured,
        'deal_hotels': deals,
        'destinations': top_destinations,
    })


def hotel_list_view(request):
    hotels = list(STATIC_HOTELS)

    # Filters
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '')
    max_price = request.GET.get('max_price', '')
    stars = request.GET.getlist('stars')
    property_type = request.GET.get('property_type', '')
    room_types = request.GET.getlist('room_type')
    facilities = request.GET.getlist('facilities')
    sort_by = request.GET.get('sort', 'featured')

    if query:
        hotels = [h for h in hotels if query.lower() in h['name'].lower() or query.lower() in h['location'].lower()]
    if city:
        hotels = [h for h in hotels if city.lower() in h['city'].lower()]
    if max_price:
        hotels = [h for h in hotels if h['price'] <= int(max_price)]
    if stars:
        star_ints = [int(s) for s in stars]
        hotels = [h for h in hotels if h['stars'] in star_ints]
    if property_type:
        hotels = [h for h in hotels if h['property_type'] == property_type]
    if facilities:
        hotels = [h for h in hotels if all(f in h.get('facilities', []) for f in facilities)]
    if room_types:
        hotels = [h for h in hotels if any(rt in h.get('room_types', []) for rt in room_types)]

    # Sort
    if sort_by == 'price_low':
        hotels.sort(key=lambda x: x['price'])
    elif sort_by == 'price_high':
        hotels.sort(key=lambda x: -x['price'])
    elif sort_by == 'rating':
        hotels.sort(key=lambda x: -x['rating'])
    elif sort_by == 'reviews':
        hotels.sort(key=lambda x: -x['reviews'])

    all_cities = sorted(set(h['city'] for h in STATIC_HOTELS))

    return render(request, 'hotels/hotel_list.html', {
        'hotels': hotels,
        'hotel_count': len(hotels),
        'all_cities': all_cities,
        'current_filters': {
            'q': query, 'city': city, 'max_price': max_price,
            'stars': stars, 'property_type': property_type,
            'room_types': room_types, 'facilities': facilities, 'sort': sort_by,
        }
    })


def hotel_detail_view(request, hotel_id):
    hotel = next((h for h in STATIC_HOTELS if h['id'] == hotel_id), None)
    if not hotel:
        from django.http import Http404
        raise Http404("Hotel not found")

    # Similar hotels
    similar = [h for h in STATIC_HOTELS if h['city'] == hotel['city'] and h['id'] != hotel_id][:3]

    # Room data for this hotel
    rooms = [
        {'id': hotel_id * 10 + 1, 'type': 'Standard', 'price': hotel['price'], 'capacity': 2, 'bed': 'King Bed', 'area': 280, 'view': 'City View', 'available': True},
        {'id': hotel_id * 10 + 2, 'type': 'Deluxe', 'price': int(hotel['price'] * 1.4), 'original': int(hotel['price'] * 1.6), 'capacity': 2, 'bed': 'King Bed', 'area': 380, 'view': 'Pool/Garden View', 'available': True},
        {'id': hotel_id * 10 + 3, 'type': 'Suite', 'price': int(hotel['price'] * 2.2), 'capacity': 4, 'bed': '2x Queen Beds', 'area': 580, 'view': 'Panoramic View', 'available': hotel['stars'] >= 4},
    ]

    amenity_icons = {
        'wifi': ('fas fa-wifi', 'Free WiFi'),
        'spa': ('fas fa-spa', 'Spa & Wellness'),
        'pool': ('fas fa-swimming-pool', 'Swimming Pool'),
        'parking': ('fas fa-parking', 'Free Parking'),
        'restaurant': ('fas fa-utensils', 'Restaurant'),
        'gym': ('fas fa-dumbbell', 'Fitness Center'),
        'beach': ('fas fa-umbrella-beach', 'Beach Access'),
        'fireplace': ('fas fa-fire', 'Fireplace'),
    }
    hotel_amenities = [(amenity_icons[f][0], amenity_icons[f][1]) for f in hotel.get('facilities', []) if f in amenity_icons]

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'similar_hotels': similar,
        'amenities': hotel_amenities,
    })


def deals_view(request):
    deals = sorted(STATIC_HOTELS, key=lambda x: x['rating'], reverse=True)[:8]
    return render(request, 'hotels/deals.html', {'deals': deals})


def contact_view(request):
    from django.contrib import messages as msg
    if request.method == 'POST':
        msg.success(request, 'Thank you for your message! Our team will get back to you within 24 hours.')
    return render(request, 'hotels/contact.html')
