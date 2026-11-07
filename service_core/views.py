import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.db import models

from .models import (
    CustomUser, HeavyVehicle, ServiceRequest, JobCard, 
    JobCardTask, MechanicWorkLog, SparePart, JobCardPartUsage, 
    Invoice, Payment, CustomerFeedback
)
from .forms import (
    UserRegistrationForm, UserLoginForm, HeavyVehicleForm,
    ServiceRequestForm, ServiceRequestAssignForm, JobCardUpdateForm,
    JobCardTaskForm, MechanicWorkLogForm, SparePartForm,
    JobCardPartUsageForm, InvoiceForm, PaymentProcessForm, CustomerFeedbackForm
)
from .decorators import admin_required, mechanic_required, customer_required


# ==============================================================================
# MODULE 1: Authentication & Navigation Views
# ==============================================================================
def home_view(request):
    total_vehicles = HeavyVehicle.objects.count()
    completed_jobs = JobCard.objects.filter(status__in=['COMPLETED', 'CLOSED']).count()
    active_mechanics = CustomUser.objects.filter(role='MECHANIC').count()
    avg_rating_val = CustomerFeedback.objects.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_val, 1) if avg_rating_val else 4.9

    context = {
        'total_vehicles': total_vehicles,
        'completed_jobs': completed_jobs,
        'active_mechanics': active_mechanics,
        'avg_rating': avg_rating,
    }
    return render(request, 'home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account successfully registered as {user.get_role_display()}! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_redirect_view(request):
    if request.user.is_admin_role:
        return redirect('admin_dashboard')
    elif request.user.is_mechanic_role:
        return redirect('mechanic_dashboard')
    else:
        return redirect('customer_dashboard')


@login_required
@admin_required
def admin_dashboard(request):
    total_vehicles = HeavyVehicle.objects.count()
    pending_requests_count = ServiceRequest.objects.filter(status='PENDING').count()
    active_job_cards_count = JobCard.objects.filter(status__in=['OPEN', 'IN_PROGRESS', 'AWAITING_PARTS', 'TESTING']).count()
    low_stock_parts_count = SparePart.objects.filter(quantity_in_stock__lte=models.F('reorder_threshold')).count()
    
    total_revenue = Invoice.objects.filter(status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

    recent_requests = ServiceRequest.objects.filter(status='PENDING')[:5]
    active_job_cards = JobCard.objects.exclude(status__in=['COMPLETED', 'CLOSED']).order_by('-created_at')[:5]
    low_stock_parts = [p for p in SparePart.objects.all() if p.is_low_stock][:5]
    recent_feedbacks = CustomerFeedback.objects.order_by('-submitted_at')[:4]

    context = {
        'total_vehicles': total_vehicles,
        'pending_requests_count': pending_requests_count,
        'active_job_cards_count': active_job_cards_count,
        'low_stock_parts_count': low_stock_parts_count,
        'total_revenue': total_revenue,
        'recent_requests': recent_requests,
        'active_job_cards': active_job_cards,
        'low_stock_parts': low_stock_parts,
        'recent_feedbacks': recent_feedbacks,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
@mechanic_required
def mechanic_dashboard(request):
    assigned_cards = JobCard.objects.filter(
        assigned_mechanic=request.user
    ).exclude(status='CLOSED').order_by('-created_at')

    completed_count = JobCard.objects.filter(
        assigned_mechanic=request.user, 
        status__in=['COMPLETED', 'CLOSED']
    ).count()

    feedbacks = CustomerFeedback.objects.filter(mechanic=request.user)
    avg_rating_val = feedbacks.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_val, 1) if avg_rating_val else "N/A"

    total_hours = MechanicWorkLog.objects.filter(mechanic=request.user).aggregate(Sum('hours_spent'))['hours_spent__sum'] or Decimal('0.00')

    context = {
        'assigned_cards': assigned_cards,
        'completed_count': completed_count,
        'avg_rating': avg_rating,
        'total_hours': total_hours,
        'feedbacks': feedbacks[:4],
    }
    return render(request, 'dashboards/mechanic_dashboard.html', context)


@login_required
@customer_required
def customer_dashboard(request):
    vehicles = HeavyVehicle.objects.filter(customer=request.user)
    service_requests = ServiceRequest.objects.filter(customer=request.user).order_by('-created_at')[:5]
    unpaid_invoices = Invoice.objects.filter(customer=request.user, status='UNPAID')
    
    # Active jobs for tracking
    active_jobs = JobCard.objects.filter(
        service_request__customer=request.user
    ).exclude(status='CLOSED').order_by('-created_at')

    # Completed jobs eligible for feedback
    completed_without_feedback = JobCard.objects.filter(
        service_request__customer=request.user,
        status__in=['COMPLETED', 'CLOSED'],
        feedback__isnull=True
    )

    context = {
        'vehicles': vehicles,
        'service_requests': service_requests,
        'unpaid_invoices': unpaid_invoices,
        'active_jobs': active_jobs,
        'completed_without_feedback': completed_without_feedback,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


# ==============================================================================
# MODULE 2: Vehicle & Customer Management Views
# ==============================================================================
@login_required
def vehicle_list(request):
    if request.user.is_admin_role or request.user.is_mechanic_role:
        vehicles = HeavyVehicle.objects.all().select_related('customer')
    else:
        vehicles = HeavyVehicle.objects.filter(customer=request.user)
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})


@login_required
@customer_required
def vehicle_create(request):
    if request.method == 'POST':
        form = HeavyVehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.customer = request.user
            vehicle.save()
            messages.success(request, f"Heavy Vehicle {vehicle.registration_number} registered successfully!")
            return redirect('vehicle_list')
    else:
        form = HeavyVehicleForm()
    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'title': 'Register Heavy Commercial Vehicle'})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(HeavyVehicle, pk=pk)
    if not (request.user.is_admin_role or request.user.is_mechanic_role or vehicle.customer == request.user):
        messages.error(request, "Permission denied.")
        return redirect('vehicle_list')

    service_history = ServiceRequest.objects.filter(vehicle=vehicle).order_by('-created_at')
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle, 'service_history': service_history})


