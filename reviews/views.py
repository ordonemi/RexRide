from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from rides.models import TripHistory
from users.models import User
from .forms import ReviewForm
from django.contrib import messages
from rides.models import RidePost
from django.db.models import Prefetch

@login_required
def add_review(request, ride_id, reviewed_user_id):
    message = ""
    trip = get_object_or_404(TripHistory, post_id=ride_id, user_id=reviewed_user_id)

    # Check if the trip is completed before allowing a review
    if trip.status != 'Completed':
        message = "You cannot review this trip because it has not been completed yet."
        trip_history_passenger = TripHistory.objects.filter(
            user=request.user,
            role="Passenger"
        ).select_related('post', 'post__departure_city', 'post__destination_city', 'post__driver')

        trip_history_driver = TripHistory.objects.filter(
            post__driver=request.user,
            role="Driver"
        ).select_related('post', 'post__departure_city', 'post__destination_city', 'user').prefetch_related(
            Prefetch('post__triphistory_set', queryset=TripHistory.objects.filter(role="Passenger", is_approved=True))
        )

        return render(request, 'trip-history.html', {
            'trip_history_passenger': trip_history_passenger,
            'trip_history_driver': trip_history_driver,
            'message': message
        })
    
    ride = get_object_or_404(RidePost, id=ride_id)

    reviewed_user = get_object_or_404(User, id=reviewed_user_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_user = reviewed_user
            review.ride = ride
            review.save()
            return redirect('view_trip_history')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'reviewed_user': reviewed_user, 'ride': ride})

@login_required
def view_reviews(request, reviewed_user_id):
    reviewed_user = get_object_or_404(User, id=reviewed_user_id)
    reviews = Review.objects.filter(reviewed_user=reviewed_user)
    return render(request, 'view_reviews.html', {'reviews': reviews, 'reviewed_user': reviewed_user})

@login_required
def view_written_reviews(request):
    written_reviews = Review.objects.filter(reviewer=request.user)
    return render(request, 'view_written_reviews.html', {'written_reviews': written_reviews})
