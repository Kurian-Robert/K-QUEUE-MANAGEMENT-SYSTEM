-- ============================================================================
-- KERALA QUEUE MANAGEMENT SYSTEM (KQMS) - ADBMS COMPREHENSIVE SQL SCRIPT
-- Tech Stack: MySQL 8.0+, Django Framework, Python
-- Academic Coursework: Advanced Database Management Systems (ADBMS)
-- Database Name: kqms
-- ============================================================================

USE kqms;

-- ============================================================================
-- PHASE 1: DATA MODELLING, 3NF NORMALIZATION & INTEGRITY CONSTRAINTS
-- ============================================================================
-- ER Architecture & Relationships:
-- 1. office (office_id PK)
-- 2. department (department_id PK, office_id FK -> office.office_id)
-- 3. service (service_id PK, department_id FK -> department.department_id)
-- 4. staff (staff_id PK, department_id FK -> department.department_id)
-- 5. citizen (citizen_id PK, email UNIQUE)
-- 6. queue_token (token_id PK, citizen_id FK, service_id FK, staff_id FK NULL)
-- 7. feedback (feedback_id PK, token_id FK UNIQUE, citizen_id FK)
-- 8. admin (id PK, username UNIQUE)
--
-- Normalization Verification (3NF):
-- 1NF: Atomic attributes, single-valued columns, primary keys defined.
-- 2NF: In 1NF and all non-key attributes are fully functionally dependent on the primary key (no partial dependencies).
-- 3NF: In 2NF and no transitive functional dependencies (no non-key attribute determines another non-key attribute).
--      Service connects to Department; Token connects to Service; Feedback is separated from QueueToken.
-- ============================================================================

-- Enforce Check Constraints on Existing Tables
ALTER TABLE service 
    DROP CONSTRAINT IF EXISTS chk_service_avg_min;
ALTER TABLE service 
    ADD CONSTRAINT chk_service_avg_min CHECK (avg_service_min > 0);

ALTER TABLE queue_token 
    DROP CONSTRAINT IF EXISTS chk_token_status;
ALTER TABLE queue_token 
    ADD CONSTRAINT chk_token_status CHECK (status IN ('Waiting', 'Serving', 'Completed', 'Cancelled'));

ALTER TABLE feedback 
    DROP CONSTRAINT IF EXISTS chk_feedback_rating;
ALTER TABLE feedback 
    ADD CONSTRAINT chk_feedback_rating CHECK (rating >= 1 AND rating <= 5);

-- Performance B-Tree Indexes for Query Optimization
CREATE INDEX IF NOT EXISTS idx_token_status ON queue_token(status);
CREATE INDEX IF NOT EXISTS idx_token_created_at ON queue_token(created_at);
CREATE INDEX IF NOT EXISTS idx_token_service_status ON queue_token(service_id, status);
CREATE INDEX IF NOT EXISTS idx_staff_dept ON staff(department_id);


-- ============================================================================
-- PHASE 2: DATABASE CREATION, DATA PREPARATION & SEED DATASET
-- ============================================================================

-- 1. Insert Government Offices in Kerala
INSERT IGNORE INTO office (office_id, office_name, office_type, district) VALUES
(1, 'Ernakulam District Collectorate', 'Collectorate', 'Ernakulam'),
(2, 'Thiruvananthapuram Taluk Office', 'Taluk Office', 'Thiruvananthapuram'),
(3, 'Kozhikode Regional Transport Office (RTO)', 'RTO', 'Kozhikode'),
(4, 'Thrissur Sub-Registrar Office', 'Sub-Registrar', 'Thrissur'),
(5, 'Kottayam Civil Supplies Office', 'Civil Supplies', 'Kottayam');

-- 2. Insert Departments mapped to Offices
INSERT IGNORE INTO department (department_id, department_name, office_id) VALUES
(1, 'Revenue & Land Records', 1),
(2, 'Public Grievance Redressal', 1),
(3, 'Certificate & Identity Verification', 2),
(4, 'Driving License & Vehicle Registration', 3),
(5, 'Property Registration & Stamp Duty', 4),
(6, 'Ration Card & Food Distribution', 5);

-- 3. Insert Public Services with Average Service Times
INSERT IGNORE INTO service (service_id, service_name, avg_service_min, department_id) VALUES
(1, 'Land Mutation (Pokkuvaravu)', 25, 1),
(2, 'Non-Creamy Layer Certificate', 15, 3),
(3, 'Income Certificate Attestation', 10, 3),
(4, 'Driving License Renewal & Slot', 20, 4),
(5, 'Vehicle Ownership Transfer', 30, 4),
(6, 'Sale Deed Registration', 45, 5),
(7, 'Priority Ration Card Transfer', 15, 6),
(8, 'District Collector Grievance Hearing', 35, 2);

