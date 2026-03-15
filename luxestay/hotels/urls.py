from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('hotels/', views.hotel_list_view, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail_view, name='hotel_detail'),
    path('deals/', views.deals_view, name='deals'),
    path('contact/', views.contact_view, name='contact'),
]
