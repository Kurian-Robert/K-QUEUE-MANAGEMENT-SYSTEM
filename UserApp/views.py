from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from UserApp.models import Citizen
from AdminApp.models import Admin, Office, Department, Service
from StaffApp.models import Staff
from QueueApp.models import QueueToken


def home(request):
    # Live queue metrics for landing page counters
    total_waiting = QueueToken.objects.filter(status='Waiting').count()
    total_serving = QueueToken.objects.filter(status='Serving').count()
    total_completed = QueueToken.objects.filter(status='Completed').count()
    total_tokens = QueueToken.objects.count()

    total_offices = Office.objects.count()
    total_departments = Department.objects.count()
    total_services = Service.objects.count()

    # Quick access services and departments
    departments = Department.objects.prefetch_related('service_set').select_related('office').all()
    all_services = Service.objects.all().select_related('department', 'department__office')
    offices_list = Office.objects.all()[:4]

    # Session authentication context
    admin_id = request.session.get('admin_id')
    staff_id = request.session.get('staff_id')
    user_id = request.session.get('user_id')

    admin_obj = Admin.objects.filter(id=admin_id).first() if admin_id else None
    staff_obj = Staff.objects.filter(staff_id=staff_id).first() if staff_id else None
    citizen_obj = Citizen.objects.filter(citizen_id=user_id).first() if user_id else None

    context = {
        'total_waiting': total_waiting,
        'total_serving': total_serving,
        'total_completed': total_completed,
        'total_tokens': total_tokens,
        'total_offices': total_offices,
        'total_departments': total_departments,
        'total_services': total_services,
        'departments': departments,
        'services': all_services,
        'offices_list': offices_list,
        'admin_obj': admin_obj,
        'staff_obj': staff_obj,
        'citizen_obj': citizen_obj,
    }
    return render(request, 'index.html', context)


# USER LOGIN
def user_login(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')

        user = Citizen.objects.filter(email=login_input).first() or Citizen.objects.filter(citizen_name=login_input).first()

        if user and check_password(password, user.password):
            request.session['user_id'] = user.citizen_id
            request.session['username'] = user.citizen_name
            request.session['user_name'] = user.citizen_name
            return redirect('user_dashboard')
        else:
            return render(request, 'user_login.html', {
                'error': 'Invalid Username/Email or Password'
            })

    return render(request, 'user_login.html')


# USER REGISTRATION
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('name') or 'Citizen'
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        phone = request.POST.get('phone')

        Citizen.objects.create(
            citizen_name=username,
            email=email,
            password=password,
            phone=phone
        )

        return redirect('user_login')

    return render(request, 'user_register.html')


# USER DASHBOARD
def user_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('user_login')

    user = Citizen.objects.filter(
        citizen_id=request.session['user_id']
    ).first()

    if not user:
        request.session.flush()
        return redirect('user_login')

    user_tokens = QueueToken.objects.filter(citizen=user).select_related('service', 'service__department', 'service__department__office', 'staff').order_by('-created_at')
    active_tokens = user_tokens.filter(status__in=['Waiting', 'Serving'])
    completed_tokens = user_tokens.filter(status='Completed')

    # Calculate queue position for active tokens
    active_tokens_list = []
    for t in active_tokens:
        ahead = QueueToken.objects.filter(
            service__department=t.service.department,
            status='Waiting',
            created_at__lt=t.created_at
        ).count() if t.status == 'Waiting' else 0
        active_tokens_list.append({
            'token': t,
            'people_ahead': ahead
        })

    latest_active = active_tokens_list[0] if active_tokens_list else None

    return render(request, 'user_dashboard.html', {
        'user': user,
        'user_tokens': user_tokens,
        'active_tokens_list': active_tokens_list,
        'latest_active': latest_active,
        'total_booked': user_tokens.count(),
        'total_active': active_tokens.count(),
        'total_completed': completed_tokens.count()
    })


# FORGOT PASSWORD
def forgot_password(request):
    return render(request, 'forgot_password.html')


# RESET PASSWORD
def reset_password(request):
    return render(request, 'reset_password.html')


# LOGOUT
def user_logout(request):
    request.session.flush()
    return redirect('user_login')