from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from AdminApp.models import Admin, Department



def admin_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = Admin.objects.get(username=username)

            if check_password(password, admin.password):

                request.session["admin_id"] = admin.id

                return redirect("/system_admin/dashboard/")

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
        return redirect("/system_admin/login/")
    return render(
        request,
        "admin_dashboard.html"
    )


def add_department(request):
    if request.method == 'POST':
        department_name = request.POST.get(
            'department_name'
        )

        department_description = request.POST.get(
            'department_description'
        )

        department_location = request.POST.get(
            'department_location'
        )

        Department.objects.create(
            department_name=department_name,
            department_description=department_description,
            department_location=department_location
        )

        return redirect('view_departments')

    return render(
        request,
        'add_department.html'
    )


def forgot_password(request):
    return render(
        request,
        'forgot_password.html'
    )


def reset_password(request):
    return render(
        request,
        'reset_password.html'
    )


def admin_logout(request):
    request.session.flush()
    return redirect("/system_admin/login/")