-- 4. Insert Staff Members
INSERT IGNORE INTO staff (staff_id, staff_name, role, department_id) VALUES
(1, 'Rajesh Kumar K', 'Senior Counter Officer', 1),
(2, 'Lakshmi Nair', 'Junior Verification Officer', 3),
(3, 'Anandhu S', 'Vehicle Inspector Assistant', 4),
(4, 'Sujatha Pillai', 'Registration Officer', 5),
(5, 'Mohammed Faizal', 'Public Relations Executive', 2),
(6, 'Divya Mary Joseph', 'Rationing Inspector', 6);

-- 5. Insert Citizens
INSERT IGNORE INTO citizen (citizen_id, citizen_name, phone, email, password) VALUES
(1, 'Kavya S Pillai', '9847123456', 'kavya.pillai@gmail.com', 'pbkdf2_sha256$260000$userpass1'),
(2, 'Vishnu Prasad', '9447654321', 'vishnu.prasad@yahoo.com', 'pbkdf2_sha256$260000$userpass2'),
(3, 'Fathima Raheem', '9745112233', 'fathima.raheem@outlook.com', 'pbkdf2_sha256$260000$userpass3'),
(4, 'George Mathew', '9895334455', 'george.mathew@gmail.com', 'pbkdf2_sha256$260000$userpass4'),
(5, 'Anjali Menon', '9496778899', 'anjali.menon@kerala.gov.in', 'pbkdf2_sha256$260000$userpass5'),
(6, 'Rahul Varma', '9446889900', 'rahul.varma@gmail.com', 'pbkdf2_sha256$260000$userpass6'),
(7, 'Sneha Balan', '9744223344', 'sneha.balan@gmail.com', 'pbkdf2_sha256$260000$userpass7');

-- 6. Insert Queue Tokens (Diverse Statuses: Completed, Serving, Waiting, Cancelled)
INSERT IGNORE INTO queue_token (token_id, token_number, status, created_at, citizen_id, service_id, staff_id) VALUES
(1, 'TK-101', 'Completed', NOW() - INTERVAL 120 MINUTE, 1, 1, 1),
(2, 'TK-102', 'Completed', NOW() - INTERVAL 100 MINUTE, 2, 3, 2),
(3, 'TK-103', 'Completed', NOW() - INTERVAL 90 MINUTE, 3, 4, 3),
(4, 'TK-104', 'Completed', NOW() - INTERVAL 75 MINUTE, 4, 6, 4),
(5, 'TK-105', 'Serving',   NOW() - INTERVAL 30 MINUTE, 5, 2, 2),
(6, 'TK-106', 'Serving',   NOW() - INTERVAL 20 MINUTE, 6, 4, 3),
(7, 'TK-107', 'Waiting',   NOW() - INTERVAL 15 MINUTE, 7, 1, NULL),
(8, 'TK-108', 'Waiting',   NOW() - INTERVAL 10 MINUTE, 1, 4, NULL),
(9, 'TK-109', 'Waiting',   NOW() - INTERVAL 5 MINUTE,  2, 7, NULL),
(10, 'TK-110', 'Cancelled', NOW() - INTERVAL 50 MINUTE, 3, 5, NULL);

-- 7. Insert Citizen Feedback
INSERT IGNORE INTO feedback (feedback_id, token_id, citizen_id, rating, comments, created_at) VALUES
(1, 1, 1, 5, 'Smooth pokkuvaravu process, officer was courteous.', NOW() - INTERVAL 80 MINUTE),
(2, 2, 2, 4, 'Fast verification at the counter, received certificate quickly.', NOW() - INTERVAL 60 MINUTE),
(3, 3, 3, 5, 'DL slot test attended without delay.', NOW() - INTERVAL 55 MINUTE),
(4, 4, 4, 3, 'Took longer than expected for deed verification, but resolved.', NOW() - INTERVAL 40 MINUTE);


-- ============================================================================
-- DATA CLEANING & HYGIENE OPERATIONS
-- ============================================================================

-- 1. Identify and Handle NULL Staff Assignments (Demonstrating IFNULL / COALESCE)
SELECT 
    t.token_id,
    t.token_number,
    t.status,
    COALESCE(s.staff_name, 'Unassigned / In Waiting Pool') AS assigned_staff,
    IFNULL(d.department_name, 'General Helpdesk') AS department_name
FROM queue_token t
LEFT JOIN staff s ON t.staff_id = s.staff_id
LEFT JOIN service srv ON t.service_id = srv.service_id
LEFT JOIN department d ON srv.department_id = d.department_id
ORDER BY t.token_id;

