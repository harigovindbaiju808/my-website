from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal

# ==============================================================================
# MODULE 1: User Registration & Authentication (Role-Based Access Control)
# ==============================================================================
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator / Workshop Manager'),
        ('MECHANIC', 'Service Mechanic / Technician'),
        ('CUSTOMER', 'Heavy Vehicle Owner / Fleet Manager'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True, null=True, help_text="Fleet/Transport Company Name if applicable")
    
    # Mechanic specific fields
    specialization = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="e.g. Engine Overhaul, Hydraulics, Air Brakes, Heavy Electricals"
    )
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of heavy vehicle experience")

    @property
    def is_admin_role(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_mechanic_role(self):
        return self.role == 'MECHANIC'

    @property
    def is_customer_role(self):
        return self.role == 'CUSTOMER'

    def __str__(self):
        role_label = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.get_full_name() or self.username} ({role_label})"


# ==============================================================================
# MODULE 2: Vehicle & Customer Management
# ==============================================================================
class HeavyVehicle(models.Model):
    VEHICLE_TYPE_CHOICES = (
        ('TRUCK', 'Multi-Axle Cargo Truck'),
        ('TIPPER', 'Heavy Tipper / Mining Dumper'),
        ('TRAILER', 'Prime Mover & Semi-Trailer'),
        ('BUS', 'Commercial Passenger Bus (Inter-city)'),
        ('TANKER', 'Petroleum / Chemical Tanker'),
        ('CRANE', 'Hydraulic Mobile Crane / Rig'),
        ('TRACTOR_TOW', 'Heavy Recovery / Tow Vehicle'),
        ('OTHER', 'Special Heavy Commercial Vehicle'),
    )

    FUEL_CHOICES = (
        ('DIESEL', 'Diesel'),
        ('CNG', 'Compressed Natural Gas (CNG)'),
        ('LNG', 'Liquefied Natural Gas (LNG)'),
        ('ELECTRIC', 'Electric Heavy Vehicle (EV)'),
        ('HYBRID', 'Diesel-Electric Hybrid'),
    )

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vehicles')
    registration_number = models.CharField(max_length=30, unique=True, help_text="e.g. KA-01-E-9842")
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPE_CHOICES, default='TRUCK')
    make = models.CharField(max_length=100, help_text="e.g. BharatBenz, Tata Motors, Ashok Leyland, Volvo, Scania")
    model_name = models.CharField(max_length=100, help_text="e.g. 3520 Tipper, Prima 5530.S, Captain 2823")
    manufacture_year = models.PositiveIntegerField(default=2021)
    chassis_number = models.CharField(max_length=60, blank=True, null=True, help_text="VIN / Chassis Number")
    engine_number = models.CharField(max_length=60, blank=True, null=True)
    odometer_reading = models.PositiveIntegerField(default=0, help_text="Current odometer reading in km")
    fuel_type = models.CharField(max_length=30, choices=FUEL_CHOICES, default='DIESEL')
    gross_vehicle_weight = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 35 Ton, 49 Ton")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration_number} - {self.make} {self.model_name} ({self.get_vehicle_type_display()})"

    class Meta:
        ordering = ['-created_at']


