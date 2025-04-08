from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            message = "Passwords do not match."
            return render(request, 'register.html', {'message': message})

        # Additional validation and user creation logic
        User.objects.create_user(name=username, email=email, password=password)
        message = "Registration successful! Please log in to continue."
        return redirect('/user/login/', {'message': message})

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Log the user in
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect('/home/')
        else:
            message =  "Invalid email or password."
            return render(request, 'login.html', {'message': message})

    return render(request, 'login.html')

def logout_confirm(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('/user/login/')
    return render(request, 'logout_confirm.html')