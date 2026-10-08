from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Staff
from AdminApp.models import Department
from QueueApp.models import QueueToken


def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        staff = Staff.objects.filter(staff_name=username).first()

        if staff:
            request.session['staff_id'] = staff.staff_id
            request.session['staff_username'] = staff.staff_name
            request.session['staff_name'] = staff.staff_name
            return redirect('staff_dashboard')
        else:
            return render(request, 'staff_login.html', {
                'error': 'Staff member not found. Try one of the seeded staff names.'
            })

    return render(request, 'staff_login.html')


def staff_register(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        designation = request.POST.get('designation') or 'Staff Officer'
        department_id = request.POST.get('department')

        department = None
        if department_id and str(department_id).strip().isdigit():
            department = Department.objects.filter(department_id=int(department_id)).first()

        if not department:
            department = Department.objects.first()

        Staff.objects.create(
            staff_name=username,
            role=designation,
            department=department
        )

        return redirect('staff_login')
    return render(request, 'staff_register.html', {
        'departments': departments
    })


def staff_dashboard(request):
    if 'staff_id' not in request.session:
        # Fallback to first staff for smooth demo if direct URL visited
        first_staff = Staff.objects.first()
        if first_staff:
            request.session['staff_id'] = first_staff.staff_id
            request.session['staff_username'] = first_staff.staff_name
            request.session['staff_name'] = first_staff.staff_name
        else:
            return redirect('staff_login')

    staff = Staff.objects.select_related('department').get(staff_id=request.session['staff_id'])

    # Currently serving token for this staff counter
    current_serving = QueueToken.objects.filter(
        staff=staff,
        status='Serving'
    ).select_related('citizen', 'service').first()

    # Live queue of waiting tokens for this staff member's department
    department_queue = QueueToken.objects.filter(
        service__department=staff.department,
        status='Waiting'
    ).select_related('citizen', 'service').order_by('created_at')

    # Completed tokens today by this staff
    completed_tokens = QueueToken.objects.filter(
        staff=staff,
        status='Completed'
    ).select_related('citizen', 'service').order_by('-created_at')[:8]

    # Metrics
    today_served_count = QueueToken.objects.filter(staff=staff, status='Completed').count()
    dept_pending_count = department_queue.count()

    context = {
        'staff': staff,
        'current_serving': current_serving,
        'department_queue': department_queue,
        'completed_tokens': completed_tokens,
        'today_served_count': today_served_count,
        'dept_pending_count': dept_pending_count,
    }
    return render(request, 'staff_dashboard.html', context)


def staff_call_next(request):
    """Call next waiting token for staff's department atomically"""
    if 'staff_id' not in request.session:
        return redirect('/staff/login')

    staff = get_object_or_404(Staff, staff_id=request.session['staff_id'])

    # Atomic fetch of next waiting token
    with transaction.atomic():
        next_token = QueueToken.objects.select_for_update().filter(
            service__department=staff.department,
            status='Waiting'
        ).order_by('created_at').first()

        if next_token:
            next_token.staff = staff
            next_token.status = 'Serving'
            next_token.save()

    return redirect('/staff/dashboard/')


def staff_start_service(request, token_id):
    """Start serving a specific token"""
    if 'staff_id' not in request.session:
        return redirect('/staff/login')

    staff = get_object_or_404(Staff, staff_id=request.session['staff_id'])
    token = get_object_or_404(QueueToken, token_id=token_id)

    token.staff = staff
    token.status = 'Serving'
    token.save()

    return redirect('/staff/dashboard/')


def staff_complete_token(request, token_id):
    """Mark serving token as completed"""
    token = get_object_or_404(QueueToken, token_id=token_id)
    token.status = 'Completed'
    token.save()

    return redirect('/staff/dashboard/')


def staff_token_action(request, token_id):
    """Handle Skip, Re-queue, or Cancel for a token"""
    action = request.POST.get('action', 'requeue')
    token = get_object_or_404(QueueToken, token_id=token_id)

    if action == 'cancel':
        token.status = 'Cancelled'
    else: # requeue / skip
        token.status = 'Waiting'
        token.staff = None
    token.save()

    return redirect('/staff/dashboard/')


def staff_logout(request):
    request.session.flush()
    return redirect('/staff/login')
