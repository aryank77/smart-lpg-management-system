from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about),
    path('contact/', views.contact),

    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('select-company/', views.select_company, name='select_company'),
    path('book/<int:company_id>/', views.book, name='book'),

    path('history/', views.history, name='history'),
    path('track/<int:booking_id>/', views.track_booking, name='track'),

    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('deliver/<int:id>/', views.mark_delivered, name='mark_delivered'),

    path('create_companies/', views.create_companies),

    # 💳 PAYMENT ROUTES
    path('payment/<int:booking_id>/', views.create_payment, name='create_payment'),
    path('payment-verify/', views.payment_verify, name='payment_verify'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
]