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

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Admin
    path('admin/', admin.site.urls),
    path('system_admin/login/', admin_views.admin_login, name='admin_login'),
    path('system_admin/register/', admin_views.admin_register, name='admin_register'),
    path('system_admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('forgot-password/', user_views.forgot_password, name='forgot_password'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('system_admin/logout/', admin_views.admin_logout, name='admin_logout'),
    #Staff
    path('staff/login/', staff_views.staff_login, name='staff_login'),
    path('staff/register/', staff_views.staff_register, name='staff_register'),
    path('staff/dashboard/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('forgot-password/', staff_views.forgot_password, name='forgot_password'),
    path('reset-password/', staff_views.reset_password, name='reset_password'),
    path('staff/logout/', staff_views.staff_logout, name='staff_logout'),
    #User
    path('',user_views.home,name='index_page'),
    path('user/login', user_views.user_login, name='user_login'),
    path('user/register/', user_views.user_register, name='user_register'),
    path('user/dashboard/', user_views.user_dashboard, name='user_dashboard'),
    path('forgot-password/', user_views.forgot_password, name='forgot_password'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('user/logout/', user_views.user_logout, name='user_logout'),
    #Queue
    path('get-token/', queue_views.generate_token, name='generate_token'),
    path('management/', queue_views.queue_management, name='queue_management'),
    path('token/<int:token_id>/', queue_views.token_status, name='token_status'),
    path('call-next/', queue_views.call_next_token, name='call_next_token'),
    path('token/<int:token_id>/complete/', queue_views.complete_token, name='complete_token'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
