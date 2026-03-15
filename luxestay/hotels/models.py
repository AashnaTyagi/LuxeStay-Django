from django.db import models
from django.utils.text import slugify


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fas fa-check')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Amenities'


class Hotel(models.Model):
    PROPERTY_TYPES = (
        ('hotel', 'Hotel'),
        ('resort', 'Resort'),
        ('villa', 'Villa'),
        ('apartment', 'Apartment'),
        ('boutique', 'Boutique Hotel'),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='hotel')
    stars = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=8.0)
    reviews_count = models.IntegerField(default=0)
    amenities = models.ManyToManyField(Amenity, blank=True)
    image = models.CharField(max_length=200, default='hotel1.jpg')  # filename in static
    thumbnail = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    is_deal = models.BooleanField(default=False)
    deal_discount = models.IntegerField(default=0)  # percent off
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def min_price(self):
        rooms = self.rooms.filter(is_available=True)
        if rooms.exists():
            return rooms.order_by('price').first().price
        return self.rooms.order_by('price').first().price if self.rooms.exists() else 0

    class Meta:
        ordering = ['-is_featured', '-rating']


class Room(models.Model):
    ROOM_TYPES = (
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
        ('family', 'Family'),
        ('executive', 'Executive'),
        ('presidential', 'Presidential Suite'),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES, default='standard')
    room_number = models.CharField(max_length=10, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.IntegerField(default=2)
    bed_type = models.CharField(max_length=50, default='King Bed')
    is_available = models.BooleanField(default=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    area_sqft = models.IntegerField(default=300)
    floor = models.IntegerField(default=1)
    view = models.CharField(max_length=100, default='City View')
    image = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.get_room_type_display()}"

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((self.original_price - self.price) / self.original_price * 100)
        return 0


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.hotel.name} ({self.rating}★)"

    class Meta:
        ordering = ['-created_at']