# ==============================================================================
# MODULE 3: Service Request Management Views
# ==============================================================================
@login_required
def service_request_list(request):
    if request.user.is_admin_role:
        requests = ServiceRequest.objects.all().select_related('vehicle', 'customer', 'assigned_mechanic')
    elif request.user.is_mechanic_role:
        requests = ServiceRequest.objects.filter(assigned_mechanic=request.user).select_related('vehicle', 'customer')
    else:
        requests = ServiceRequest.objects.filter(customer=request.user).select_related('vehicle')
    return render(request, 'services/service_request_list.html', {'service_requests': requests})


@login_required
@customer_required
def service_request_create(request):
    # Customer must have at least one vehicle registered
    customer_vehicles = HeavyVehicle.objects.filter(customer=request.user)
    if not customer_vehicles.exists():
        messages.warning(request, "Please register your heavy vehicle before requesting service.")
        return redirect('vehicle_create')

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, customer=request.user)
        if form.is_valid():
            req = form.save(commit=False)
            req.customer = request.user
            req.save()
            messages.success(request, f"Service Request {req.request_number} submitted! Our workshop team will review and assign a mechanic.")
            return redirect('service_request_detail', pk=req.pk)
    else:
        form = ServiceRequestForm(customer=request.user)

    return render(request, 'services/service_request_form.html', {'form': form})


