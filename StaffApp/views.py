from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import Staff
from AdminApp.models import Department

def staff_login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            staff = Staff.objects.get(username=username)

            if check_password(password, staff.password):
                request.session['staff_id'] = staff.id
                request.session['staff_username'] = staff.username

                return redirect('/staff/dashboard')

            else:
                return render(request, 'staff_login.html', {
                    'error': 'Invalid Password'
                })

        except Staff.DoesNotExist:
            return render(request, 'staff_login.html', {
                'error': 'Invalid Username'
            })

    return render(request, 'staff_login.html')


def staff_register(request):

    departments = Department.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        phone = request.POST.get('phone')
        designation = request.POST.get('designation')
        department_id = request.POST.get('department')
        picture = request.FILES.get('picture')

        department = Department.objects.get(id=department_id)

        Staff.objects.create(
            username=username,
            email=email,
            password=password,
            phone=phone,
            designation=designation,
            department=department,
            picture=picture
        )

        return redirect('/staff/login')
    return render(request, 'staff_register.html', {
        'departments': departments
    })


def staff_dashboard(request):

    if 'staff_id' not in request.session:
        return redirect('/staff/login')

    staff = Staff.objects.get(id=request.session['staff_id'])

    return render(request, 'staff_dashboard.html', {
        'staff': staff
    })


def forgot_password(request):
    # Verify the staff's email
    return render(request, 'forgot_password.html')

def reset_password(request):
    # Update the staff's password
    return render(request, 'reset_password.html')

def staff_logout(request):
    request.session.flush()
    return redirect('/staff/login')
