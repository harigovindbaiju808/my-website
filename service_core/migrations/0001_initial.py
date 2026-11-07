import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('ADMIN', 'Administrator / Workshop Manager'), ('MECHANIC', 'Service Mechanic / Technician'), ('CUSTOMER', 'Heavy Vehicle Owner / Fleet Manager')], default='CUSTOMER', max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, help_text='Fleet/Transport Company Name if applicable', max_length=150, null=True)),
                ('specialization', models.CharField(blank=True, help_text='e.g. Engine Overhaul, Hydraulics, Air Brakes, Heavy Electricals', max_length=100, null=True)),
                ('experience_years', models.PositiveIntegerField(default=0, help_text='Years of heavy vehicle experience')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='HeavyVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_number', models.CharField(help_text='e.g. KA-01-E-9842', max_length=30, unique=True)),
                ('vehicle_type', models.CharField(choices=[('TRUCK', 'Multi-Axle Cargo Truck'), ('TIPPER', 'Heavy Tipper / Mining Dumper'), ('TRAILER', 'Prime Mover & Semi-Trailer'), ('BUS', 'Commercial Passenger Bus (Inter-city)'), ('TANKER', 'Petroleum / Chemical Tanker'), ('CRANE', 'Hydraulic Mobile Crane / Rig'), ('TRACTOR_TOW', 'Heavy Recovery / Tow Vehicle'), ('OTHER', 'Special Heavy Commercial Vehicle')], default='TRUCK', max_length=30)),
                ('make', models.CharField(help_text='e.g. BharatBenz, Tata Motors, Ashok Leyland, Volvo, Scania', max_length=100)),
                ('model_name', models.CharField(help_text='e.g. 3520 Tipper, Prima 5530.S, Captain 2823', max_length=100)),
                ('manufacture_year', models.PositiveIntegerField(default=2021)),
                ('chassis_number', models.CharField(blank=True, help_text='VIN / Chassis Number', max_length=60, null=True)),
                ('engine_number', models.CharField(blank=True, max_length=60, null=True)),
                ('odometer_reading', models.PositiveIntegerField(default=0, help_text='Current odometer reading in km')),
                ('fuel_type', models.CharField(choices=[('DIESEL', 'Diesel'), ('CNG', 'Compressed Natural Gas (CNG)'), ('LNG', 'Liquefied Natural Gas (LNG)'), ('ELECTRIC', 'Electric Heavy Vehicle (EV)'), ('HYBRID', 'Diesel-Electric Hybrid')], default='DIESEL', max_length=30)),
                ('gross_vehicle_weight', models.CharField(blank=True, help_text='e.g. 35 Ton, 49 Ton', max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='service_core.customuser')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_card_number', models.CharField(editable=False, max_length=30, unique=True)),
                ('status', models.CharField(choices=[('OPEN', 'Job Card Open / Vehicle Received'), ('IN_PROGRESS', 'Work in Progress'), ('AWAITING_PARTS', 'Awaiting Spare Parts from Inventory'), ('TESTING', 'Dynamometer / Road Testing & QC'), ('COMPLETED', 'Service Complete & QC Cleared'), ('CLOSED', 'Closed & Invoiced')], default='OPEN', max_length=30)),
                ('meter_reading_in', models.PositiveIntegerField(default=0, help_text='Kilometers upon workshop entry')),
                ('meter_reading_out', models.PositiveIntegerField(blank=True, help_text='Kilometers after testing', null=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('estimated_completion', models.DateTimeField(blank=True, null=True)),
                ('actual_completion', models.DateTimeField(blank=True, null=True)),
                ('diagnosis_findings', models.TextField(blank=True, help_text='Technical diagnostic observations', null=True)),
                ('work_performed_summary', models.TextField(blank=True, help_text='Summary of repairs and adjustments executed', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_job_cards', to='service_core.customuser')),
                ('assigned_mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_cards', to='service_core.customuser')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SparePart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.CharField(help_text='SKU / OEM Part #', max_length=60, unique=True)),
                ('name', models.CharField(max_length=150)),
                ('category', models.CharField(choices=[('ENGINE', 'Engine Components & Turbochargers'), ('BRAKES', 'Pneumatic Brakes, Valves & Drums'), ('SUSPENSION', 'Multi-Leaf Springs & Air Bellows'), ('TRANSMISSION', 'Clutches, Gear Sets & Propeller Shafts'), ('HYDRAULICS', 'Hydraulic Cylinders, Pumps & High-Pressure Hoses'), ('ELECTRICAL', 'Starters, Alternators, Relays & Sensors'), ('FILTERS_LUBES', 'Heavy Filters, Engine Oils & Differential Fluids')], max_length=30)),
                ('unit_price', models.DecimalField(decimal_places=2, help_text='Selling price per unit in INR (₹)', max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('quantity_in_stock', models.PositiveIntegerField(default=0)),
                ('reorder_threshold', models.PositiveIntegerField(default=5, help_text='Triggers low-stock warning')),
                ('unit_of_measure', models.CharField(default='Units', help_text='e.g. Units, Liters, Sets, Meters', max_length=20)),
                ('supplier_name', models.CharField(blank=True, max_length=150, null=True)),
                ('rack_location', models.CharField(blank=True, help_text='Bay / Shelf Number', max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_number', models.CharField(editable=False, max_length=30, unique=True)),
                ('service_type', models.CharField(choices=[('ROUTINE', 'Routine Preventive Maintenance (Periodic Service)'), ('ENGINE', 'Engine Overhaul & Fuel Injector Calibration'), ('BRAKE_SUSPENSION', 'Pneumatic Brake Shoes, Drums & Air Suspension Service'), ('HYDRAULIC', 'Hydraulic Ram, Valve & Tipper Cylinder Repair'), ('TRANSMISSION', 'Heavy Clutch, Differential & Gearbox Overhaul'), ('ELECTRICAL', 'Commercial Vehicle Electrical, Alternator & ECU Diagnostics'), ('BREAKDOWN', 'Emergency On-Highway Heavy Breakdown Assistance')], max_length=40)),
                ('priority', models.CharField(choices=[('LOW', 'Low - Planned Fleet Maintenance'), ('MEDIUM', 'Medium - Scheduled Repair'), ('HIGH', 'High - Immediate Attention Required'), ('CRITICAL', 'Critical - Roadside Breakdown / Immobility')], default='MEDIUM', max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending Admin Review'), ('ASSIGNED', 'Mechanic Assigned / Job Card Generated'), ('IN_PROGRESS', 'Service in Progress'), ('COMPLETED', 'Service Completed'), ('CANCELLED', 'Request Cancelled')], default='PENDING', max_length=20)),
                ('description', models.TextField(help_text='Detailed description of symptoms, noises, or requested service work')),
                ('breakdown_location', models.CharField(blank=True, help_text='Enter highway mile marker, site, or city if mobile service unit is required', max_length=255, null=True)),
                ('preferred_date', models.DateField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_mechanic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_requests', to='service_core.customuser')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to='service_core.customuser')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to='service_core.heavyvehicle')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MechanicWorkLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_title', models.CharField(max_length=200)),
                ('work_details', models.TextField()),
                ('hours_spent', models.DecimalField(decimal_places=2, default=1.0, help_text='Labor hours dedicated', max_digits=5)),
                ('logged_at', models.DateTimeField(auto_now_add=True)),
                ('job_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_logs', to='service_core.jobcard')),
                ('mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_logs', to='service_core.customuser')),
            ],
            options={
                'ordering': ['-logged_at'],
            },
        ),
        migrations.CreateModel(
            name='JobCardTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('job_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='service_core.jobcard')),
            ],
        ),
        migrations.CreateModel(
            name='JobCardPartUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('issued_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service_core.customuser')),
                ('job_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts_used', to='service_core.jobcard')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_card_usages', to='service_core.sparepart')),
            ],
        ),
        migrations.AddField(
            model_name='jobcard',
            name='service_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job_card', to='service_core.servicerequest'),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(editable=False, max_length=30, unique=True)),
                ('labor_hours', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('labor_rate_per_hour', models.DecimalField(decimal_places=2, default=500.0, max_digits=8)),
                ('labor_charges', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('parts_charges', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('roadside_assistance_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=18.0, help_text='GST Percentage (e.g. 18%)', max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('status', models.CharField(choices=[('UNPAID', 'Awaiting Payment'), ('PAID', 'Paid in Full'), ('CANCELLED', 'Invoice Voided')], default='UNPAID', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='service_core.customuser')),
                ('job_card', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='service_core.jobcard')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=60, unique=True)),
                ('payment_method', models.CharField(choices=[('UPI', 'UPI / QR Code (GooglePay, PhonePe, Paytm)'), ('CARD', 'Credit / Debit Card (Commercial / Fleet Card)'), ('NET_BANKING', 'Corporate Internet Banking'), ('CASH', 'Cash at Workshop Counter')], default='UPI', max_length=30)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('SUCCESS', 'Payment Successful'), ('PENDING', 'Payment Pending'), ('FAILED', 'Payment Failed')], default='SUCCESS', max_length=20)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('gateway_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='service_core.invoice')),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='CustomerFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(5, '★★★★★ (5/5) - Outstanding & Rapid Service'), (4, '★★★★☆ (4/5) - Very Satisfied'), (3, '★★★☆☆ (3/5) - Satisfactory / Met Standard'), (2, '★★☆☆☆ (2/5) - Needs Improvement / Delayed'), (1, '★☆☆☆☆ (1/5) - Unsatisfactory Repair Work')], default=5)),
                ('timeliness_rating', models.PositiveSmallIntegerField(default=5)),
                ('quality_rating', models.PositiveSmallIntegerField(default=5)),
                ('comments', models.TextField(help_text='Share your thoughts on vehicle performance after repair and workshop professionalism')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='service_core.customuser')),
                ('job_card', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='service_core.jobcard')),
                ('mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mechanic_feedbacks', to='service_core.customuser')),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]
