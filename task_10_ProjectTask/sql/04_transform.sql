DROP TABLE IF EXISTS stg.ticket_enriched;

CREATE TABLE stg.ticket_enriched AS
SELECT
    t.ticket_id,
    t.user_id,
    u.full_name AS user_full_name,
    u.level AS user_level,
    t.category_id,
    c.name AS category,
    t.subject,
    t.description,
    t.created_at,
    t.updated_at,
    t.resolved_at,
    t.status,
    t.priority,
    t.staff_id,
    s.full_name AS staff_full_name,
    s.department,
    t.comments_json,
    jsonb_array_length(COALESCE(t.comments_json, '[]'::jsonb)) AS comments_count,
    t.status IN ('решена', 'закрыта') AS is_final_status,
    CASE
        WHEN t.status IN ('решена', 'закрыта')
        THEN ROUND(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at)) / 3600.0, 2)
        ELSE NULL
    END AS resolution_hours
FROM raw.tickets t
JOIN raw.users u
    ON u.user_id = t.user_id
JOIN raw.categories c
    ON c.category_id = t.category_id
LEFT JOIN raw.support_staff s
    ON s.staff_id = t.staff_id;
