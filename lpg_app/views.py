from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from .models import Booking, Company
from django.utils import timezone
from datetime import timedelta
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@gmail.com", "admin123")
        return HttpResponse("Admin created")
    return HttpResponse("Admin already exists")
# Home
def index(request):
    return render(request, 'lpg_app/index.html')


# About
def about(request):
    return render(request, 'lpg_app/about.html')


# Contact
def contact(request):
    return render(request, 'lpg_app/contact.html')


# Register
def register(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        role = request.POST.get('role')
        if not role:
            role = 'user'
        Profile.objects.create(user=user, role=role)
        return redirect('login')

    return render(request, 'lpg_app/register.html')


# Login
def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            
            if hasattr(user, 'profile'): 
                if user.profile.role == 'delivery':
                    return redirect('delivery_dashboard')  # Redirect
                else:
                    return redirect('select_company')

    return render(request, 'lpg_app/login.html')


# Logout
def user_logout(request):
    logout(request)
    return redirect('login')


# Select Company
def select_company(request):
    companies = Company.objects.all()
    return render(request, 'lpg_app/select_company.html', {'companies': companies})


# Book Cylinder
@login_required(login_url='login')
def book(request, company_id):
    company = Company.objects.get(id=company_id)

    if request.method == "POST":
        Booking.objects.create(
            user=request.user,
            company=company,
            consumer_number=request.POST['consumer_number'],
            address=request.POST['address'],
            phone=request.POST['phone'],
        )
        return redirect('history')

    return render(request, 'lpg_app/book.html', {'company': company})


# Booking History
def history(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'lpg_app/history.html', {'bookings': bookings})


# 🔥 TRACK BOOKING (AUTO STATUS UPDATE + TRUCK)
def track_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    time_passed = timezone.now() - booking.created_at

    # Auto status update
    if time_passed > timedelta(minutes=3) and booking.status != "Delivered":
        booking.status = "Delivered"

    elif time_passed > timedelta(minutes=2) and booking.status not in ["Out for Delivery", "Delivered"]:
        booking.status = "Out for Delivery"

    elif time_passed > timedelta(minutes=1) and booking.status == "Pending":
        booking.status = "Approved"

    booking.save()

    return render(request, 'lpg_app/track.html', {'booking': booking})


def delivery_dashboard(request):
    bookings = Booking.objects.all()
    return render(request, 'lpg_app/delivery.html', {'bookings': bookings})

def mark_delivered(request, id):
    booking = Booking.objects.get(id=id)
    booking.status = "Delivered"
    booking.save()
    return redirect('delivery_dashboard')