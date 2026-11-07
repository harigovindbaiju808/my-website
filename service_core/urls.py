from django.urls import path
from . import views

urlpatterns = [
    # Module 1: Auth & Dashboards
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/mechanic/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),

    # Module 2: Heavy Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),

    # Module 3: Service Requests
    path('services/', views.service_request_list, name='service_request_list'),
    path('services/book/', views.service_request_create, name='service_request_create'),
    path('services/<int:pk>/', views.service_request_detail, name='service_request_detail'),
    path('services/<int:pk>/assign/', views.service_request_assign, name='service_request_assign'),

    # Module 4 & 5: Job Cards & Mechanic Work Tracking
    path('jobcards/', views.jobcard_list, name='jobcard_list'),
    path('jobcards/<int:pk>/', views.jobcard_detail, name='jobcard_detail'),
    path('jobcards/<int:pk>/update/', views.jobcard_update, name='jobcard_update'),
    path('jobcards/<int:pk>/tasks/add/', views.jobcard_add_task, name='jobcard_add_task'),
    path('jobcards/<int:pk>/tasks/<int:task_id>/toggle/', views.jobcard_toggle_task, name='jobcard_toggle_task'),
    path('jobcards/<int:pk>/worklogs/add/', views.jobcard_add_worklog, name='jobcard_add_worklog'),
    path('jobcards/<int:pk>/parts/issue/', views.jobcard_issue_part, name='jobcard_issue_part'),

    # Module 6: Spare Parts & Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.part_create, name='part_create'),
    path('inventory/<int:pk>/edit/', views.part_update, name='part_update'),

    # Module 7: Billing & Payment Management
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/generate/<int:job_card_id>/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/pay/', views.process_payment, name='process_payment'),

    # Module 8: Feedback & Reporting System
    path('jobcards/<int:job_card_id>/feedback/', views.feedback_create, name='feedback_create'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
]
