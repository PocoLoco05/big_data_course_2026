-- Среднее время решения по сотрудникам.
SELECT
    full_name,
    avg_resolution_time_hours
FROM mart.support_kpi
ORDER BY avg_resolution_time_hours DESC NULLS LAST;

-- Количество заявок по категориям.
SELECT
    category,
    SUM(total_tickets) AS total_tickets
FROM mart.ticket_stats
GROUP BY category
ORDER BY total_tickets DESC;

-- Динамика создания заявок по дням.
SELECT
    DATE(created_at) AS created_day,
    COUNT(*) AS total_tickets
FROM stg.ticket_enriched
GROUP BY DATE(created_at)
ORDER BY created_day;

-- Круговая диаграмма статусов заявок.
SELECT
    status,
    COUNT(*) AS total_tickets
FROM stg.ticket_enriched
GROUP BY status
ORDER BY total_tickets DESC;
