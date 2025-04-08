from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RidePost, City, TripHistory
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from django.db.models import Prefetch

@login_required
def view_all_rides(request):
    message = ''

    # Fetch all rides that are "In Progress" in the TripHistory Table
    rides = TripHistory.objects.filter(
        status="In Progress",
    ).select_related('post', 'post__driver', 'post__departure_city', 'post__destination_city')

    # Filtering logic
    departure_city = request.GET.get('departure_city')
    destination_city = request.GET.get('destination_city')
    departure_date = request.GET.get('departure_date')  # New filter for date

    if departure_city:
        # Filter by departure city through the related `post` field
        rides = rides.filter(post__departure_city__name__icontains=departure_city)
    if destination_city:
        # Filter by destination city through the related `post` field
        rides = rides.filter(post__destination_city__name__icontains=destination_city)
    if departure_date:
        try:
            # Parse the date and filter rides by the trip date
            parsed_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            rides = rides.filter(trip_date=parsed_date)
        except ValueError:
            message = "Invalid date format. Please use YYYY-MM-DD."

    return render(request, 'view_all_rides.html', {'rides': rides, 'message': message})

@login_required
def post_ride(request):
    if request.method == 'POST':
        # Get form data
        departure_city_id = request.POST['departure_city']
        destination_city_id = request.POST['destination_city']
        details = request.POST['details']
        departure_time = request.POST['departure_time']
        available_seats = request.POST['available_seats']

        # Fetch the related City objects
        departure_city = City.objects.get(id=departure_city_id)
        destination_city = City.objects.get(id=destination_city_id)

        # Create the RidePost
        ride_post = RidePost.objects.create(
            driver=request.user,
            departure_city=departure_city,
            destination_city=destination_city,
            details=details,
            departure_time=departure_time,
            available_seats=available_seats
        )

        # Add the ride to the TripHistory table
        TripHistory.objects.create(
            post=ride_post,
            user=request.user,
            role="Driver",  # Role is "Driver" since the user is creating the ride
            status="In Progress",  # Status is "In Progress" for a new ride
            trip_date=request.POST['departure_time'],  # Assuming the trip date is the same as the departure time
            is_approved=True  # Automatically approved for the driver
        )

        message = "Ride posted successfully!"
        return redirect(reverse('view_all_rides', {'message': message}))  # Redirect to the list of ride
    
    # Fetch all cities for the dropdown
    cities = City.objects.all()
    return render(request, 'post-ride.html', {'cities': cities})

@login_required
def view_trip_history(request):
    # Trips where the logged-in user was a passenger
    trip_history_passenger = TripHistory.objects.filter(
        user=request.user,
        role="Passenger"
    ).select_related('post', 'post__departure_city', 'post__destination_city', 'post__driver')

    # Trips where the logged-in user was a driver
    trip_history_driver = TripHistory.objects.filter(
        post__driver=request.user,
        role="Driver"
    ).select_related('post', 'post__departure_city', 'post__destination_city', 'user').prefetch_related(
        Prefetch('post__triphistory_set', queryset=TripHistory.objects.filter(role="Passenger", is_approved=True))
    )

    return render(request, 'trip-history.html', {
        'trip_history_passenger': trip_history_passenger,
        'trip_history_driver': trip_history_driver,
    })

@login_required
def ride_details(request, ride_id):
    # Get the ride by ID
    ride = get_object_or_404(RidePost.objects.select_related('driver', 'departure_city', 'destination_city'), id=ride_id)

    return render(request, 'ride-details.html', {'ride': ride})

@login_required
def book_ride(request, ride_id):
    message = ""
    # Get the ride object
    ride = get_object_or_404(RidePost, id=ride_id)

    # Check if the logged-in user is the driver
    if ride.driver == request.user:
        message = "You cannot book your own ride."
        return render(request, 'ride-details.html', {'ride': ride, 'message': message})
    
    # Check if the ride is already booked by the logged-in user
    if TripHistory.objects.filter(post=ride, user=request.user).exists():
        message = "You have already booked this ride."
        return render(request, 'ride-details.html', {'ride': ride, 'message': message})
    
    # Create a booking request
    TripHistory.objects.create(
        post=ride,
        user=request.user,
        role="Passenger",
        status="Pending Approval",
        trip_date=ride.departure_time,
        is_approved=False
    )

    message = 'Your booking request has been sent to the driver for approval. Check your trip history for updates.'
    return render(request, 'ride-details.html', {'ride': ride, 'message': message})

@login_required
def manage_booking_requests(request):
    message=""

    # Get all pending booking requests for the logged-in driver
    pending_requests = TripHistory.objects.filter(
        post__driver=request.user,
        is_approved=False,
        status="Pending Approval"
    ).select_related('post', 'user')

    # Get all rides for the logged-in driver that are in "In Progress"
    driver_rides = TripHistory.objects.filter(
        post__driver=request.user,
        role="Driver",
        status="In Progress"
    ).select_related('post', 'post__departure_city', 'post__destination_city')

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve" or action == "reject":
            request_id = request.POST.get("request_id")
            trip_request = get_object_or_404(TripHistory, id=request_id, post__driver=request.user)

            if action == "approve":
                # Update available seats for the ride
                ride = trip_request.post
                if ride.available_seats > 0:
                    ride.available_seats -= 1
                    ride.save()
                    trip_request.is_approved = True
                    trip_request.status = "Approved"
                    trip_request.save()
                    message = f"Booking request from {trip_request.user.name} has been approved."
                else:
                    trip_request.status = "Rejected"
                    trip_request.save()
                    message = "No available seats left for this ride."
            elif action == "reject":
                trip_request.status = "Rejected"
                trip_request.save()
                message = f"Booking request from {trip_request.user.name} has been rejected."

        elif action == "complete":
            ride_id = request.POST.get("ride_id")
            ride = get_object_or_404(TripHistory, id=ride_id, post__driver=request.user, role="Driver")

            # Mark the ride as complete
            ride.status = "Completed"
            ride.save()

            # Mark all other entries with the same post ID and driver ID as completed
            TripHistory.objects.filter(post=ride.post, post__driver=request.user).update(status="Completed")

            message = f"Ride from {ride.post.departure_city.name} to {ride.post.destination_city.name} has been marked as complete."

        return redirect('manage_booking_requests', {'message': message})

    return render(request, 'manage_booking_requests.html', {
        'pending_requests': pending_requests,
        'driver_rides': driver_rides
    })