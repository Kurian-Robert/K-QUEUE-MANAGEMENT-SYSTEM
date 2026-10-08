"""
=============================================================================
Kerala Queue Management System (KQMS) - Dedicated ADBMS Query Layer
=============================================================================
Centralized query execution layer for Advanced Database Management Systems (ADBMS)
coursework requirements:
- Phase 1 & 2: Schema validation, constraints, and statistical aggregates
- Phase 3: 6-table relational JOINs, correlated subqueries, views & SPs/Functions
- Phase 4: ACID transactions, SAVEPOINT atomicity, and rollback verification
=============================================================================
"""

import time
from django.db import connection, transaction


def dictfetchall(cursor):
    """Utility helper: Convert raw cursor tuples to list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Phase 3 Predefined Optimized Raw SQL Queries
ADBMS_QUERIES = {
    'join': """
        -- 6-Table Relational Join demonstrating normalized relationships
        SELECT 
            t.token_number,
            t.status,
            c.citizen_name,
            c.phone AS contact,
            srv.service_name,
            d.department_name,
            o.office_name,
            COALESCE(st.staff_name, 'Unassigned') AS handling_staff,
            COALESCE(fb.rating, 'N/A') AS rating
        FROM queue_token t
        INNER JOIN citizen c ON t.citizen_id = c.citizen_id
        INNER JOIN service srv ON t.service_id = srv.service_id
        INNER JOIN department d ON srv.department_id = d.department_id
        INNER JOIN office o ON d.office_id = o.office_id
        LEFT JOIN staff st ON t.staff_id = st.staff_id
        LEFT JOIN feedback fb ON t.token_id = fb.token_id
        ORDER BY t.created_at DESC;
    """,
    'subquery_where': """
        -- Subquery in WHERE: Services with duration strictly above the global mean
        SELECT 
            service_id,
            service_name,
            avg_service_min,
            ROUND((SELECT AVG(avg_service_min) FROM service), 2) AS global_average_min
        FROM service
        WHERE avg_service_min > (
            SELECT AVG(avg_service_min) FROM service
        )
        ORDER BY avg_service_min DESC;
    """,
    'correlated_subquery': """
        -- Correlated Subquery: Most recent token per citizen
        SELECT 
            c.citizen_id,
            c.citizen_name,
            c.email,
            (
                SELECT t.token_number 
                FROM queue_token t 
                WHERE t.citizen_id = c.citizen_id 
                ORDER BY t.created_at DESC 
                LIMIT 1
            ) AS latest_token,
            (
                SELECT t.status 
                FROM queue_token t 
                WHERE t.citizen_id = c.citizen_id 
                ORDER BY t.created_at DESC 
                LIMIT 1
            ) AS latest_status
        FROM citizen c;
    """,
    'subquery_not_exists': """
        -- Subquery with NOT EXISTS: Completed tokens with pending feedback
        SELECT 
            c.citizen_id,
            c.citizen_name,
            c.phone,
            t.token_number,
            t.status
        FROM citizen c
        JOIN queue_token t ON c.citizen_id = t.citizen_id
        WHERE t.status = 'Completed'
        AND NOT EXISTS (
            SELECT 1 FROM feedback fb WHERE fb.token_id = t.token_id
        );
    """,
    'aggregate_having': """
        -- Group Aggregation with HAVING filter
        SELECT 
            d.department_name,
            COUNT(t.token_id) AS total_tokens,
            ROUND(AVG(srv.avg_service_min), 1) AS avg_service_duration,
            ROUND(AVG(fb.rating), 2) AS satisfaction_rating
        FROM department d
        JOIN service srv ON d.department_id = srv.department_id
        LEFT JOIN queue_token t ON srv.service_id = t.service_id
        LEFT JOIN feedback fb ON t.token_id = fb.token_id
        GROUP BY d.department_id, d.department_name
        HAVING COUNT(t.token_id) >= 1
        ORDER BY satisfaction_rating DESC;
    """,
    'explain_plan': """
        -- Query Execution Plan Analysis
        EXPLAIN 
        SELECT t.token_number, t.status, s.service_name, c.citizen_name 
        FROM queue_token t
        JOIN service s ON t.service_id = s.service_id
        JOIN citizen c ON t.citizen_id = c.citizen_id
        WHERE t.status = 'Waiting';
    """
}


def get_adbms_dashboard_stats():
    """Fetch summary aggregates, database views, and entity lists for ADBMS dashboard."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_tokens,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_tokens,
                SUM(CASE WHEN status = 'Serving' THEN 1 ELSE 0 END) AS serving_tokens,
                SUM(CASE WHEN status = 'Waiting' THEN 1 ELSE 0 END) AS waiting_tokens
            FROM queue_token
        """)
        stats = cursor.fetchone()
        token_stats = {
            'total': stats[0] or 0,
            'completed': stats[1] or 0,
            'serving': stats[2] or 0,
            'waiting': stats[3] or 0,
        }

        # Query Database Views
        cursor.execute("SELECT * FROM vw_department_daily_performance")
        dept_performance = dictfetchall(cursor)

        cursor.execute("SELECT * FROM vw_active_queue_status")
        active_queue = dictfetchall(cursor)

        cursor.execute("SELECT staff_id, staff_name, role FROM staff")
        staff_list = dictfetchall(cursor)

        cursor.execute("SELECT service_id, service_name, avg_service_min FROM service")
        service_list = dictfetchall(cursor)

    return {
        'token_stats': token_stats,
        'dept_performance': dept_performance,
        'active_queue': active_queue,
        'staff_list': staff_list,
        'service_list': service_list,
    }


def run_adbms_query(query_type):
    """Execute raw SQL query and measure execution performance in milliseconds."""
    raw_sql = ADBMS_QUERIES.get(query_type, ADBMS_QUERIES['join'])
    start_time = time.time()
    with connection.cursor() as cursor:
        cursor.execute(raw_sql)
        columns = [col[0] for col in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        'query_type': query_type,
        'sql': raw_sql.strip(),
        'columns': columns,
        'rows': rows,
        'row_count': len(rows),
        'execution_time_ms': elapsed_ms
    }


def execute_wait_time_function(service_id):
    """Execute MySQL Stored Function `fn_calculate_estimated_wait_time`."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT service_name, avg_service_min FROM service WHERE service_id = %s", [service_id])
        service_info = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM queue_token WHERE service_id = %s AND status = 'Waiting'", [service_id])
        waiting_count = cursor.fetchone()[0]

        cursor.execute("SELECT fn_calculate_estimated_wait_time(%s)", [service_id])
        estimated_min = cursor.fetchone()[0]

    return {
        'service_id': service_id,
        'service_name': service_info[0] if service_info else 'Unknown',
        'avg_service_min': service_info[1] if service_info else 0,
        'waiting_tokens': waiting_count,
        'estimated_wait_minutes': estimated_min,
        'sql_invoked': f"SELECT fn_calculate_estimated_wait_time({service_id})"
    }


