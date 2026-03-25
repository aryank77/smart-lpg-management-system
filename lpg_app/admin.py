from django.contrib import admin
from .models import Booking, Company

admin.site.register(Company)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'consumer_number', 'address', 'phone', 'status', 'created_at')

admin.site.register(Booking, BookingAdmin)