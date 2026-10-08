"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from AdminApp import views as admin_views
from StaffApp import views as staff_views
from UserApp import views as user_views
from QueueApp import views as queue_views
from QueueApp import adbms_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('system_admin/login/', admin_views.admin_login, name='admin_login'),
    path('system_admin/register/', admin_views.admin_register, name='admin_register'),
    path('system_admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('system_admin/offices/', admin_views.office_management, name='office_management'),
    path('system_admin/services/', admin_views.service_management, name='service_management'),
    path('system_admin/departments/', admin_views.department_management, name='department_management'),
    path('system_admin/staff/', admin_views.staff_management, name='staff_management'),
    path('system_admin/users/', admin_views.user_management, name='user_management'),
    path('system_admin/logout/', admin_views.admin_logout, name='admin_logout'),

    # Staff
    path('staff/login/', staff_views.staff_login, name='staff_login'),
    path('staff/register/', staff_views.staff_register, name='staff_register'),
    path('staff/dashboard/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('staff/call-next/', staff_views.staff_call_next, name='staff_call_next'),
    path('staff/token/<int:token_id>/start/', staff_views.staff_start_service, name='staff_start_service'),
    path('staff/token/<int:token_id>/complete/', staff_views.staff_complete_token, name='staff_complete_token'),
    path('staff/token/<int:token_id>/action/', staff_views.staff_token_action, name='staff_token_action'),
    path('staff/logout/', staff_views.staff_logout, name='staff_logout'),

    # User & Public
    path('', user_views.home, name='index_page'),
    path('user/login', user_views.user_login, name='user_login'),
    path('user/register/', user_views.user_register, name='user_register'),
    path('user/dashboard/', user_views.user_dashboard, name='user_dashboard'),
    path('forgot-password/', user_views.forgot_password, name='forgot_password'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('user/logout/', user_views.user_logout, name='user_logout'),

    # Queue
    path('get-token/', queue_views.generate_token, name='generate_token'),
    path('management/', queue_views.queue_management, name='queue_management'),
    path('token/<int:token_id>/', queue_views.token_status, name='token_status'),
    path('track-token/', queue_views.track_token_redirect, name='track_token_redirect'),

    # ADBMS Coursework Showcase
    path('adbms/dashboard/', adbms_views.adbms_dashboard, name='adbms_dashboard'),
    path('adbms/api/run-query/', adbms_views.adbms_run_query, name='adbms_run_query'),
    path('adbms/api/calc-wait-time/', adbms_views.adbms_calc_wait_time, name='adbms_calc_wait_time'),
    path('adbms/api/call-next-sp/', adbms_views.adbms_call_next_token_sp, name='adbms_call_next_token_sp'),
    path('adbms/api/transaction-demo/', adbms_views.adbms_transaction_demo, name='adbms_transaction_demo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
