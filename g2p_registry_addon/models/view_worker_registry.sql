-- Registry Worker View
CREATE OR REPLACE VIEW g2p_registry_worker AS
SELECT 
    id              AS id,
    CAST(id AS VARCHAR) AS link_registry_id,
    name            AS name,
    email           AS email,
    phone           AS phone,
    province_id     AS province_id,
    district_id     AS district_id,
    constituency_id AS constituency_id,
    ward_id         AS ward_id
FROM res_partner
WHERE is_registrant = True 
  AND is_group = False 
  AND active = True;

-- Monthly Availability Registry View
CREATE OR REPLACE VIEW g2p_registry_monthly_availability AS
SELECT 
    enumerator.id AS id,
    CAST(enumerator.partner_id AS VARCHAR) AS link_registry_id,
    enumerator.name AS name,
    enumerator.data_collection_month AS attendance_month_str,
    DATE_TRUNC('month', enumerator.data_collection_date) AS attendance_month,
    enumerator.source_type AS source_type
FROM g2p_enumerator enumerator
WHERE enumerator.partner_id IS NOT NULL

# TODO: update model names
-- Monthly Attendance Registry View
CREATE OR REPLACE VIEW g2p_registry_monthly_attendance AS
SELECT 
    ROW_NUMBER() OVER () AS id,
    CAST(worker_id AS VARCHAR) AS link_registry_id,
    nrc_number       AS nrc_number,
    DATE_TRUNC('month', date_of_work)     AS attendance_month,
    COUNT(date_of_work) AS number_of_days
FROM g2p_worker_attendance
GROUP BY link_registry_id, nrc_number, attendance_month