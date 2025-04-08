from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rides.models import TripHistory

def landingpage(request):
    return render(request, 'landing.html')

@login_required
def home(request):
    message = ""

    # Check if the user is a driver and has any pending ride requests
    pending_requests = TripHistory.objects.filter(
        post__driver=request.user,
        is_approved=False,
        status="Pending Approval"
    ).exists()

    if (pending_requests):
        message = "You have a pending ride request. Please navigate to Manage Booking Requests to approve or reject it."

    return render(request, 'home.html', {'message': message})

@login_required
def profile(request):
    return render(request, 'profile.html', {
        'user': request.user
    })