from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from UserApp.models import Citizen


def home(request):
    return render(request, 'index.html')


# USER LOGIN
def user_login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Citizen.objects.get(username=username)

            if check_password(password, user.password):

                # Store logged-in user's details in session
                request.session['user_id'] = user.id
                request.session['username'] = user.username

                return redirect('user_dashboard')

            else:
                return render(request, 'user_login.html', {
                    'error': 'Invalid Password'
                })

        except Citizen.DoesNotExist:
            return render(request, 'user_login.html', {
                'error': 'Invalid Username'
            })

    return render(request, 'user_login.html')


# USER REGISTRATION
def user_register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        picture = request.FILES.get('picture')

        Citizen.objects.create(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address,
            picture=picture
        )

        return redirect('user_login')

    return render(request, 'user_register.html')


# USER DASHBOARD
def user_dashboard(request):

    if 'user_id' not in request.session:
        return redirect('user_login')

    user = Citizen.objects.get(
        id=request.session['user_id']
    )

    return render(request, 'user_dashboard.html', {
        'user': user
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