@login_required
def service_request_detail(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    if not (request.user.is_admin_role or req.customer == request.user or (req.assigned_mechanic == request.user)):
        messages.error(request, "Access restricted.")
        return redirect('dashboard_redirect')
    return render(request, 'services/service_request_detail.html', {'req': req})


@login_required
@admin_required
def service_request_assign(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)

    if request.method == 'POST':
        form = ServiceRequestAssignForm(request.POST, instance=req)
        if form.is_valid():
            mechanic = form.cleaned_data['assigned_mechanic']
            est_comp = form.cleaned_data.get('estimated_completion')
            req.assigned_mechanic = mechanic
            req.status = 'ASSIGNED'
            req.save()

            # Create or update Job Card automatically
            job_card, created = JobCard.objects.get_or_create(
                service_request=req,
                defaults={
                    'assigned_mechanic': mechanic,
                    'assigned_by': request.user,
                    'meter_reading_in': req.vehicle.odometer_reading,
                    'estimated_completion': est_comp,
                    'status': 'OPEN'
                }
            )
            if not created:
                job_card.assigned_mechanic = mechanic
                if est_comp:
                    job_card.estimated_completion = est_comp
                job_card.save()

            # Initialize standard check tasks
            JobCardTask.objects.get_or_create(job_card=job_card, task_name="Initial visual inspection & safety check")
            JobCardTask.objects.get_or_create(job_card=job_card, task_name="Diagnostic scan & fluid level verification")
            JobCardTask.objects.get_or_create(job_card=job_card, task_name=f"Execute repair: {req.get_service_type_display()}")
            JobCardTask.objects.get_or_create(job_card=job_card, task_name="Final quality control & road test")

            messages.success(request, f"Request {req.request_number} assigned to mechanic {mechanic.get_full_name()}! Job Card {job_card.job_card_number} created.")
            return redirect('jobcard_detail', pk=job_card.pk)
    else:
        form = ServiceRequestAssignForm(instance=req)

    return render(request, 'services/service_request_assign.html', {'form': form, 'req': req})


# ==============================================================================
# MODULE 4 & 5: Job Card Management & Mechanic Work Tracking
# ==============================================================================
@login_required
def jobcard_list(request):
    if request.user.is_admin_role:
        cards = JobCard.objects.all().select_related('service_request__vehicle', 'assigned_mechanic')
    elif request.user.is_mechanic_role:
        cards = JobCard.objects.filter(assigned_mechanic=request.user).select_related('service_request__vehicle')
    else:
        cards = JobCard.objects.filter(service_request__customer=request.user).select_related('service_request__vehicle', 'assigned_mechanic')

    return render(request, 'jobcards/jobcard_list.html', {'job_cards': cards})


@login_required
def jobcard_detail(request, pk):
    card = get_object_or_404(JobCard, pk=pk)
    
    # Check permissions
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user or card.service_request.customer == request.user):
        messages.error(request, "Access restricted.")
        return redirect('dashboard_redirect')

    tasks = card.tasks.all()
    work_logs = card.work_logs.all()
    parts_used = card.parts_used.all().select_related('part')
    total_parts_cost = card.total_parts_cost()
    total_hours = card.total_labor_hours()

    task_form = JobCardTaskForm()
    log_form = MechanicWorkLogForm()
    part_usage_form = JobCardPartUsageForm()

    context = {
        'card': card,
        'tasks': tasks,
        'work_logs': work_logs,
        'parts_used': parts_used,
        'total_parts_cost': total_parts_cost,
        'total_hours': total_hours,
        'task_form': task_form,
        'log_form': log_form,
        'part_usage_form': part_usage_form,
    }
    return render(request, 'jobcards/jobcard_detail.html', context)


@login_required
def jobcard_update(request, pk):
    card = get_object_or_404(JobCard, pk=pk)
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user):
        messages.error(request, "Permission denied.")
        return redirect('jobcard_detail', pk=pk)

    if request.method == 'POST':
        form = JobCardUpdateForm(request.POST, instance=card)
        if form.is_valid():
            updated_card = form.save()
            # Sync service request status
            if updated_card.status in ['IN_PROGRESS', 'AWAITING_PARTS', 'TESTING']:
                updated_card.service_request.status = 'IN_PROGRESS'
            elif updated_card.status in ['COMPLETED', 'CLOSED']:
                updated_card.service_request.status = 'COMPLETED'
                if not updated_card.actual_completion:
                    updated_card.actual_completion = timezone.now()
                    updated_card.save()
            updated_card.service_request.save()

            messages.success(request, f"Job Card {card.job_card_number} updated to {card.get_status_display()}!")
            return redirect('jobcard_detail', pk=card.pk)
    else:
        form = JobCardUpdateForm(instance=card)

    return render(request, 'jobcards/jobcard_form.html', {'form': form, 'card': card})


@login_required
def jobcard_add_task(request, pk):
    card = get_object_or_404(JobCard, pk=pk)
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user):
        messages.error(request, "Permission denied.")
        return redirect('jobcard_detail', pk=pk)

    if request.method == 'POST':
        form = JobCardTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.job_card = card
            task.save()
            messages.success(request, f"Checklist item '{task.task_name}' added.")
    return redirect('jobcard_detail', pk=pk)


@login_required
def jobcard_toggle_task(request, pk, task_id):
    card = get_object_or_404(JobCard, pk=pk)
    task = get_object_or_404(JobCardTask, pk=task_id, job_card=card)
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user):
        messages.error(request, "Permission denied.")
        return redirect('jobcard_detail', pk=pk)

    task.is_completed = not task.is_completed
    task.completed_at = timezone.now() if task.is_completed else None
    task.save()
    return redirect('jobcard_detail', pk=pk)