# ==============================================================================
# MODULE 3: Service Request Management
# ==============================================================================
class ServiceRequest(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('ROUTINE', 'Routine Preventive Maintenance (Periodic Service)'),
        ('ENGINE', 'Engine Overhaul & Fuel Injector Calibration'),
        ('BRAKE_SUSPENSION', 'Pneumatic Brake Shoes, Drums & Air Suspension Service'),
        ('HYDRAULIC', 'Hydraulic Ram, Valve & Tipper Cylinder Repair'),
        ('TRANSMISSION', 'Heavy Clutch, Differential & Gearbox Overhaul'),
        ('ELECTRICAL', 'Commercial Vehicle Electrical, Alternator & ECU Diagnostics'),
        ('BREAKDOWN', 'Emergency On-Highway Heavy Breakdown Assistance'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low - Planned Fleet Maintenance'),
        ('MEDIUM', 'Medium - Scheduled Repair'),
        ('HIGH', 'High - Immediate Attention Required'),
        ('CRITICAL', 'Critical - Roadside Breakdown / Immobility'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending Admin Review'),
        ('ASSIGNED', 'Mechanic Assigned / Job Card Generated'),
        ('IN_PROGRESS', 'Service in Progress'),
        ('COMPLETED', 'Service Completed'),
        ('CANCELLED', 'Request Cancelled'),
    )

    request_number = models.CharField(max_length=30, unique=True, editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_requests')
    vehicle = models.ForeignKey(HeavyVehicle, on_delete=models.CASCADE, related_name='service_requests')
    service_type = models.CharField(max_length=40, choices=SERVICE_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(help_text="Detailed description of symptoms, noises, or requested service work")
    breakdown_location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Enter highway mile marker, site, or city if mobile service unit is required"
    )
    preferred_date = models.DateField(default=timezone.now)
    assigned_mechanic = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            year = timezone.now().strftime('%Y')
            last_id = ServiceRequest.objects.count() + 1
            self.request_number = f"REQ-{year}-{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} | {self.vehicle.registration_number} ({self.get_service_type_display()})"

    class Meta:
        ordering = ['-created_at']


# ==============================================================================
# MODULE 4: Job Card Management
# ==============================================================================
class JobCard(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Job Card Open / Vehicle Received'),
        ('IN_PROGRESS', 'Work in Progress'),
        ('AWAITING_PARTS', 'Awaiting Spare Parts from Inventory'),
        ('TESTING', 'Dynamometer / Road Testing & QC'),
        ('COMPLETED', 'Service Complete & QC Cleared'),
        ('CLOSED', 'Closed & Invoiced'),
    )

    job_card_number = models.CharField(max_length=30, unique=True, editable=False)
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='job_card')
    assigned_mechanic = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_cards')
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_job_cards')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    meter_reading_in = models.PositiveIntegerField(help_text="Kilometers upon workshop entry", default=0)
    meter_reading_out = models.PositiveIntegerField(blank=True, null=True, help_text="Kilometers after testing")
    start_time = models.DateTimeField(default=timezone.now)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    diagnosis_findings = models.TextField(blank=True, null=True, help_text="Technical diagnostic observations")
    work_performed_summary = models.TextField(blank=True, null=True, help_text="Summary of repairs and adjustments executed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.job_card_number:
            year = timezone.now().strftime('%Y')
            last_id = JobCard.objects.count() + 1
            self.job_card_number = f"JC-{year}-{last_id:04d}"
        super().save(*args, **kwargs)

    def total_parts_cost(self):
        total = sum(item.subtotal for item in self.parts_used.all())
        return total or Decimal('0.00')

    def total_labor_hours(self):
        total = sum(log.hours_spent for log in self.work_logs.all())
        return total or Decimal('0.00')

    def __str__(self):
        return f"{self.job_card_number} | {self.service_request.vehicle.registration_number}"

    class Meta:
        ordering = ['-created_at']


class JobCardTask(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status_flag = "✓" if self.is_completed else "○"
        return f"[{status_flag}] {self.task_name}"


# ==============================================================================
# MODULE 5: Mechanic Task & Progress Tracking
# ==============================================================================
class MechanicWorkLog(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='work_logs')
    mechanic = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='work_logs')
    activity_title = models.CharField(max_length=200)
    work_details = models.TextField()
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Labor hours dedicated")
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_title} ({self.hours_spent} hrs) by {self.mechanic.get_full_name()}"

    class Meta:
        ordering = ['-logged_at']


# ==============================================================================
# MODULE 6: Inventory Management (Spare Parts & Parts Issued)
# ==============================================================================
class SparePart(models.Model):
    CATEGORY_CHOICES = (
        ('ENGINE', 'Engine Components & Turbochargers'),
        ('BRAKES', 'Pneumatic Brakes, Valves & Drums'),
        ('SUSPENSION', 'Multi-Leaf Springs & Air Bellows'),
        ('TRANSMISSION', 'Clutches, Gear Sets & Propeller Shafts'),
        ('HYDRAULICS', 'Hydraulic Cylinders, Pumps & High-Pressure Hoses'),
        ('ELECTRICAL', 'Starters, Alternators, Relays & Sensors'),
        ('FILTERS_LUBES', 'Heavy Filters, Engine Oils & Differential Fluids'),
    )

    part_number = models.CharField(max_length=60, unique=True, help_text="SKU / OEM Part #")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price per unit in INR (₹)")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=5, help_text="Triggers low-stock warning")
    unit_of_measure = models.CharField(max_length=20, default='Units', help_text="e.g. Units, Liters, Sets, Meters")
    supplier_name = models.CharField(max_length=150, blank=True, null=True)
    rack_location = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. Bay 4 - Rack C")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_threshold

    def __str__(self):
        return f"[{self.part_number}] {self.name} ({self.quantity_in_stock} {self.unit_of_measure} available)"

    class Meta:
        ordering = ['name']


class JobCardPartUsage(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='parts_used')
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='job_card_usages')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.quantity) * Decimal(self.unit_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.part.name} for {self.job_card.job_card_number}"


