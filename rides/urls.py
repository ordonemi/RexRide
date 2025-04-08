from django.urls import path
from . import views

urlpatterns = [
    path('search-ride/', views.view_all_rides, name='view_all_rides'),
    path('post-ride/', views.post_ride, name='post_ride'),
    path('trip-history/', views.view_trip_history, name='view_trip_history'),
    path('ride-details/<int:ride_id>/', views.ride_details, name='ride_details'),
    path('<int:ride_id>/book-ride/', views.book_ride, name='book_ride'),
    path('manage-booking-requests/', views.manage_booking_requests, name='manage_booking_requests'),
]