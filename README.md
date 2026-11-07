# Heavy Vehicle Repair and Service Management System

**Student Name:** HARIGOVIND P B  
**Register Number:** CCE25CD032  
**Topic:** Heavy Vehicle Repair and Service Management  
**Framework:** Django (Python Web Framework) & Bootstrap 5  

---

## 📋 Project Overview

The **Heavy Vehicle Repair and Service Management System** is an enterprise-grade, web-based platform tailored specifically for commercial vehicle workshops, logistics fleet operators, and heavy machinery owners (multi-axle trucks, tippers, trailers, commercial passenger buses, and mobile rigs).

It streamlines the complete lifecycle of heavy vehicle maintenance:
- **Intake & Diagnostics:** Vehicle registration, odometer logs, and roadside breakdown reporting.
- **Workshop Dispatch:** Intelligent job card creation with checklist-based inspections and technician allocation.
- **Inventory & Billing:** Real-time OEM spare parts deduction, labor tracking, automated 18% GST invoice generation, and simulated online payments.
- **Quality Assurance & Telemetry:** 5-star customer feedback loops, technician productivity reports, and operational analytics dashboards.

---

## 🚀 Key Modules Implemented

The system implements all **8 core modules** outlined in the project specification:

### 1. User Registration & Authentication (Role-Based Access Control)
- Multi-role permission system:
  - **Administrator / Workshop Manager (`ADMIN`)**: Full oversight of bays, mechanic assignment, inventory, billing, and reports.
  - **Service Mechanic / Technician (`MECHANIC`)**: Access to assigned job cards, technical checklist items, labor hour logging, and parts requisition.
  - **Vehicle Owner / Fleet Manager (`CUSTOMER`)**: Vehicle registration, service booking, live repair timeline tracking, and invoice payments.
- Role-specific login redirects and protected view decorators (`@admin_required`, `@mechanic_required`, `@customer_required`).

### 2. Vehicle & Customer Management
- Complete registry of heavy commercial vehicles:
  - Category types: Multi-Axle Cargo Trucks, Heavy Tippers, Prime Movers & Semi-Trailers, Commercial Buses, Fuel Tankers, Hydraulic Cranes.
  - Tracking of Registration Number, Make, Model, VIN/Chassis Number, Engine Serial, Gross Vehicle Weight (GVW), Fuel Type, and Odometer Mileage.
  - Historical maintenance logs tied to vehicle profile.

### 3. Service Request Management
- Customer service booking for planned preventive maintenance or critical highway breakdowns.
- Roadside emergency location tagging (highway mile markers, site coords).
- Priority classification (`Low`, `Medium`, `High`, `Critical / Breakdown`).
- Admin triage workflow to assign certified mechanics and automatically generate Job Cards.

### 4. Job Card Management
- Unique auto-incrementing Job Card numbers (e.g., `JC-2026-0001`).
- Multi-state lifecycle tracking: `Open` ➔ `In Progress` ➔ `Awaiting Parts` ➔ `Testing & QC` ➔ `Completed` ➔ `Closed & Invoiced`.
- Inspection checklist tasks with completion timestamps.
- Odometer IN and OUT records for road test verification.

### 5. Mechanic Task & Progress Tracking
- Dedicated Mechanic Work Console.
- Interactive checklist to toggle task clearance.
- Activity logging: dedicated labor hours, technical observations, and repair notes.
- Direct spare parts consumption reporting.

### 6. Inventory & Spare Parts Management
- OEM parts catalog categorized by: Engine Components, Pneumatic Brakes, Multi-Leaf Springs & Air Bellows, Clutches & Transmission, Hydraulics, Electrical, and Heavy Lubricants.
- Automatic inventory decrementing when components are issued to a job card.
- Visual low-stock badges and reorder threshold alerts.

### 7. Billing & Payment Management
- Automated invoice computation:
  $$\text{Subtotal} = \text{Parts Total} + (\text{Labor Hours} \times \text{Hourly Rate}) + \text{Breakdown Fee} - \text{Discount}$$
  $$\text{Tax (18\% GST)} = \text{Subtotal} \times 0.18$$
  $$\text{Total Payable} = \text{Subtotal} + \text{Tax}$$
- Printable tax invoice format with GSTIN breakdown and customer details.
- Simulated payment checkout supporting UPI / QR, Commercial Cards, and Net Banking with instant transaction receipts.

### 8. Feedback & Reporting System
- Customer feedback submissions with star ratings (1–5 stars) on overall experience, repair quality, and turnaround timeliness.
- Executive analytics dashboard featuring:
  - Revenue stream breakdown (Chart.js doughnut chart: parts vs. labor vs. taxes).
  - Job card lifecycle distribution (Chart.js bar chart).
  - Technician productivity and average customer ratings.
  - Top consumed spare parts list.

---

## 🔑 Pre-Configured Demo Accounts (Ready to Test)