# ==============================================================================
# MODULE 7: Billing & Payment Management
# ==============================================================================
class Invoice(models.Model):
    STATUS_CHOICES = (
        ('UNPAID', 'Awaiting Payment'),
        ('PAID', 'Paid in Full'),
        ('CANCELLED', 'Invoice Voided'),
    )

    invoice_number = models.CharField(max_length=30, unique=True, editable=False)
    job_card = models.OneToOneField(JobCard, on_delete=models.CASCADE, related_name='invoice')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='invoices')
    labor_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    labor_rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=500.0)
    labor_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    parts_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    roadside_assistance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.0, help_text="GST Percentage (e.g. 18%)")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNPAID')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def calculate_totals(self):
        # Calculate parts charges from job card parts
        self.parts_charges = self.job_card.total_parts_cost()
        
        # Calculate labor charges
        if not self.labor_hours or self.labor_hours == 0:
            self.labor_hours = self.job_card.total_labor_hours() or Decimal('2.0')
        self.labor_charges = Decimal(self.labor_hours) * Decimal(self.labor_rate_per_hour)
        
        # Subtotal before tax
        subtotal = self.labor_charges + self.parts_charges + Decimal(self.roadside_assistance_fee) - Decimal(self.discount_amount)
        if subtotal < 0:
            subtotal = Decimal('0.00')
            
        self.tax_amount = (subtotal * Decimal(self.tax_rate)) / Decimal('100.0')
        self.total_amount = subtotal + self.tax_amount

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().strftime('%Y')
            last_id = Invoice.objects.count() + 1
            self.invoice_number = f"INV-{year}-{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} | ₹{self.total_amount} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('UPI', 'UPI / QR Code (GooglePay, PhonePe, Paytm)'),
        ('CARD', 'Credit / Debit Card (Commercial / Fleet Card)'),
        ('NET_BANKING', 'Corporate Internet Banking'),
        ('CASH', 'Cash at Workshop Counter'),
    )

    STATUS_CHOICES = (
        ('SUCCESS', 'Payment Successful'),
        ('PENDING', 'Payment Pending'),
        ('FAILED', 'Payment Failed'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=60, unique=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    payment_date = models.DateTimeField(default=timezone.now)
    gateway_reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_id} | ₹{self.amount_paid} ({self.payment_method})"

    class Meta:
        ordering = ['-payment_date']


# ==============================================================================
# MODULE 8: Feedback & Reporting System
# ==============================================================================
class CustomerFeedback(models.Model):
    RATING_CHOICES = (
        (5, '★★★★★ (5/5) - Outstanding & Rapid Service'),
        (4, '★★★★☆ (4/5) - Very Satisfied'),
        (3, '★★★☆☆ (3/5) - Satisfactory / Met Standard'),
        (2, '★★☆☆☆ (2/5) - Needs Improvement / Delayed'),
        (1, '★☆☆☆☆ (1/5) - Unsatisfactory Repair Work'),
    )

    job_card = models.OneToOneField(JobCard, on_delete=models.CASCADE, related_name='feedback')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    mechanic = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mechanic_feedbacks')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    timeliness_rating = models.PositiveSmallIntegerField(default=5)
    quality_rating = models.PositiveSmallIntegerField(default=5)
    comments = models.TextField(help_text="Share your thoughts on vehicle performance after repair and workshop professionalism")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.job_card.job_card_number} - {self.rating} Stars by {self.customer.get_full_name() or self.customer.username}"

    class Meta:
        ordering = ['-submitted_at']
