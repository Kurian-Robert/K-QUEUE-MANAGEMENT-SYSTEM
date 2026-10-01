from django.shortcuts import render, redirect, get_object_or_404
from .models import QueueToken

from UserApp.models import Citizen
from StaffApp.models import Staff
from AdminApp.models import Service


# Generate Token
def generate_token(request):

    if request.method == 'POST':

        citizen_id = request.POST.get('citizen_id')
        service_id = request.POST.get('service_id')

        citizen = get_object_or_404(
            Citizen,
            pk=citizen_id
        )

        service = get_object_or_404(
            Service,
            service_id=service_id
        )

        # Find the last token
        last_token = QueueToken.objects.order_by(
            '-token_id'
        ).first()

        if last_token:
            token_number = str(
                int(last_token.token_number) + 1
            )
        else:
            token_number = '1'

        # Create token
        QueueToken.objects.create(
            citizen=citizen,
            service=service,
            token_number=token_number,
            status='Waiting'
        )

        return redirect('queue_management')

    citizens = Citizen.objects.all()
    services = Service.objects.all()

    return render(
        request,
        'get_token.html',
        {
            'citizens': citizens,
            'services': services
        }
    )


# Display Queue
def queue_management(request):

    tokens = QueueToken.objects.all().order_by(
        'created_at'
    )

    return render(
        request,
        'queue_management.html',
        {
            'tokens': tokens
        }
    )


# Token Status
def token_status(request, token_id):

    token = get_object_or_404(
        QueueToken,
        token_id=token_id
    )

    return render(
        request,
        'token_status.html',
        {
            'token': token
        }
    )


# Call Next Token
def call_next_token(request):

    if request.method == 'POST':

        staff_id = request.POST.get('staff_id')

        staff = get_object_or_404(
            Staff,
            pk=staff_id
        )

        # Find first waiting token
        token = QueueToken.objects.filter(
            status='Waiting'
        ).order_by(
            'created_at'
        ).first()

        if token:
            token.staff = staff
            token.status = 'Serving'
            token.save()

        return redirect('queue_management')

    staff = Staff.objects.all()

    return render(
        request,
        'call_next_token.html',
        {
            'staff': staff
        }
    )


# Complete Token
def complete_token(request, token_id):

    token = get_object_or_404(
        QueueToken,
        token_id=token_id
    )

    token.status = 'Completed'
    token.save()

    return redirect('queue_management')