@login_required
def jobcard_add_worklog(request, pk):
    card = get_object_or_404(JobCard, pk=pk)
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user):
        messages.error(request, "Permission denied.")
        return redirect('jobcard_detail', pk=pk)

    if request.method == 'POST':
        form = MechanicWorkLogForm(request.POST)
        if form.is_valid():
            log_item = form.save(commit=False)
            log_item.job_card = card
            log_item.mechanic = request.user
            log_item.save()
            messages.success(request, f"Work progress log logged: {log_item.hours_spent} hrs dedicated.")
    return redirect('jobcard_detail', pk=pk)


@login_required
def jobcard_issue_part(request, pk):
    card = get_object_or_404(JobCard, pk=pk)
    if not (request.user.is_admin_role or card.assigned_mechanic == request.user):
        messages.error(request, "Permission denied.")
        return redirect('jobcard_detail', pk=pk)

    if request.method == 'POST':
        form = JobCardPartUsageForm(request.POST)
        if form.is_valid():
            part = form.cleaned_data['part']
            quantity = form.cleaned_data['quantity']

            # Deduct from inventory
            part.quantity_in_stock -= quantity
            part.save()

            # Record usage
            usage = JobCardPartUsage.objects.create(
                job_card=card,
                part=part,
                quantity=quantity,
                unit_price=part.unit_price,
                issued_by=request.user
            )
            messages.success(request, f"Issued {quantity}x {part.name} to Job Card. Stock updated to {part.quantity_in_stock} {part.unit_of_measure}.")
        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect('jobcard_detail', pk=pk)


# ==============================================================================
# MODULE 6: Inventory Management Views
# ==============================================================================
@login_required
def inventory_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    filter_low_stock = request.GET.get('low_stock', '')

    parts = SparePart.objects.all()

    if query:
        parts = parts.filter(Q(name__icontains=query) | Q(part_number__icontains=query) | Q(supplier_name__icontains=query))
    if category:
        parts = parts.filter(category=category)
    if filter_low_stock == '1':
        parts = [p for p in parts if p.is_low_stock]

    categories = SparePart.CATEGORY_CHOICES
    low_stock_count = sum(1 for p in SparePart.objects.all() if p.is_low_stock)

    context = {
        'parts': parts,
        'categories': categories,
        'selected_category': category,
        'query': query,
        'low_stock_count': low_stock_count,
        'is_low_stock_filter': filter_low_stock == '1'
    }
    return render(request, 'inventory/inventory_list.html', context)


@login_required
@admin_required
def part_create(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            part = form.save()
            messages.success(request, f"Spare part '{part.name}' added to inventory!")
            return redirect('inventory_list')
    else:
        form = SparePartForm()
    return render(request, 'inventory/part_form.html', {'form': form, 'title': 'Add New Spare Part / Component'})


@login_required
@admin_required
def part_update(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, f"Spare part '{part.name}' updated successfully.")
            return redirect('inventory_list')
    else:
        form = SparePartForm(instance=part)
    return render(request, 'inventory/part_form.html', {'form': form, 'title': f'Edit Spare Part: {part.part_number}'})


# ==============================================================================
# MODULE 7: Billing & Payment Management Views
# ==============================================================================
@login_required
def invoice_list(request):
    if request.user.is_admin_role or request.user.is_mechanic_role:
        invoices = Invoice.objects.all().select_related('customer', 'job_card__service_request__vehicle')
    else:
        invoices = Invoice.objects.filter(customer=request.user).select_related('job_card__service_request__vehicle')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})


@login_required
@admin_required
def invoice_create(request, job_card_id):
    card = get_object_or_404(JobCard, pk=job_card_id)

    # If invoice already exists, redirect to it
    if hasattr(card, 'invoice'):
        return redirect('invoice_detail', pk=card.invoice.pk)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.job_card = card
            invoice.customer = card.service_request.customer
            invoice.calculate_totals()
            invoice.save()
            messages.success(request, f"Invoice {invoice.invoice_number} generated for {card.job_card_number}!")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        default_hours = card.total_labor_hours() or Decimal('3.0')
        form = InvoiceForm(initial={
            'labor_hours': default_hours,
            'labor_rate_per_hour': Decimal('600.00'),
            'tax_rate': Decimal('18.00'),
            'discount_amount': Decimal('0.00'),
            'roadside_assistance_fee': Decimal('1500.00') if card.service_request.breakdown_location else Decimal('0.00'),
        })

    parts_cost = card.total_parts_cost()
    return render(request, 'billing/invoice_form.html', {'form': form, 'card': card, 'parts_cost': parts_cost})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if not (request.user.is_admin_role or request.user.is_mechanic_role or invoice.customer == request.user):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_redirect')

    payments = invoice.payments.all()
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice, 'payments': payments})


