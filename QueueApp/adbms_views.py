"""
ADBMS Showcase Views - Refactored and simplified.
Raw SQL queries, Stored Procedure calls, and Transaction blocks
are consolidated in `QueueApp.queries`.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from QueueApp import queries


def adbms_dashboard(request):
    """Main ADBMS Interactive Dashboard displaying summary aggregates, views, and entity lists.
    Restricted to System Administrators only.
    """
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    context = queries.get_adbms_dashboard_stats()
    return render(request, 'adbms_dashboard.html', context)


def adbms_run_query(request):
    """Phase 3 API: Execute predefined raw MySQL queries (JOIN, Subqueries, HAVING, EXPLAIN)."""
    query_type = request.GET.get('type', 'join')
    result = queries.run_adbms_query(query_type)
    return JsonResponse(result)


def adbms_calc_wait_time(request):
    """Phase 3 API: Execute Stored Function `fn_calculate_estimated_wait_time`."""
    service_id = request.GET.get('service_id', 1)
    result = queries.execute_wait_time_function(service_id)
    return JsonResponse(result)


def adbms_call_next_token_sp(request):
    """Phase 3 API: Execute Stored Procedure `sp_call_next_token` with OUT parameters."""
    staff_id = request.GET.get('staff_id', 1)
    result = queries.execute_call_next_procedure(staff_id)
    return JsonResponse(result)


@csrf_exempt
def adbms_transaction_demo(request):
    """Phase 4 API: Demonstrate ACID Atomicity and automatic ROLLBACK on CHECK violation."""
    mode = request.GET.get('mode', 'commit')
    result = queries.execute_acid_transaction_demo(mode)
    return JsonResponse(result)
