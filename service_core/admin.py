from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, HeavyVehicle, ServiceRequest, JobCard, 
    JobCardTask, MechanicWorkLog, SparePart, JobCardPartUsage, 
    Invoice, Payment, CustomerFeedback
)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Heavy Vehicle Role Information', {
            'fields': ('role', 'phone_number', 'address', 'company_name', 'specialization', 'experience_years')
        }),
    )

@admin.register(HeavyVehicle)
class HeavyVehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'make', 'model_name', 'vehicle_type', 'customer', 'manufacture_year', 'odometer_reading')
    list_filter = ('vehicle_type', 'fuel_type', 'make')
    search_fields = ('registration_number', 'chassis_number', 'customer__username')

class JobCardInline(admin.StackedInline):
    model = JobCard
    extra = 0

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'vehicle', 'customer', 'service_type', 'priority', 'status', 'preferred_date')
    list_filter = ('status', 'priority', 'service_type')
    search_fields = ('request_number', 'vehicle__registration_number', 'customer__username')
    inlines = [JobCardInline]

class JobCardTaskInline(admin.TabularInline):
    model = JobCardTask
    extra = 1

class JobCardPartUsageInline(admin.TabularInline):
    model = JobCardPartUsage
    extra = 0

class MechanicWorkLogInline(admin.TabularInline):
    model = MechanicWorkLog
    extra = 0

@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ('job_card_number', 'service_request', 'assigned_mechanic', 'status', 'created_at')
    list_filter = ('status', 'assigned_mechanic')
    search_fields = ('job_card_number', 'service_request__vehicle__registration_number')
    inlines = [JobCardTaskInline, JobCardPartUsageInline, MechanicWorkLogInline]

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'name', 'category', 'unit_price', 'quantity_in_stock', 'reorder_threshold', 'unit_of_measure', 'is_low_stock')
    list_filter = ('category',)
    search_fields = ('part_number', 'name', 'supplier_name')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'job_card', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'customer__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'invoice', 'amount_paid', 'payment_method', 'status', 'payment_date')
    list_filter = ('payment_method', 'status')
    search_fields = ('transaction_id', 'invoice__invoice_number')

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('job_card', 'customer', 'mechanic', 'rating', 'submitted_at')
    list_filter = ('rating',)
    search_fields = ('customer__username', 'mechanic__username')

admin.site.register(CustomUser, CustomUserAdmin)
