from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    CustomUser, HeavyVehicle, ServiceRequest, JobCard, 
    JobCardTask, MechanicWorkLog, SparePart, JobCardPartUsage, 
    Invoice, Payment, CustomerFeedback
)

# ------------------------------------------------------------------------------
# Module 1 Forms: User Registration & Authentication
# ------------------------------------------------------------------------------
class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile / Contact Number'}))
    company_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fleet / Logistics Company Name (Optional)'}))
    specialization = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization (For Mechanics, e.g. Engine Overhaul)'}))
    experience_years = forms.IntegerField(required=False, min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Workshop / Operating Address'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 
            'phone_number', 'company_name', 'specialization', 
            'experience_years', 'address'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Select, forms.CheckboxInput)):
                field.widget.attrs.setdefault('class', 'form-control')


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


# ------------------------------------------------------------------------------
# Module 2 Forms: Vehicle & Customer Management
# ------------------------------------------------------------------------------
class HeavyVehicleForm(forms.ModelForm):
    class Meta:
        model = HeavyVehicle
        fields = [
            'registration_number', 'vehicle_type', 'make', 'model_name',
            'manufacture_year', 'chassis_number', 'engine_number',
            'odometer_reading', 'fuel_type', 'gross_vehicle_weight'
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. KA-01-E-9842'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tata Motors, BharatBenz, Ashok Leyland'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Prima 5530.S, 3520 Tipper'}),
            'manufacture_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2030}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '17-digit Chassis / VIN'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Engine Serial Number'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current km'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'gross_vehicle_weight': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 40 Tonnes'}),
        }


# ------------------------------------------------------------------------------
# Module 3 Forms: Service Request Management
# ------------------------------------------------------------------------------
class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            'vehicle', 'service_type', 'priority', 'preferred_date', 
            'breakdown_location', 'description'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'breakdown_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if bringing vehicle to workshop, or enter Highway / Site location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Explain symptoms, warning lights, unusual sounds or requested repairs...'}),
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        if customer:
            self.fields['vehicle'].queryset = HeavyVehicle.objects.filter(customer=customer)


class ServiceRequestAssignForm(forms.ModelForm):
    estimated_completion = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = ServiceRequest
        fields = ['assigned_mechanic']
        widgets = {
            'assigned_mechanic': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_mechanic'].queryset = CustomUser.objects.filter(role='MECHANIC')
        self.fields['assigned_mechanic'].required = True


# ------------------------------------------------------------------------------
# Module 4 Forms: Job Card Management
# ------------------------------------------------------------------------------
class JobCardUpdateForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = [
            'status', 'meter_reading_in', 'meter_reading_out',
            'estimated_completion', 'actual_completion',
            'diagnosis_findings', 'work_performed_summary'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'meter_reading_in': forms.NumberInput(attrs={'class': 'form-control'}),
            'meter_reading_out': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_completion': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'actual_completion': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'diagnosis_findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_performed_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class JobCardTaskForm(forms.ModelForm):
    class Meta:
        model = JobCardTask
        fields = ['task_name']
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add checklist item (e.g. Inspect brake linings, Bleed air lines)'}),
        }


# ------------------------------------------------------------------------------
# Module 5 Forms: Mechanic Task & Work Log
# ------------------------------------------------------------------------------
class MechanicWorkLogForm(forms.ModelForm):
    class Meta:
        model = MechanicWorkLog
        fields = ['activity_title', 'hours_spent', 'work_details']
        widgets = {
            'activity_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Disassembled rear axle diff assembly'}),
            'hours_spent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'work_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Technical notes, torque specs applied, observations...'}),
        }


# ------------------------------------------------------------------------------
# Module 6 Forms: Inventory Management
# ------------------------------------------------------------------------------
class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = [
            'part_number', 'name', 'category', 'unit_price', 'cost_price',
            'quantity_in_stock', 'reorder_threshold', 'unit_of_measure',
            'rack_location', 'supplier_name', 'description'
        ]
        widgets = {
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PCS, LTR, SET, MTR'}),
            'rack_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bay / Shelf Number'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class JobCardPartUsageForm(forms.ModelForm):
    class Meta:
        model = JobCardPartUsage
        fields = ['part', 'quantity']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        part = cleaned_data.get('part')
        quantity = cleaned_data.get('quantity')
        if part and quantity:
            if part.quantity_in_stock < quantity:
                raise forms.ValidationError(
                    f"Insufficient inventory! Only {part.quantity_in_stock} {part.unit_of_measure} of '{part.name}' in stock."
                )
        return cleaned_data


# ------------------------------------------------------------------------------
# Module 7 Forms: Billing & Payment Management
# ------------------------------------------------------------------------------
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'labor_hours', 'labor_rate_per_hour', 'roadside_assistance_fee',
            'discount_amount', 'tax_rate', 'notes'
        ]
        widgets = {
            'labor_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'labor_rate_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '50'}),
            'roadside_assistance_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '50'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment terms or customer notes...'}),
        }


class PaymentProcessForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    card_or_upi_info = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number (e.g. 4532... ) or UPI ID (e.g. fleet@upi)'})
    )
    payer_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cardholder or Account Holder Name'})
    )


# ------------------------------------------------------------------------------
# Module 8 Forms: Customer Feedback & Reviews
# ------------------------------------------------------------------------------
class CustomerFeedbackForm(forms.ModelForm):
    class Meta:
        model = CustomerFeedback
        fields = ['rating', 'timeliness_rating', 'quality_rating', 'comments']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'timeliness_rating': forms.Select(
                choices=[(1, '1 - Very Late'), (2, '2 - Delayed'), (3, '3 - On Schedule'), (4, '4 - Fast'), (5, '5 - Ahead of Schedule')],
                attrs={'class': 'form-select'}
            ),
            'quality_rating': forms.Select(
                choices=[(1, '1 - Poor Repair'), (2, '2 - Mediocre'), (3, '3 - Standard'), (4, '4 - High Quality'), (5, '5 - Flawless Quality')],
                attrs={'class': 'form-select'}
            ),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your service experience, driver feedback, and vehicle performance...'}),
        }
