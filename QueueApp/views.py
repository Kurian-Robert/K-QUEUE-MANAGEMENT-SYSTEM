import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from .models import QueueToken, Feedback

from UserApp.models import Citizen
from StaffApp.models import Staff
from AdminApp.models import Service, Department, Office


# Generate Token
def generate_token(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id') or request.POST.get('service') or request.GET.get('service_id')
        citizen_id = request.POST.get('citizen_id')
        applicant_name = request.POST.get('applicant_name', '').strip()
        applicant_phone = request.POST.get('applicant_phone', '').strip()

        # 1. Resolve Service safely (never hard crash to 404)
        service = None
        if service_id and str(service_id).strip().isdigit():
            service = Service.objects.filter(service_id=int(service_id)).select_related('department', 'department__office').first()

        if not service and service_id:
            service = Service.objects.filter(service_name__icontains=str(service_id).strip()).first()

        if not service:
            service = Service.objects.first()

        if not service:
            return render(request, 'get_token.html', {
                'error': 'No public services are currently available. Please contact administrator.',
                'citizens': Citizen.objects.all(),
                'departments': Department.objects.prefetch_related('service_set').select_related('office').all(),
                'services': Service.objects.all().select_related('department', 'department__office'),
            })

        # 2. Resolve Citizen (Logged-in citizen, Walk-in entry, or Selected profile)
        citizen = None
        session_user_id = request.session.get('user_id')

        # Case A: User is already logged into citizen portal
        if session_user_id and str(session_user_id).isdigit():
            citizen = Citizen.objects.filter(citizen_id=int(session_user_id)).first()

        # Case B: Walk-in applicant entered Name and/or Phone
        if not citizen and (applicant_phone or applicant_name):
            clean_phone = re.sub(r'\D', '', applicant_phone)[-10:] if applicant_phone else ""
            clean_name = applicant_name or (f"Citizen {clean_phone[-4:]}" if clean_phone else "Walk-in Citizen")
            
            if clean_phone:
                citizen = Citizen.objects.filter(phone__endswith=clean_phone).first()
            
            if not citizen:
                citizen = Citizen.objects.create(
                    citizen_name=clean_name,
                    phone=applicant_phone or "9847000000",
                    email=f"citizen_{clean_phone or 'guest'}@kqms.kerala.gov.in",
                    password="walk_in_guest"
                )
            
            # Store in session so user can immediately view token in their dashboard
            request.session['user_id'] = citizen.citizen_id
            request.session['user_name'] = citizen.citizen_name

        # Case C: Citizen selected from profile dropdown
        if not citizen and citizen_id and str(citizen_id).strip().isdigit():
            citizen = Citizen.objects.filter(citizen_id=int(citizen_id)).first()

        # Case D: Safe fallback
        if not citizen:
            citizen = Citizen.objects.first()
            if not citizen:
                citizen = Citizen.objects.create(
                    citizen_name="Walk-in Citizen",
                    phone="9847000000",
                    email="guest@kqms.kerala.gov.in",
                    password="walk_in_guest"
                )

        # 3. Safely generate token number atomically
        with transaction.atomic():
            last_token = QueueToken.objects.select_for_update().order_by('-token_id').first()
            if last_token:
                digits = re.findall(r'\d+', str(last_token.token_number))
                next_num = int(digits[-1]) + 1 if digits else (last_token.token_id + 1)
                token_number = f"TK-{next_num}"
            else:
                token_number = "TK-101"

            # Create token
            new_token = QueueToken.objects.create(
                citizen=citizen,
                service=service,
                token_number=token_number,
                status='Waiting'
            )

        return redirect('token_status', token_id=new_token.token_id)

    selected_service_id = request.GET.get('service_id')
    selected_dept_id = request.GET.get('dept_id')
    selected_office_id = request.GET.get('office_id')

    citizens = Citizen.objects.all()
    offices = Office.objects.all()
    departments = Department.objects.prefetch_related('service_set').select_related('office').all()
    services = Service.objects.all().select_related('department', 'department__office')

    return render(
        request,
        'get_token.html',
        {
            'citizens': citizens,
            'offices': offices,
            'departments': departments,
            'services': services,
            'selected_service_id': int(selected_service_id) if selected_service_id and selected_service_id.isdigit() else None,
            'selected_dept_id': int(selected_dept_id) if selected_dept_id and selected_dept_id.isdigit() else None,
            'selected_office_id': int(selected_office_id) if selected_office_id and selected_office_id.isdigit() else None,
        }
    )


# Display Queue
def queue_management(request):

    tokens = QueueToken.objects.all().select_related('citizen', 'service', 'staff').order_by('-created_at')
    current_token = tokens.filter(status='Serving').first() or tokens.filter(status='Waiting').first()
    waiting_count = tokens.filter(status='Waiting').count()
    completed_count = tokens.filter(status='Completed').count()

    return render(
        request,
        'queue_management.html',
        {
            'tokens': tokens,
            'current_token': current_token,
            'waiting_count': waiting_count,
            'completed_count': completed_count
        }
    )


# Token Status & Live Tracking
def token_status(request, token_id):
    token = get_object_or_404(
        QueueToken.objects.select_related('citizen', 'service', 'service__department', 'service__department__office', 'staff'),
        token_id=token_id
    )

    if request.method == 'POST' and request.POST.get('action') == 'submit_feedback':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '')
        if rating and rating.isdigit():
            Feedback.objects.update_or_create(
                token=token,
                defaults={
                    'citizen': token.citizen,
                    'rating': int(rating),
                    'comments': comments.strip()
                }
            )
        return redirect('token_status', token_id=token.token_id)

    # Calculate real-time queue position for this token's department
    people_ahead = 0
    if token.status == 'Waiting':
        people_ahead = QueueToken.objects.filter(
            service__department=token.service.department,
            status='Waiting',
            created_at__lt=token.created_at
        ).count()

    current_serving = QueueToken.objects.filter(
        service__department=token.service.department,
        status='Serving'
    ).first()

    feedback_obj = Feedback.objects.filter(token=token).first()

    return render(
        request,
        'token_status.html',
        {
            'token': token,
            'people_ahead': people_ahead,
            'current_serving': current_serving,
            'feedback': feedback_obj
        }
    )


# Fast Token Tracker Search from Home Page
def track_token_redirect(request):
    query = request.GET.get('q', '').strip()
    if query:
        if query.isdigit():
            token = QueueToken.objects.filter(token_id=int(query)).first()
        else:
            token = QueueToken.objects.filter(token_number__iexact=query).first()
            if not token:
                import re
                nums = re.findall(r'\d+', query)
                if nums:
                    token = QueueToken.objects.filter(token_number__icontains=nums[-1]).first() or QueueToken.objects.filter(token_id=int(nums[-1])).first()
        if token:
            return redirect('token_status', token_id=token.token_id)
    return redirect('queue_management')


