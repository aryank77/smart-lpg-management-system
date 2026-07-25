from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Booking, Company, Contact, Profile
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# 💳 PAYMENT CREATE (FINAL FIXED)
def create_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = 800  # rupees

    order = client.order.create({
        "amount": amount * 100,   # ✅ paise (80000)
        "currency": "INR",
        "payment_capture": 1
    })

    booking.razorpay_order_id = order['id']
    booking.save()

    return render(request, "lpg_app/payment.html", {
        "order_id": order['id'],
        "amount": amount,   # ✅ rupees UI ke liye
        "key": settings.RAZORPAY_KEY_ID
    })


# 🧾 PAYMENT VERIFY
@csrf_exempt
def payment_verify(request):
    if request.method == "POST":
        data = request.POST

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            booking = Booking.objects.get(razorpay_order_id=data['razorpay_order_id'])

            booking.razorpay_payment_id = data['razorpay_payment_id']
            booking.is_paid = True
            booking.status = "Confirmed"
            booking.save()

            return redirect('history')

        except:
            return redirect('payment_failed')


# ❌ PAYMENT FAILED
def payment_failed(request):
    return HttpResponse("Payment Failed. Try Again.")


# 🔧 UTIL
def create_companies(request):
    if Company.objects.count() == 0:
        Company.objects.create(name="HP Gas")
        Company.objects.create(name="Indane Gas")
        Company.objects.create(name="Bharat Gas")
        return HttpResponse("Companies created")
    return HttpResponse("Already exists")


def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@gmail.com", "admin123")
        return HttpResponse("Admin created")
    return HttpResponse("Admin already exists")


# 🏠 PAGES
def index(request):
    return render(request, 'lpg_app/index.html')


def about(request):
    return render(request, 'lpg_app/about.html')


def contact(request):
    print(request.method)

    if request.method == "POST":
        Contact.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            subject=request.POST["subject"],
            message=request.POST["message"],
        )
        return render(request, "lpg_app/contact.html", {"success": True})

    return render(request, "lpg_app/contact.html")


# 🔐 AUTH
def register(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        role = request.POST.get('role') or 'user'
        Profile.objects.create(user=user, role=role)
        return redirect('login')

    return render(request, 'lpg_app/register.html')


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
                    return redirect('delivery_dashboard')
                else:
                    return redirect('select_company')

    return render(request, 'lpg_app/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


# 🏢 COMPANY
def select_company(request):
    companies = Company.objects.all()
    return render(request, 'lpg_app/select_company.html', {'companies': companies})


# 🔥 BOOKING
@login_required(login_url='login')
def book(request, company_id):
    company = Company.objects.get(id=company_id)

    if request.method == "POST":

        if Booking.objects.filter(user=request.user, is_paid=False).exists():
            return redirect('history')

        booking = Booking.objects.create(
            user=request.user,
            company=company,
            consumer_number=request.POST['consumer_number'],
            address=request.POST['address'],
            phone=request.POST['phone'],
        )

        return redirect('create_payment', booking_id=booking.id)

    return render(request, 'lpg_app/book.html', {'company': company})


# 📜 HISTORY
def history(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'lpg_app/history.html', {'bookings': bookings})


# 🚚 TRACKING
def track_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    time_passed = timezone.now() - booking.created_at

    if time_passed > timedelta(minutes=3) and booking.status != "Delivered":
        booking.status = "Delivered"
    elif time_passed > timedelta(minutes=2) and booking.status not in ["Out for Delivery", "Delivered"]:
        booking.status = "Out for Delivery"
    elif time_passed > timedelta(minutes=1) and booking.status == "Pending":
        booking.status = "Approved"

    booking.save()

    return render(request, 'lpg_app/track.html', {'booking': booking})


# 🚚 DELIVERY
def delivery_dashboard(request):
    bookings = Booking.objects.all()
    return render(request, 'lpg_app/delivery.html', {'bookings': bookings})


def mark_delivered(request, id):
    booking = Booking.objects.get(id=id)
    booking.status = "Delivered"
    booking.save()
    return redirect('delivery_dashboard')

