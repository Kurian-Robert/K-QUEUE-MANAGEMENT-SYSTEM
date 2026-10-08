def auth_context(request):
    """
    Global authentication context processor for KQMS.
    Provides safe role IDs and display names across all templates
    without throwing VariableDoesNotExist or SessionStore KeyErrors.
    """
    admin_id = request.session.get('admin_id')
    staff_id = request.session.get('staff_id')
    user_id = request.session.get('user_id')

    return {
        'auth_admin_id': admin_id,
        'auth_admin_name': request.session.get('admin_username') or 'System Admin',
        'auth_staff_id': staff_id,
        'auth_staff_name': request.session.get('staff_name') or request.session.get('staff_username') or 'Staff Officer',
        'auth_user_id': user_id,
        'auth_user_name': request.session.get('user_name') or request.session.get('username') or 'Citizen',
    }
