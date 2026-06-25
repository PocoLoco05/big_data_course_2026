DROP TABLE IF EXISTS mart.support_kpi;
DROP TABLE IF EXISTS mart.ticket_stats;

CREATE TABLE mart.support_kpi AS
SELECT
    s.staff_id,
    s.full_name,
    COUNT(te.ticket_id) FILTER (
        WHERE te.status IN ('решена', 'закрыта')
    ) AS tickets_resolved,
    ROUND(AVG(te.resolution_hours) FILTER (
        WHERE te.status IN ('решена', 'закрыта')
    ), 2) AS avg_resolution_time_hours,
    COUNT(te.ticket_id) FILTER (
        WHERE te.status IN ('новая', 'в работе')
    ) AS backlog
FROM raw.support_staff s
LEFT JOIN stg.ticket_enriched te
    ON te.staff_id = s.staff_id
GROUP BY
    s.staff_id,
    s.full_name
ORDER BY
    s.staff_id;

CREATE TABLE mart.ticket_stats AS
SELECT
    category,
    priority,
    ROUND(AVG(resolution_hours) FILTER (
        WHERE status IN ('решена', 'закрыта')
    ), 2) AS avg_resolution_time,
    COUNT(*) AS total_tickets
FROM stg.ticket_enriched
GROUP BY
    category,
    priority
ORDER BY
    category,
    priority;