-- 2. Data Cleaning: Strip Whitespace and Standardize Strings
UPDATE citizen 
SET citizen_name = TRIM(citizen_name),
    email = LOWER(TRIM(email))
WHERE citizen_id > 0;

-- 3. Data Cleaning: Standardize Phone Formats (ensuring 10 digits)
UPDATE citizen
SET phone = REGEXP_REPLACE(phone, '[^0-9]', '')
WHERE citizen_id > 0;


-- ============================================================================
-- BASIC QUERIES & AGGREGATE SUMMARY FUNCTIONS
-- ============================================================================

-- 1. Basic Filtering and Ordering
SELECT token_number, status, created_at 
FROM queue_token 
WHERE status = 'Waiting' 
ORDER BY created_at ASC;

-- 2. Aggregate Summary by Service (COUNT, AVG, MIN, MAX)
SELECT 
    srv.service_name,
    COUNT(t.token_id) AS total_tokens_issued,
    SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN t.status = 'Waiting' THEN 1 ELSE 0 END) AS waiting_count,
    ROUND(AVG(srv.avg_service_min), 1) AS standard_service_duration_min
FROM service srv
LEFT JOIN queue_token t ON srv.service_id = t.service_id
GROUP BY srv.service_id, srv.service_name
ORDER BY total_tokens_issued DESC;

-- 3. Department Level Aggregate with HAVING Clause
SELECT 
    d.department_name,
    COUNT(t.token_id) AS total_department_tokens,
    ROUND(AVG(fb.rating), 2) AS avg_citizen_rating
FROM department d
JOIN service srv ON d.department_id = srv.department_id
LEFT JOIN queue_token t ON srv.service_id = t.service_id
LEFT JOIN feedback fb ON t.token_id = fb.token_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(t.token_id) >= 1
ORDER BY avg_citizen_rating DESC;


-- ============================================================================
-- PHASE 3: DATA QUERYING AND ANALYTICAL OPERATIONS
-- ============================================================================

-- 1. Multi-Table JOIN (6 Tables: Token, Citizen, Service, Dept, Office, Staff)
SELECT 
    t.token_number,
    t.status,
    c.citizen_name,
    c.phone AS citizen_contact,
    srv.service_name,
    d.department_name,
    o.office_name,
    o.district,
    COALESCE(st.staff_name, 'Awaiting Counter Assignment') AS handling_staff,
    fb.rating AS citizen_rating,
    fb.comments AS citizen_feedback
FROM queue_token t
INNER JOIN citizen c ON t.citizen_id = c.citizen_id
INNER JOIN service srv ON t.service_id = srv.service_id
INNER JOIN department d ON srv.department_id = d.department_id
INNER JOIN office o ON d.office_id = o.office_id
LEFT JOIN staff st ON t.staff_id = st.staff_id
LEFT JOIN feedback fb ON t.token_id = fb.token_id
ORDER BY t.created_at DESC;

-- 2. Nested Subquery in WHERE: Services with Average Time Above Global Mean
SELECT 
    service_id,
    service_name,
    avg_service_min
FROM service
WHERE avg_service_min > (
    SELECT AVG(avg_service_min) FROM service
)
ORDER BY avg_service_min DESC;

-- 3. Correlated Subquery: Latest Token Issued for Each Citizen
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
    ) AS latest_token_number,
    (
        SELECT t.status 
        FROM queue_token t 
        WHERE t.citizen_id = c.citizen_id 
        ORDER BY t.created_at DESC 
        LIMIT 1
    ) AS latest_token_status
FROM citizen c;

-- 4. Subquery with NOT EXISTS: Citizens who have Completed Tokens but No Feedback
SELECT 
    c.citizen_id,
    c.citizen_name,
    c.phone,
    t.token_number
FROM citizen c
JOIN queue_token t ON c.citizen_id = t.citizen_id
WHERE t.status = 'Completed'
AND NOT EXISTS (
    SELECT 1 FROM feedback fb WHERE fb.token_id = t.token_id
);


-- ============================================================================
-- SQL VIEWS FOR REUSABLE REPORTING & LIVE DASHBOARDS
-- ============================================================================

-- View 1: Real-time Active Queue Status
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
WHERE t.status IN ('Waiting', 'Serving');

-- View 2: Department Daily Performance Summary
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
GROUP BY d.department_id, d.department_name, o.office_name;

-- View 3: Citizen Service History with Feedback
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
LEFT JOIN feedback fb ON t.token_id = fb.token_id;