The project includes a database seeding command that populates realistic demo accounts, heavy vehicles, inventory parts, active job cards, and invoices.

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full workshop control, assignment, billing, and reports |
| **Lead Mechanic** | `mechanic_ravi` | `pass123` | Diesel Engine & Turbo Specialist |
| **Specialist Mechanic** | `mechanic_anil` | `pass123` | Pneumatic Brakes & Hydraulics Specialist |
| **Fleet Owner (Surat)** | `fleet_kiran` | `pass123` | Fleet manager with 50+ logistics vehicles |
| **Mining Fleet Owner** | `suresh_tipper` | `pass123` | Mining tipper operator |

*(The login screen also features 1-click autofill buttons for these accounts).*

---

## 🛠️ Installation & Setup Instructions

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed on your machine.
- `pip` package manager.
- Git.

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd django-project-harigovind
```

### 2. Create and Activate Virtual Environment
- **On Windows (PowerShell / Command Prompt):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Seed Initial Demo Data
```bash
python manage.py seed_data
```

### 6. Launch the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your web browser.

---

## 📤 Submission Steps via GitHub

As specified in the project submission instructions:

1. **Step 1:** Create a GitHub account at [github.com](https://github.com) if you do not have one.
2. **Step 2:** Create a new public repository and name it:
   ```
   django-project-harigovind
   ```
3. **Step 3:** Push the complete Django project code to your repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Heavy Vehicle Repair & Service Management System"
   git branch -M main
   git remote add origin https://github.com/<your-username>/django-project-harigovind.git
   git push -u origin main
   ```
4. **Step 4:** Navigate to your GitHub repository ➔ **Settings** ➔ **Collaborators** ➔ click **"Add people"**.
5. **Step 5:** Search for username: **`Ziuke@1905`** and click **"Add collaborator"**.
6. **Step 6:** Submit your GitHub repository URL before the deadline.

---

## 🏛️ Project Directory Structure

```text
django-project-harigovind/
│
├── manage.py                          # Django management CLI utility
├── requirements.txt                   # Project Python dependencies
├── .gitignore                         # Git exclusion rules
├── README.md                          # Project documentation & submission guide
│
├── heavy_vehicle_service/             # Project Configuration Root
│   ├── __init__.py
│   ├── settings.py                    # Django configuration (Auth, DB, Apps, Templates)
│   ├── urls.py                        # Project root URL dispatcher
│   ├── wsgi.py                        # WSGI entrypoint for web servers
│   └── asgi.py                        # ASGI entrypoint
│
├── service_core/                      # Core Heavy Vehicle Application
│   ├── __init__.py
│   ├── apps.py                        # App configuration
│   ├── models.py                      # 8 Core Modules Data Models
│   ├── forms.py                       # User, Vehicle, Request, JobCard, Invoice & Payment Forms
│   ├── views.py                       # Business logic, state transitions, views
│   ├── urls.py                        # App URL routes
│   ├── admin.py                       # Django Admin customization
│   ├── decorators.py                  # RBAC access control decorators
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py            # Initial database schema migration
│   └── management/
│       └── commands/
│           ├── __init__.py
│           └── seed_data.py           # Evaluator demo data seeder command
│
├── static/
│   └── css/
│       └── custom.css                 # Custom styles for heavy vehicle themes
│
└── templates/                         # Responsive Bootstrap 5 HTML Templates
    ├── base.html                      # Master layout with role-based navbar & footer
    ├── home.html                      # System landing page & 8 modules overview
    ├── auth/
    │   ├── login.html                 # Sign-in with quick autofill demo buttons
    │   └── register.html              # Multi-role account registration
    ├── dashboards/
    │   ├── admin_dashboard.html       # Master workshop console
    │   ├── mechanic_dashboard.html    # Mechanic task & hours console
    │   └── customer_dashboard.html    # Fleet owner service tracking & bill pay
    ├── vehicles/
    │   ├── vehicle_list.html          # Heavy vehicle fleet records
    │   ├── vehicle_form.html          # Vehicle registration form
    │   └── vehicle_detail.html        # Specs & maintenance history
    ├── services/
    │   ├── service_request_list.html  # Intake requests
    │   ├── service_request_form.html  # Book service or report breakdown
    │   ├── service_request_detail.html# Request status & job allocation
    │   └── service_request_assign.html# Admin mechanic assignment
    ├── jobcards/
    │   ├── jobcard_list.html          # All workshop job cards
    │   ├── jobcard_detail.html        # Interactive task checklist & parts issued
    │   └── jobcard_form.html          # Update repair status & readings
    ├── inventory/
    │   ├── inventory_list.html        # Spare parts stock & low-stock alerts
    │   └── part_form.html             # Add/edit OEM components
    ├── billing/
    │   ├── invoice_list.html          # Invoices overview
    │   ├── invoice_form.html          # Compute labor + parts + GST
    │   ├── invoice_detail.html        # Official printable tax invoice
    │   └── payment_form.html          # Simulated payment gateway
    ├── feedback/
    │   ├── feedback_list.html         # Customer reviews showcase
    │   └── feedback_form.html         # 5-star rating submission
    └── reports/
        └── reports_dashboard.html     # Financial & productivity analytics with Chart.js
```

---

**Developed by:** HARIGOVIND P B  
**Register No:** CCE25CD032  
**Course:** Heavy Vehicle Repair and Service Management System
