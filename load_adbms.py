import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.db import connection

def apply_adbms_setup():
    with connection.cursor() as cursor:
        print("1. Applying Check Constraints...")
        for drop_sql in [
            "ALTER TABLE service DROP CHECK chk_service_avg_min",
            "ALTER TABLE queue_token DROP CHECK chk_token_status",
            "ALTER TABLE feedback DROP CHECK chk_feedback_rating"
        ]:
            try:
                cursor.execute(drop_sql)
            except Exception:
                pass

        for add_sql in [
            "ALTER TABLE service ADD CONSTRAINT chk_service_avg_min CHECK (avg_service_min > 0)",
            "ALTER TABLE queue_token ADD CONSTRAINT chk_token_status CHECK (status IN ('Waiting', 'Serving', 'Completed', 'Cancelled'))",
            "ALTER TABLE feedback ADD CONSTRAINT chk_feedback_rating CHECK (rating >= 1 AND rating <= 5)"
        ]:
            try:
                cursor.execute(add_sql)
                print(f"   -> Constraint added: {add_sql.split()[5]}")
            except Exception as e:
                print(f"   -> Constraint notice: {e}")

        print("2. Verifying Indexes...")
        indexes = [
            "CREATE INDEX idx_token_status ON queue_token(status)",
            "CREATE INDEX idx_token_created_at ON queue_token(created_at)",
            "CREATE INDEX idx_token_service_status ON queue_token(service_id, status)",
            "CREATE INDEX idx_staff_dept ON staff(department_id)"
        ]
        for idx in indexes:
            try:
                cursor.execute(idx)
            except Exception:
                pass
        print("   -> Indexes verified.")

        print("3. Populating Seed Data...")
        # Offices
        offices = [
            (1, 'Ernakulam District Collectorate', 'Collectorate', 'Ernakulam'),
            (2, 'Thiruvananthapuram Taluk Office', 'Taluk Office', 'Thiruvananthapuram'),
            (3, 'Kozhikode Regional Transport Office (RTO)', 'RTO', 'Kozhikode'),
            (4, 'Thrissur Sub-Registrar Office', 'Sub-Registrar', 'Thrissur'),
            (5, 'Kottayam Civil Supplies Office', 'Civil Supplies', 'Kottayam')
        ]
        for o in offices:
            cursor.execute("INSERT IGNORE INTO office (office_id, office_name, office_type, district) VALUES (%s, %s, %s, %s)", o)

        # Departments
        departments = [
            (1, 'Revenue & Land Records', 1),
            (2, 'Public Grievance Redressal', 1),
            (3, 'Certificate & Identity Verification', 2),
            (4, 'Driving License & Vehicle Registration', 3),
            (5, 'Property Registration & Stamp Duty', 4),
            (6, 'Ration Card & Food Distribution', 5)
        ]
        for d in departments:
            cursor.execute("INSERT IGNORE INTO department (department_id, department_name, office_id) VALUES (%s, %s, %s)", d)

        # Services
        services = [
            (1, 'Land Mutation (Pokkuvaravu)', 25, 1),
            (2, 'Non-Creamy Layer Certificate', 15, 3),
            (3, 'Income Certificate Attestation', 10, 3),
            (4, 'Driving License Renewal & Slot', 20, 4),
            (5, 'Vehicle Ownership Transfer', 30, 4),
            (6, 'Sale Deed Registration', 45, 5),
            (7, 'Priority Ration Card Transfer', 15, 6),
            (8, 'District Collector Grievance Hearing', 35, 2)
        ]
        for s in services:
            cursor.execute("INSERT IGNORE INTO service (service_id, service_name, avg_service_min, department_id) VALUES (%s, %s, %s, %s)", s)

        # Staff
        staff_members = [
            (1, 'Rajesh Kumar K', 'Senior Counter Officer', 1),
            (2, 'Lakshmi Nair', 'Junior Verification Officer', 3),
            (3, 'Anandhu S', 'Vehicle Inspector Assistant', 4),
            (4, 'Sujatha Pillai', 'Registration Officer', 5),
            (5, 'Mohammed Faizal', 'Public Relations Executive', 2),
            (6, 'Divya Mary Joseph', 'Rationing Inspector', 6)
        ]
        for st in staff_members:
            cursor.execute("INSERT IGNORE INTO staff (staff_id, staff_name, role, department_id) VALUES (%s, %s, %s, %s)", st)

        # Citizens
        citizens = [
            (1, 'Kavya S Pillai', '9847123456', 'kavya.pillai@gmail.com', 'pbkdf2_sha256$260000$userpass1'),
            (2, 'Vishnu Prasad', '9447654321', 'vishnu.prasad@yahoo.com', 'pbkdf2_sha256$260000$userpass2'),
            (3, 'Fathima Raheem', '9745112233', 'fathima.raheem@outlook.com', 'pbkdf2_sha256$260000$userpass3'),
            (4, 'George Mathew', '9895334455', 'george.mathew@gmail.com', 'pbkdf2_sha256$260000$userpass4'),
            (5, 'Anjali Menon', '9496778899', 'anjali.menon@kerala.gov.in', 'pbkdf2_sha256$260000$userpass5'),
            (6, 'Rahul Varma', '9446889900', 'rahul.varma@gmail.com', 'pbkdf2_sha256$260000$userpass6'),
            (7, 'Sneha Balan', '9744223344', 'sneha.balan@gmail.com', 'pbkdf2_sha256$260000$userpass7')
        ]
        for c in citizens:
            cursor.execute("INSERT IGNORE INTO citizen (citizen_id, citizen_name, phone, email, password) VALUES (%s, %s, %s, %s, %s)", c)

        # Queue Tokens
        tokens = [
            (1, 'TK-101', 'Completed', 1, 1, 1),
            (2, 'TK-102', 'Completed', 2, 3, 2),
            (3, 'TK-103', 'Completed', 3, 4, 3),
            (4, 'TK-104', 'Completed', 4, 6, 4),
            (5, 'TK-105', 'Serving', 5, 2, 2),
            (6, 'TK-106', 'Serving', 6, 4, 3),
            (7, 'TK-107', 'Waiting', 7, 1, None),
            (8, 'TK-108', 'Waiting', 1, 4, None),
            (9, 'TK-109', 'Waiting', 2, 7, None),
            (10, 'TK-110', 'Cancelled', 3, 5, None)
        ]
        for tk in tokens:
            cursor.execute("""
                INSERT IGNORE INTO queue_token (token_id, token_number, status, citizen_id, service_id, staff_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW() - INTERVAL 10 MINUTE)
            """, tk)

        # Feedback
        feedbacks = [
            (1, 1, 1, 5, 'Smooth pokkuvaravu process, officer was courteous.'),
            (2, 2, 2, 4, 'Fast verification at the counter, received certificate quickly.'),
            (3, 3, 3, 5, 'DL slot test attended without delay.'),
            (4, 4, 4, 3, 'Took longer than expected for deed verification, but resolved.')
        ]
        for fb in feedbacks:
            cursor.execute("""
                INSERT IGNORE INTO feedback (feedback_id, token_id, citizen_id, rating, comments, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, fb)
        print("   -> Seed data populated successfully.")

        print("4. Creating SQL Views...")
        cursor.execute("""
        CREATE OR REPLACE VIEW vw_active_queue_status AS
        SELECT 
            t.token_id,
            t.token_number,
            t.status,
            c.citizen_name,
            srv.service_name,
            d.department_name,
            o.office_name,
            COALESCE(st.staff_name, 'Unassigned') AS counter_staff,
            TIMESTAMPDIFF(MINUTE, t.created_at, NOW()) AS elapsed_waiting_minutes
        FROM queue_token t
        JOIN citizen c ON t.citizen_id = c.citizen_id
        JOIN service srv ON t.service_id = srv.service_id
        JOIN department d ON srv.department_id = d.department_id
        JOIN office o ON d.office_id = o.office_id
        LEFT JOIN staff st ON t.staff_id = st.staff_id
        WHERE t.status IN ('Waiting', 'Serving')
        """)

        cursor.execute("""
        CREATE OR REPLACE VIEW vw_department_daily_performance AS
        SELECT 
            d.department_id,
            d.department_name,
            o.office_name,
            COUNT(t.token_id) AS total_tokens,
            SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tokens,
            SUM(CASE WHEN t.status = 'Serving' THEN 1 ELSE 0 END) AS serving_tokens,
            SUM(CASE WHEN t.status = 'Waiting' THEN 1 ELSE 0 END) AS waiting_tokens,
            ROUND(AVG(srv.avg_service_min), 1) AS expected_avg_service_time,
            ROUND(AVG(fb.rating), 2) AS customer_satisfaction_score
        FROM department d
        JOIN office o ON d.office_id = o.office_id
        JOIN service srv ON d.department_id = srv.department_id
        LEFT JOIN queue_token t ON srv.service_id = t.service_id
        LEFT JOIN feedback fb ON t.token_id = fb.token_id
        GROUP BY d.department_id, d.department_name, o.office_name
        """)

        cursor.execute("""
        CREATE OR REPLACE VIEW vw_citizen_service_history AS
        SELECT 
            c.citizen_id,
            c.citizen_name,
            c.phone,
            t.token_id,
            t.token_number,
            srv.service_name,
            t.status,
            t.created_at,
            fb.rating,
            fb.comments
        FROM citizen c
        JOIN queue_token t ON c.citizen_id = t.citizen_id
        JOIN service srv ON t.service_id = srv.service_id
        LEFT JOIN feedback fb ON t.token_id = fb.token_id
        """)
        print("   -> SQL Views created successfully.")

        print("5. Creating Stored Function...")
        cursor.execute("DROP FUNCTION IF EXISTS fn_calculate_estimated_wait_time")
        cursor.execute("""
        CREATE FUNCTION fn_calculate_estimated_wait_time(p_service_id INT)
        RETURNS INT
        DETERMINISTIC
        READS SQL DATA
        BEGIN
            DECLARE v_waiting_count INT DEFAULT 0;
            DECLARE v_avg_time INT DEFAULT 15;
            DECLARE v_total_wait_min INT DEFAULT 0;

            SELECT COUNT(*) INTO v_waiting_count
            FROM queue_token
            WHERE service_id = p_service_id AND status = 'Waiting';

            SELECT avg_service_min INTO v_avg_time
            FROM service
            WHERE service_id = p_service_id;

            SET v_total_wait_min = v_waiting_count * COALESCE(v_avg_time, 15);

            RETURN v_total_wait_min;
        END
        """)
        print("   -> Stored Function created.")

        print("6. Creating Stored Procedures...")
        cursor.execute("DROP PROCEDURE IF EXISTS sp_call_next_token")
        cursor.execute("""
        CREATE PROCEDURE sp_call_next_token(
            IN  p_staff_id     INT,
            OUT p_token_id     INT,
            OUT p_token_number VARCHAR(20)
        )
        proc_label: BEGIN
            DECLARE v_dept_id INT;
            DECLARE v_selected_token_id INT DEFAULT NULL;
            DECLARE v_selected_token_num VARCHAR(20) DEFAULT NULL;

            SELECT department_id INTO v_dept_id
            FROM staff
            WHERE staff_id = p_staff_id;

            IF v_dept_id IS NULL THEN
                SET p_token_id = NULL;
                SET p_token_number = 'STAFF_NOT_FOUND';
                LEAVE proc_label;
            END IF;

            SELECT t.token_id, t.token_number 
            INTO v_selected_token_id, v_selected_token_num
            FROM queue_token t
            JOIN service s ON t.service_id = s.service_id
            WHERE s.department_id = v_dept_id AND t.status = 'Waiting'
            ORDER BY t.created_at ASC
            LIMIT 1
            FOR UPDATE;

            IF v_selected_token_id IS NOT NULL THEN
                UPDATE queue_token
                SET status = 'Serving',
                    staff_id = p_staff_id
                WHERE token_id = v_selected_token_id;

                SET p_token_id = v_selected_token_id;
                SET p_token_number = v_selected_token_num;
            ELSE
                SET p_token_id = NULL;
                SET p_token_number = 'NO_WAITING_TOKENS';
            END IF;
        END
        """)

        cursor.execute("DROP PROCEDURE IF EXISTS sp_department_performance_report")
        cursor.execute("""
        CREATE PROCEDURE sp_department_performance_report(IN p_dept_id INT)
        BEGIN
            SELECT 
                d.department_name,
                o.office_name,
                COUNT(t.token_id) AS total_tokens_issued,
                SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tokens,
                SUM(CASE WHEN t.status = 'Waiting' THEN 1 ELSE 0 END) AS waiting_tokens,
                SUM(CASE WHEN t.status = 'Serving' THEN 1 ELSE 0 END) AS serving_tokens,
                ROUND(AVG(srv.avg_service_min), 1) AS avg_duration_min,
                ROUND(AVG(fb.rating), 2) AS satisfaction_rating
            FROM department d
            JOIN office o ON d.office_id = o.office_id
            JOIN service srv ON d.department_id = srv.department_id
            LEFT JOIN queue_token t ON srv.service_id = t.service_id
            LEFT JOIN feedback fb ON t.token_id = fb.token_id
            WHERE d.department_id = p_dept_id
            GROUP BY d.department_id, d.department_name, o.office_name;
        END
        """)
        print("   -> Stored Procedures created.")

    print("\n[OK] ALL ADBMS DATABASE PHASES INITIALIZED SUCCESSFULLY IN MYSQL!")

if __name__ == '__main__':
    apply_adbms_setup()