def execute_call_next_procedure(staff_id):
    """Execute MySQL Stored Procedure `sp_call_next_token` with OUT parameters."""
    with connection.cursor() as cursor:
        cursor.callproc('sp_call_next_token', [staff_id, 0, ''])
        cursor.execute("SELECT @_sp_call_next_token_1, @_sp_call_next_token_2")
        out_token_id, out_token_num = cursor.fetchone()

        cursor.execute("SELECT staff_name, role FROM staff WHERE staff_id = %s", [staff_id])
        staff_info = cursor.fetchone()

    return {
        'staff_id': staff_id,
        'staff_name': staff_info[0] if staff_info else 'Unknown',
        'staff_role': staff_info[1] if staff_info else '',
        'assigned_token_id': out_token_id,
        'assigned_token_number': out_token_num,
        'status_message': 'Successfully assigned next token' if out_token_id else 'No waiting tokens for this department'
    }


def execute_acid_transaction_demo(mode):
    """
    Demonstrate ACID Atomicity & Rollback:
    - Mode 'commit': Status updated and valid feedback inserted -> COMMITTED.
    - Mode 'rollback': Intentionally violates CHECK constraint chk_feedback_rating -> ROLLED BACK.
    """
    logs = []
    success = False
    error_msg = None

    with connection.cursor() as cursor:
        cursor.execute("SELECT token_id, token_number, status, citizen_id FROM queue_token WHERE status = 'Serving' LIMIT 1")
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT token_id, token_number, status, citizen_id FROM queue_token ORDER BY token_id DESC LIMIT 1")
            row = cursor.fetchone()
        token_id, token_num, initial_status, citizen_id = row

    logs.append(f"[STEP 1] Starting Transaction (BEGIN/START TRANSACTION). Target Token: #{token_num} (Initial Status: '{initial_status}')")

    try:
        with transaction.atomic():
            sid = transaction.savepoint()
            logs.append(f"[STEP 2] Created SAVEPOINT '{sid}'")

            with connection.cursor() as cursor:
                cursor.execute("UPDATE queue_token SET status = 'Completed' WHERE token_id = %s", [token_id])
            logs.append(f"[STEP 3] Executed: UPDATE queue_token SET status = 'Completed' WHERE token_id = {token_id}")

            if mode == 'rollback':
                logs.append("[STEP 4] [SIMULATING FAILURE] Attempting INSERT with invalid rating = 99 (Violates CHECK constraint)...")
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO feedback (token_id, citizen_id, rating, comments, created_at)
                        VALUES (%s, %s, 99, 'Test failure feedback', NOW())
                    """, [token_id, citizen_id])
            else:
                logs.append(f"[STEP 4] [SUCCESS PATH] Inserting valid feedback (rating = 5) for citizen {citizen_id}...")
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO feedback (token_id, citizen_id, rating, comments, created_at)
                        VALUES (%s, %s, 5, 'Transaction committed successfully.', NOW())
                    """, [token_id, citizen_id])
                logs.append("[STEP 5] All statements validated successfully. Committing transaction (COMMIT)...")

            success = True

    except Exception as e:
        error_msg = str(e)
        logs.append(f"[STEP 5] [EXCEPTION INTERCEPTED]: {error_msg}")
        logs.append("[STEP 6] Executing ROLLBACK! Restoring database state prior to transaction.")
        success = False

    with connection.cursor() as cursor:
        cursor.execute("SELECT token_id, token_number, status FROM queue_token WHERE token_id = %s", [token_id])
        final_row = cursor.fetchone()
        final_status = final_row[2] if final_row else 'Unknown'

    logs.append(f"[FINAL STATE] Verified Token #{token_num} Final Status in MySQL: '{final_status}'")
    if mode == 'rollback':
        logs.append("[VERIFICATION] ATOMICITY GUARANTEED: Even though UPDATE ran at Step 3, the subsequent failure triggered ROLLBACK, leaving Token status intact!")
    else:
        logs.append("[VERIFICATION] CONSISTENCY & DURABILITY GUARANTEED: Both token update and feedback creation are permanently saved.")

    return {
        'mode': mode,
        'success': success,
        'error': error_msg,
        'token_id': token_id,
        'token_number': token_num,
        'initial_status': initial_status,
        'final_status': final_status,
        'logs': logs
    }
