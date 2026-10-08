from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from AdminApp.models import Admin, Office, Department, Service
from StaffApp.models import Staff
from UserApp.models import Citizen
from QueueApp.models import QueueToken



def admin_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = Admin.objects.get(username=username)

            if check_password(password, admin.password):

                request.session["admin_id"] = admin.id
                request.session["admin_username"] = admin.username

                return redirect("admin_dashboard")

            else:

                return render(
                    request,
                    "admin_login.html",
                    {
                        "error": "Invalid username or password"
                    }
                )

        except Admin.DoesNotExist:

            return render(
                request,
                "admin_login.html",
                {
                    "error": "Invalid username or password"
                }
            )
    return render(request, "admin_login.html")


def admin_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        # Check username
        if Admin.objects.filter(username=username).exists():

            return render(
                request,
                "admin_register.html",
                {
                    "error": "Username already exists. Please choose another username."
                }
            )

        # Check email
        if Admin.objects.filter(email=email).exists():

            return render(
                request,
                "admin_register.html",
                {
                    "error": "Email already exists. Please use another email."
                }
            )

        # Encrypt password
        password = make_password(password)

        # Create admin
        Admin.objects.create(
            username=username,
            email=email,
            password=password,
            phone=phone
        )

        return redirect("/system_admin/login/")
    return render(request, "admin_register.html")



def admin_dashboard(request):
    if "admin_id" not in request.session:
        admin = Admin.objects.first()
        if admin:
            request.session["admin_id"] = admin.id
            request.session["admin_username"] = admin.username
        else:
            return redirect("admin_login")

    total_citizens = Citizen.objects.count()
    total_staff = Staff.objects.count()
    total_departments = Department.objects.count()
    total_offices = Office.objects.count()
    total_services = Service.objects.count()
    total_tokens = QueueToken.objects.count()
    waiting_tokens = QueueToken.objects.filter(status='Waiting').count()
    serving_tokens = QueueToken.objects.filter(status='Serving').count()
    completed_tokens = QueueToken.objects.filter(status='Completed').count()

    recent_tokens = QueueToken.objects.all().select_related('citizen', 'service', 'staff').order_by('-created_at')[:8]

    context = {
        'total_citizens': total_citizens,
        'total_staff': total_staff,
        'total_departments': total_departments,
        'total_offices': total_offices,
        'total_services': total_services,
        'total_tokens': total_tokens,
        'waiting_tokens': waiting_tokens,
        'serving_tokens': serving_tokens,
        'completed_tokens': completed_tokens,
        'recent_tokens': recent_tokens,
    }
    return render(request, "admin_dashboard.html", context)




def office_management(request):
    if request.method == 'POST':
        office_name = request.POST.get('office_name')
        office_type = request.POST.get('office_type') or 'Taluk Office'
        district = request.POST.get('district') or 'Ernakulam'
        if office_name:
            Office.objects.create(
                office_name=office_name,
                office_type=office_type,
                district=district
            )
        return redirect('office_management')

    offices = Office.objects.all().order_by('office_id')
    return render(request, 'office_management.html', {'offices': offices})


def service_management(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        department_id = request.POST.get('department_id')
        avg_service_min = request.POST.get('avg_service_min') or 15
        
        department = Department.objects.filter(department_id=department_id).first() or Department.objects.first()
        if service_name:
            Service.objects.create(
                service_name=service_name,
                department=department,
                avg_service_min=int(avg_service_min)
            )
        return redirect('service_management')

    services = Service.objects.all().select_related('department').order_by('service_id')
    departments = Department.objects.all()
    return render(request, 'service_management.html', {
        'services': services,
        'departments': departments
    })


def department_management(request):
    if request.method == 'POST':
        department_name = request.POST.get('department_name')
        office_id = request.POST.get('office_id')
        office = Office.objects.filter(office_id=office_id).first() or Office.objects.first()
        if department_name:
            Department.objects.create(
                department_name=department_name,
                office=office
            )
        return redirect('department_management')

    departments = Department.objects.all().select_related('office').order_by('department_id')
    offices = Office.objects.all()
    return render(request, 'department_management.html', {
        'departments': departments,
        'offices': offices
    })




def admin_logout(request):
    request.session.flush()
    return redirect("/system_admin/login/")


def staff_management(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'add':
            staff_name = request.POST.get('staff_name')
            role = request.POST.get('role') or 'Counter 1 - Staff'
            department_id = request.POST.get('department_id')
            dept = Department.objects.filter(department_id=department_id).first() or Department.objects.first()
            if staff_name:
                Staff.objects.create(
                    staff_name=staff_name.strip()[:60],
                    role=role.strip()[:30],
                    department=dept
                )
        elif action == 'edit':
            staff_id = request.POST.get('staff_id')
            staff_obj = Staff.objects.filter(staff_id=staff_id).first()
            if staff_obj:
                new_name = request.POST.get('staff_name')
                new_role = request.POST.get('role')
                dept_id = request.POST.get('department_id')
                if new_name:
                    staff_obj.staff_name = new_name.strip()[:60]
                if new_role:
                    staff_obj.role = new_role.strip()[:30]
                if dept_id:
                    dept = Department.objects.filter(department_id=dept_id).first()
                    if dept:
                        staff_obj.department = dept
                staff_obj.save()
        elif action == 'toggle_status':
            staff_id = request.POST.get('staff_id')
            staff_obj = Staff.objects.filter(staff_id=staff_id).first()
            if staff_obj:
                if staff_obj.role.startswith('[OFF] '):
                    staff_obj.role = staff_obj.role.replace('[OFF] ', '').strip()
                else:
                    base_role = staff_obj.role[:24]
                    staff_obj.role = f"[OFF] {base_role}"
                staff_obj.save()
        elif action == 'delete':
            staff_id = request.POST.get('staff_id')
            Staff.objects.filter(staff_id=staff_id).delete()

        return redirect('staff_management')

    query = request.GET.get('q', '').strip()
    staff_members = Staff.objects.all().select_related('department').order_by('staff_id')
    if query:
        from django.db.models import Q
        staff_members = staff_members.filter(
            Q(staff_name__icontains=query) |
            Q(role__icontains=query) |
            Q(department__department_name__icontains=query)
        )

    departments = Department.objects.all().order_by('department_name')
    return render(request, 'staff_management.html', {
        'staff_members': staff_members,
        'departments': departments,
        'query': query
    })


def user_management(request):
    citizens = Citizen.objects.all().order_by('citizen_id')
    return render(request, 'user_management.html', {
        'citizens': citizens
    })