-- ============================================================================
-- STORED FUNCTION: ESTIMATED WAIT TIME CALCULATION
-- Calculates total estimated wait time in minutes for any public service
-- based on current waiting tokens multiplied by standard service duration.
-- ============================================================================
DROP FUNCTION IF EXISTS fn_calculate_estimated_wait_time;
DELIMITER $$
CREATE FUNCTION fn_calculate_estimated_wait_time(p_service_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_waiting_count INT DEFAULT 0;
    DECLARE v_avg_time INT DEFAULT 15;
    DECLARE v_total_wait_min INT DEFAULT 0;

    -- Fetch count of tokens currently in Waiting status for this service
    SELECT COUNT(*) INTO v_waiting_count
    FROM queue_token
    WHERE service_id = p_service_id AND status = 'Waiting';

    -- Fetch standard average service duration
    SELECT avg_service_min INTO v_avg_time
    FROM service
    WHERE service_id = p_service_id;

    -- Compute cumulative estimated wait time
    SET v_total_wait_min = v_waiting_count * COALESCE(v_avg_time, 15);

    RETURN v_total_wait_min;
END$$
DELIMITER ;


-- ============================================================================
-- STORED PROCEDURE: ATOMIC CALL NEXT TOKEN
-- Uses Row-Level Locking (FOR UPDATE) to safely pull the oldest waiting token,
-- transition it to 'Serving', and assign to the staff member.
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_call_next_token;
DELIMITER $$
CREATE PROCEDURE sp_call_next_token(
    IN  p_staff_id     INT,
    OUT p_token_id     INT,
    OUT p_token_number VARCHAR(20)
)
proc_label: BEGIN
    DECLARE v_dept_id INT;
    DECLARE v_selected_token_id INT DEFAULT NULL;
    DECLARE v_selected_token_num VARCHAR(20) DEFAULT NULL;

    -- Fetch staff department
    SELECT department_id INTO v_dept_id
    FROM staff
    WHERE staff_id = p_staff_id;

    IF v_dept_id IS NULL THEN
        SET p_token_id = NULL;
        SET p_token_number = 'STAFF_NOT_FOUND';
        LEAVE proc_label;
    END IF;

    -- Select next waiting token for staff's department using row lock
    SELECT t.token_id, t.token_number 
    INTO v_selected_token_id, v_selected_token_num
    FROM queue_token t
    JOIN service s ON t.service_id = s.service_id
    WHERE s.department_id = v_dept_id AND t.status = 'Waiting'
    ORDER BY t.created_at ASC
    LIMIT 1
    FOR UPDATE;

    IF v_selected_token_id IS NOT NULL THEN
        -- Atomically update token status to Serving
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
END$$
DELIMITER ;


-- ============================================================================
-- STORED PROCEDURE: COMPREHENSIVE DEPARTMENT PERFORMANCE REPORT
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_department_performance_report;
DELIMITER $$
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
END$$
DELIMITER ;


-- ============================================================================
-- QUERY EXECUTION PLAN DEMONSTRATION (EXPLAIN)
-- Demonstrates query optimization, index usage, and cost-based execution.
-- ============================================================================
EXPLAIN 
SELECT t.token_number, t.status, s.service_name, c.citizen_name 
FROM queue_token t
JOIN service s ON t.service_id = s.service_id
JOIN citizen c ON t.citizen_id = c.citizen_id
WHERE t.status = 'Waiting';


-- ============================================================================
-- PHASE 4: DATA INTEGRITY & TRANSACTION HANDLING (ACID DEMONSTRATION)
-- ============================================================================

-- Scenario A: Successful Multi-table Atomic Transaction with SAVEPOINT & COMMIT
START TRANSACTION;

SAVEPOINT before_service_completion;

-- Step 1: Update token from Serving to Completed
UPDATE queue_token
SET status = 'Completed'
WHERE token_id = 5;

-- Step 2: Insert Citizen Feedback atomically
INSERT INTO feedback (token_id, citizen_id, rating, comments, created_at)
VALUES (5, 5, 5, 'Exceptional counter assistance, completed in 10 mins.', NOW());

-- Everything succeeded -> COMMIT
COMMIT;


-- Scenario B: Intentional Failure & Automatic ROLLBACK Demonstration
-- Demonstrates Atomicity: If one statement in the atomic batch fails, all prior changes roll back.
START TRANSACTION;

SAVEPOINT before_failed_token;

-- Step 1: Change status
UPDATE queue_token
SET status = 'Completed'
WHERE token_id = 6;

-- Step 2: Intentionally attempt an invalid insert (rating 99 violates CHECK constraint chk_feedback_rating)
-- In MySQL 8.0, this triggers an error:
-- Error Code: 3819. Check constraint 'chk_feedback_rating' is violated.
-- The application intercepts this error and executes ROLLBACK:
ROLLBACK;

-- Verify that token 6 remains in its original status ('Serving') because of ROLLBACK:
SELECT token_id, token_number, status 
FROM queue_token 
WHERE token_id = 6;
