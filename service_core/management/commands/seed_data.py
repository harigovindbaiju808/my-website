from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from service_core.models import (
    CustomUser, HeavyVehicle, ServiceRequest, JobCard,
    JobCardTask, MechanicWorkLog, SparePart, JobCardPartUsage,
    Invoice, Payment, CustomerFeedback
)

class Command(BaseCommand):
    help = 'Seeds initial heavy vehicle workshop data for demo and academic evaluation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing seed data for Heavy Vehicle Management System..."))

        # 1. Users
        # Admin
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Harigovind',
                'last_name': 'P B',
                'email': 'admin@heavyvehicle.local',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+91 9876543210',
                'company_name': 'Harigovind Heavy Motors Workshop',
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Mechanics
        mech1, _ = CustomUser.objects.get_or_create(
            username='mechanic_ravi',
            defaults={
                'first_name': 'Ravi',
                'last_name': 'Kumar',
                'email': 'ravi.mechanic@heavyvehicle.local',
                'role': 'MECHANIC',
                'phone_number': '+91 9845012345',
                'specialization': 'Diesel Engine Overhaul & Turbo Diagnostics',
                'experience_years': 8,
                'address': 'Bay 1, Heavy Vehicle Maintenance Hub'
            }
        )
        mech1.set_password('pass123')
        mech1.save()

        mech2, _ = CustomUser.objects.get_or_create(
            username='mechanic_anil',
            defaults={
                'first_name': 'Anil',
                'last_name': 'Sharma',
                'email': 'anil.mechanic@heavyvehicle.local',
                'role': 'MECHANIC',
                'phone_number': '+91 9823054321',
                'specialization': 'Pneumatic Air Brakes, Suspension & Hydraulics',
                'experience_years': 6,
                'address': 'Bay 2, Heavy Vehicle Maintenance Hub'
            }
        )
        mech2.set_password('pass123')
        mech2.save()

        # Customers
        cust1, _ = CustomUser.objects.get_or_create(
            username='fleet_kiran',
            defaults={
                'first_name': 'Kiran',
                'last_name': 'Patel',
                'email': 'kiran.logistics@gujaratfreight.com',
                'role': 'CUSTOMER',
                'phone_number': '+91 9712345678',
                'company_name': 'Gujarat Interstate Freight Carriers (50+ Fleets)',
                'address': 'Plot 42, Transport Nagar, Surat'
            }
        )
        cust1.set_password('pass123')
        cust1.save()

        cust2, _ = CustomUser.objects.get_or_create(
            username='suresh_tipper',
            defaults={
                'first_name': 'Suresh',
                'last_name': 'Reddy',
                'email': 'suresh.mining@reddytrans.com',
                'role': 'CUSTOMER',
                'phone_number': '+91 9440123890',
                'company_name': 'Reddy Earthmovers & Mining Transport',
                'address': 'Industrial Area, Bellary'
            }
        )
        cust2.set_password('pass123')
        cust2.save()

        self.stdout.write(self.style.SUCCESS("✓ User accounts created (Admin, Mechanics, Customers)."))

        # 2. Heavy Vehicles
        v1, _ = HeavyVehicle.objects.get_or_create(
            registration_number='KA-01-E-9842',
            defaults={
                'customer': cust1,
                'vehicle_type': 'TRAILER',
                'make': 'Tata Motors',
                'model_name': 'Prima 5530.S Prime Mover',
                'manufacture_year': 2022,
                'chassis_number': 'MAT615048N3C19283',
                'engine_number': 'CUMMINS-ISBe6.7-300',
                'odometer_reading': 148500,
                'fuel_type': 'DIESEL',
                'gross_vehicle_weight': '55 Tonnes'
            }
        )

        v2, _ = HeavyVehicle.objects.get_or_create(
            registration_number='KA-04-F-3112',
            defaults={
                'customer': cust1,
                'vehicle_type': 'TRUCK',
                'make': 'BharatBenz',
                'model_name': '2823R Multi-Axle Rigid Truck',
                'manufacture_year': 2021,
                'chassis_number': 'MBD2823RHB829104',
                'engine_number': 'OM926-LA-240HP',
                'odometer_reading': 92400,
                'fuel_type': 'DIESEL',
                'gross_vehicle_weight': '28 Tonnes'
            }
        )

        v3, _ = HeavyVehicle.objects.get_or_create(
            registration_number='KA-34-M-7705',
            defaults={
                'customer': cust2,
                'vehicle_type': 'TIPPER',
                'make': 'Ashok Leyland',
                'model_name': '3520-8x4 Heavy Mining Tipper',
                'manufacture_year': 2023,
                'chassis_number': 'MAL3520A8H738291',
                'engine_number': 'A-SERIES-BS6-200HP',
                'odometer_reading': 43200,
                'fuel_type': 'DIESEL',
                'gross_vehicle_weight': '35 Tonnes'
            }
        )

        v4, _ = HeavyVehicle.objects.get_or_create(
            registration_number='KL-07-CD-5050',
            defaults={
                'customer': cust1,
                'vehicle_type': 'BUS',
                'make': 'Volvo',
                'model_name': '9400 B11R Multi-Axle Coach',
                'manufacture_year': 2022,
                'chassis_number': 'YV3B11R00NA837261',
                'engine_number': 'VOLVO-D11K-430',
                'odometer_reading': 210000,
                'fuel_type': 'DIESEL',
                'gross_vehicle_weight': '22 Tonnes'
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ Heavy Commercial Vehicles registered."))

        # 3. Inventory Spare Parts
        parts_data = [
            ('FL-ENG-092', 'Cummins Heavy Diesel Fuel Filter (Primary)', 'FILTERS_LUBES', 2850.00, 1900.00, 24, 6, 'PCS', 'Bay A-1', 'FleetGuard India'),
            ('BRK-AIR-44', 'Heavy-Duty Pneumatic Brake Shoe Set (4-Axle)', 'BRAKES', 8500.00, 5800.00, 12, 4, 'SET', 'Bay B-3', 'WABCO Automotive'),
            ('TRB-VGT-18', 'Holset VGT Turbocharger Assembly', 'ENGINE', 42000.00, 31000.00, 3, 2, 'PCS', 'Bay A-4', 'Cummins Technologies'),
            ('SUS-BEL-01', 'Commercial Air Suspension Bellow (Firestone Type)', 'SUSPENSION', 6400.00, 4200.00, 18, 5, 'PCS', 'Bay C-2', 'Firestone Industrial'),
            ('HYD-TIP-90', 'Telescopic Tipper Cylinder Seal & O-Ring Kit', 'HYDRAULICS', 7200.00, 4500.00, 8, 3, 'SET', 'Bay D-1', 'Hyva Hydraulics'),
            ('ALT-24V-80', 'Heavy Commercial 24V 80A Alternator', 'ELECTRICAL', 14500.00, 9800.00, 5, 2, 'PCS', 'Bay E-2', 'Bosch Heavy Mobility'),
            ('OIL-15W40', 'Mobil Delvac Super 15W-40 Heavy Duty Diesel Oil', 'FILTERS_LUBES', 480.00, 340.00, 150, 30, 'Liters', 'Drum Yard', 'ExxonMobil'),
            ('CLU-430-PL', '430mm Heavy Pull-Type Clutch Disc & Pressure Plate', 'TRANSMISSION', 22500.00, 16000.00, 4, 2, 'SET', 'Bay B-1', 'Valeo Friction'),
        ]

        for pno, name, cat, price, cost, qty, reorder, uom, rack, supp in parts_data:
            SparePart.objects.get_or_create(
                part_number=pno,
                defaults={
                    'name': name,
                    'category': cat,
                    'unit_price': Decimal(str(price)),
                    'cost_price': Decimal(str(cost)),
                    'quantity_in_stock': qty,
                    'reorder_threshold': reorder,
                    'unit_of_measure': uom,
                    'rack_location': rack,
                    'supplier_name': supp,
                }
            )
        self.stdout.write(self.style.SUCCESS("✓ Spare parts stock loaded into inventory."))

        # 4. Service Requests & Job Cards
        # Request 1: Emergency Breakdown (InProgress)
        req1, _ = ServiceRequest.objects.get_or_create(
            request_number='REQ-2026-0001',
            defaults={
                'customer': cust1,
                'vehicle': v1,
                'service_type': 'BREAKDOWN',
                'priority': 'CRITICAL',
                'status': 'IN_PROGRESS',
                'description': 'Engine power loss and black exhaust smoke stranded on National Highway 44 near Toll Plaza. Boost pressure sensor alert.',
                'breakdown_location': 'NH 44, Mile Marker 182, near Nelamangala Toll',
                'preferred_date': timezone.now().date(),
                'assigned_mechanic': mech1,
            }
        )

        jc1, _ = JobCard.objects.get_or_create(
            job_card_number='JC-2026-0001',
            defaults={
                'service_request': req1,
                'assigned_mechanic': mech1,
                'assigned_by': admin_user,
                'status': 'IN_PROGRESS',
                'meter_reading_in': 148500,
                'estimated_completion': timezone.now() + timezone.timedelta(days=1),
                'diagnosis_findings': 'ECU error code 234: High turbo manifold boost leakage. Split intercooler air hose and blocked primary diesel filter.',
                'work_performed_summary': 'Replaced ruptured silicone booster elbow hose. Flushed high-pressure fuel line and installed new Cummins fuel filter.',
            }
        )

        JobCardTask.objects.get_or_create(job_card=jc1, task_name="Mobile dispatch unit safety cordon & hazard triangles", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc1, task_name="OBD-II commercial vehicle ECU error code diagnosis", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc1, task_name="Replace damaged turbo boost intake pipe & seals", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc1, task_name="Install replacement diesel filter and bleed fuel system", defaults={'is_completed': False})

        MechanicWorkLog.objects.get_or_create(
            job_card=jc1,
            activity_title="Emergency roadside diagnosis & boost leak detection",
            defaults={'mechanic': mech1, 'work_details': 'Traveled 28km with mobile unit. Located high-pressure split in intercooler boot. Clamped and prepared fuel filter exchange.', 'hours_spent': Decimal('3.5')}
        )

        fuel_filter = SparePart.objects.get(part_number='FL-ENG-092')
        JobCardPartUsage.objects.get_or_create(
            job_card=jc1,
            part=fuel_filter,
            defaults={'quantity': 2, 'unit_price': fuel_filter.unit_price, 'issued_by': mech1}
        )

        # Request 2: Completed Service with Invoice, Payment and Feedback
        req2, _ = ServiceRequest.objects.get_or_create(
            request_number='REQ-2026-0002',
            defaults={
                'customer': cust2,
                'vehicle': v3,
                'service_type': 'HYDRAULIC',
                'priority': 'HIGH',
                'status': 'COMPLETED',
                'description': 'Tipper body slowly drifting down when fully raised with 30 ton iron ore load. Hydraulic pump leaking at PTO shaft seal.',
                'preferred_date': timezone.now().date() - timezone.timedelta(days=3),
                'assigned_mechanic': mech2,
            }
        )

        jc2, _ = JobCard.objects.get_or_create(
            job_card_number='JC-2026-0002',
            defaults={
                'service_request': req2,
                'assigned_mechanic': mech2,
                'assigned_by': admin_user,
                'status': 'CLOSED',
                'meter_reading_in': 43200,
                'meter_reading_out': 43215,
                'estimated_completion': timezone.now() - timezone.timedelta(days=2),
                'actual_completion': timezone.now() - timezone.timedelta(days=2),
                'diagnosis_findings': 'Worn cylinder rod wipers and cracked main seal in the Hyva tipping ram. Hydraulic fluid contaminated with quarry dust.',
                'work_performed_summary': 'Disassembled 5-stage telescopic hydraulic cylinder. Polished hard chrome ram stages. Replaced complete seal kit and refilled 45L high-viscosity hydraulic fluid. Pressure tested to 190 bar under full payload.',
            }
        )

        JobCardTask.objects.get_or_create(job_card=jc2, task_name="Drain hydraulic fluid reservoir and inspect sediment magnet", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc2, task_name="Dismantle telescopic tipper cylinder and hone gland nuts", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc2, task_name="Fit new Hyva high-pressure polyurethane seal kit", defaults={'is_completed': True, 'completed_at': timezone.now()})
        JobCardTask.objects.get_or_create(job_card=jc2, task_name="Full payload dump lift test & 190 bar pressure certification", defaults={'is_completed': True, 'completed_at': timezone.now()})

        MechanicWorkLog.objects.get_or_create(
            job_card=jc2,
            activity_title="Complete tipper ram overhaul & seal replacement",
            defaults={'mechanic': mech2, 'work_details': 'Cleaned and rebushed mounting trunnions. Rebuilt cylinder assembly with zero hydraulic drift after 30 min hold test.', 'hours_spent': Decimal('6.0')}
        )

        hyd_part = SparePart.objects.get(part_number='HYD-TIP-90')
        JobCardPartUsage.objects.get_or_create(
            job_card=jc2,
            part=hyd_part,
            defaults={'quantity': 1, 'unit_price': hyd_part.unit_price, 'issued_by': mech2}
        )

        # Invoice for JC2
        inv2, _ = Invoice.objects.get_or_create(
            invoice_number='INV-2026-0001',
            defaults={
                'job_card': jc2,
                'customer': cust2,
                'labor_hours': Decimal('6.0'),
                'labor_rate_per_hour': Decimal('650.00'),
                'labor_charges': Decimal('3900.00'),
                'parts_charges': Decimal('7200.00'),
                'roadside_assistance_fee': Decimal('0.00'),
                'discount_amount': Decimal('300.00'),
                'tax_rate': Decimal('18.0'),
                'tax_amount': Decimal('1944.00'),
                'total_amount': Decimal('12744.00'),
                'status': 'PAID',
                'paid_at': timezone.now() - timezone.timedelta(days=1),
                'notes': 'Warranty 6 months on hydraulic cylinder seal packing. Regular fluid level check advised.'
            }
        )

        Payment.objects.get_or_create(
            transaction_id='TXN-HVS98231019',
            defaults={
                'invoice': inv2,
                'payment_method': 'UPI',
                'amount_paid': Decimal('12744.00'),
                'status': 'SUCCESS',
                'payment_date': timezone.now() - timezone.timedelta(days=1),
                'gateway_reference': 'UPI-REF-REDDYMINING-44910'
            }
        )

        CustomerFeedback.objects.get_or_create(
            job_card=jc2,
            defaults={
                'customer': cust2,
                'mechanic': mech2,
                'rating': 5,
                'timeliness_rating': 5,
                'quality_rating': 5,
                'comments': 'Exceptional service! Our Ashok Leyland tipper was repaired and pressure-tested ahead of schedule. Zero hydraulic sag with heavy granite load. Highly recommended workshop!',
            }
        )

        # Request 3: Pending Assignment (for Admin to demonstrate workflow)
        ServiceRequest.objects.get_or_create(
            request_number='REQ-2026-0003',
            defaults={
                'customer': cust1,
                'vehicle': v2,
                'service_type': 'BRAKE_SUSPENSION',
                'priority': 'HIGH',
                'status': 'PENDING',
                'description': 'Air pressure building up very slowly in dual air brake reservoir. Spongy pedal response and air hiss sound near front axle.',
                'preferred_date': timezone.now().date() + timezone.timedelta(days=1),
            }
        )

        self.stdout.write(self.style.SUCCESS("✓ Service requests, Job cards, Work logs, Invoices, Payments & Feedback created!"))
        self.stdout.write(self.style.SUCCESS("=== SEEDING COMPLETE ==="))
        self.stdout.write("Credentials:")
        self.stdout.write("  Admin:     admin / admin123")
        self.stdout.write("  Mechanic:  mechanic_ravi / pass123")
        self.stdout.write("  Mechanic:  mechanic_anil / pass123")
        self.stdout.write("  Customer:  fleet_kiran / pass123")
        self.stdout.write("  Customer:  suresh_tipper / pass123")