@login_required
@customer_required
def process_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, customer=request.user)

    if invoice.status == 'PAID':
        messages.info(request, "This invoice is already fully paid.")
        return redirect('invoice_detail', pk=invoice.pk)

    if request.method == 'POST':
        form = PaymentProcessForm(request.POST)
        if form.is_valid():
            txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            payment_method = form.cleaned_data['payment_method']
            
            # Create payment record
            Payment.objects.create(
                invoice=invoice,
                transaction_id=txn_id,
                payment_method=payment_method,
                amount_paid=invoice.total_amount,
                status='SUCCESS',
                gateway_reference=f"AUTH-OK-{form.cleaned_data['payer_name'].replace(' ', '')}"
            )

            # Update invoice status
            invoice.status = 'PAID'
            invoice.paid_at = timezone.now()
            invoice.save()

            # Close job card and finalize service request
            job_card = invoice.job_card
            job_card.status = 'CLOSED'
            job_card.save()

            service_request = job_card.service_request
            service_request.status = 'COMPLETED'
            service_request.save()

            messages.success(request, f"Payment of ₹{invoice.total_amount:,.2f} successful! Transaction ID: {txn_id}. Invoice marked as PAID.")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = PaymentProcessForm()

    return render(request, 'billing/payment_form.html', {'form': form, 'invoice': invoice})


# ==============================================================================
# MODULE 8: Feedback & Reporting System Views
# ==============================================================================
@login_required
@customer_required
def feedback_create(request, job_card_id):
    card = get_object_or_404(JobCard, pk=job_card_id, service_request__customer=request.user)
    
    if hasattr(card, 'feedback'):
        messages.info(request, "Feedback has already been submitted for this service.")
        return redirect('feedback_list')

    if request.method == 'POST':
        form = CustomerFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job_card = card
            feedback.customer = request.user
            feedback.mechanic = card.assigned_mechanic
            feedback.save()
            messages.success(request, "Thank you! Your feedback and ratings have been submitted successfully.")
            return redirect('feedback_list')
    else:
        form = CustomerFeedbackForm()

    return render(request, 'feedback/feedback_form.html', {'form': form, 'card': card})


@login_required
def feedback_list(request):
    feedbacks = CustomerFeedback.objects.all().select_related('customer', 'mechanic', 'job_card__service_request__vehicle')
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 2) if avg_rating else 5.0
    return render(request, 'feedback/feedback_list.html', {'feedbacks': feedbacks, 'avg_rating': avg_rating})


@login_required
@admin_required
def reports_dashboard(request):
    # Overall operational statistics
    total_vehicles = HeavyVehicle.objects.count()
    total_services = ServiceRequest.objects.count()
    completed_services = ServiceRequest.objects.filter(status='COMPLETED').count()
    active_jobs = JobCard.objects.exclude(status__in=['COMPLETED', 'CLOSED']).count()

    # Financial Analytics
    paid_invoices = Invoice.objects.filter(status='PAID')
    total_revenue = paid_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    parts_revenue = paid_invoices.aggregate(Sum('parts_charges'))['parts_charges__sum'] or Decimal('0.00')
    labor_revenue = paid_invoices.aggregate(Sum('labor_charges'))['labor_charges__sum'] or Decimal('0.00')
    tax_collected = paid_invoices.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0.00')

    # Job status distribution
    job_statuses = JobCard.objects.values('status').annotate(count=Count('id'))

    # Mechanic workload & performance
    mechanics = CustomUser.objects.filter(role='MECHANIC').annotate(
        assigned_jobs_count=Count('job_cards'),
        avg_rating=Avg('mechanic_feedbacks__rating')
    )

    # Top spare parts consumed
    top_parts = JobCardPartUsage.objects.values('part__name', 'part__part_number').annotate(
        total_qty=Sum('quantity'),
        total_val=Sum('subtotal')
    ).order_by('-total_qty')[:5]

    context = {
        'total_vehicles': total_vehicles,
        'total_services': total_services,
        'completed_services': completed_services,
        'active_jobs': active_jobs,
        'total_revenue': total_revenue,
        'parts_revenue': parts_revenue,
        'labor_revenue': labor_revenue,
        'tax_collected': tax_collected,
        'job_statuses': job_statuses,
        'mechanics': mechanics,
        'top_parts': top_parts,
    }
    return render(request, 'reports/reports_dashboard.html', context)
