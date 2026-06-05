import os
import sys

import psycopg2


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", os.getenv("DB", "educational_portal")),
        "user": os.getenv("DB_USER", os.getenv("USER", "postgres")),
        "password": os.getenv("DB_PASSWORD", os.getenv("PASSWORD", "")),
    }


def get_connection():
    try:
        conn = psycopg2.connect(**get_db_config())
        conn.autocommit = False
        return conn
    except Exception as error:
        print(f"Ошибка подключения к БД: {error}")
        sys.exit(1)


def create_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS dmr;")
    conn.commit()
    print("Схема dmr создана или уже существовала.")


def create_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS dmr.analytics_student_performance (
        student_id           INTEGER NOT NULL,
        course_id            INTEGER NOT NULL,
        department_id        INTEGER,
        department_name      VARCHAR(255),
        education_level      VARCHAR(50),
        education_base       VARCHAR(50),
        semester             INTEGER NOT NULL,
        course_year          INTEGER,
        final_grade          INTEGER CHECK (final_grade IN (2, 3, 4, 5)),
        total_events         INTEGER NOT NULL DEFAULT 0,
        avg_weekly_events    DECIMAL(10, 2) NOT NULL DEFAULT 0,
        total_course_views   INTEGER NOT NULL DEFAULT 0,
        total_quiz_views     INTEGER NOT NULL DEFAULT 0,
        total_module_views   INTEGER NOT NULL DEFAULT 0,
        total_submissions    INTEGER NOT NULL DEFAULT 0,
        peak_activity_week   INTEGER,
        consistency_score    DECIMAL(5, 2) NOT NULL DEFAULT 0,
        activity_category    VARCHAR(20) NOT NULL,
        last_update          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (student_id, course_id, semester)
    );
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    print("Таблица dmr.analytics_student_performance создана или уже существовала.")


def refresh_data_mart(conn):
    query = """
    WITH prepared_logs AS (
        SELECT
            ul.userid::INTEGER AS student_id,
            ul.courseid::INTEGER AS course_id,
            NULLIF(ul.depart::TEXT, '')::INTEGER AS department_id,
            d.name AS department_name,
            CASE NULLIF(ul.leveled::TEXT, '')::INTEGER
                WHEN 1 THEN 'бакалавриат'
                WHEN 2 THEN 'магистратура'
                WHEN 3 THEN 'специалитет'
                WHEN 4 THEN 'аспирантура'
                ELSE 'не указано'
            END AS education_level,
            CASE NULLIF(ul.name_osno::TEXT, '')::INTEGER
                WHEN 1 THEN 'бюджет'
                WHEN 2 THEN 'контракт'
                ELSE 'не указано'
            END AS education_base,
            ul.num_sem::INTEGER AS semester,
            ul.kurs::INTEGER AS course_year,
            NULLIF(ul.namer_level::TEXT, '')::INTEGER AS final_grade,
            ul.num_week::INTEGER AS week_number,
            COALESCE(ul.s_all, 0)::INTEGER AS weekly_events,
            COALESCE(ul.s_course_viewed, 0)::INTEGER AS weekly_course_views,
            COALESCE(ul.s_q_attempt_viewed, 0)::INTEGER AS weekly_quiz_views,
            COALESCE(ul.s_a_course_module_viewed, 0)::INTEGER AS weekly_module_views,
            COALESCE(ul.s_a_submission_status_viewed, 0)::INTEGER AS weekly_submissions
        FROM public.user_logs ul
        LEFT JOIN public.departments d
            ON d.id = NULLIF(ul.depart::TEXT, '')::INTEGER
        WHERE ul.userid IS NOT NULL
          AND ul.courseid IS NOT NULL
          AND ul.num_sem IS NOT NULL
          AND NULLIF(ul.namer_level::TEXT, '')::INTEGER IN (2, 3, 4, 5)
    ),
    weekly_ranked AS (
        SELECT
            prepared_logs.*,
            ROW_NUMBER() OVER (
                PARTITION BY student_id, course_id, semester
                ORDER BY weekly_events DESC, week_number ASC
            ) AS activity_rank
        FROM prepared_logs
    ),
    aggregated AS (
        SELECT
            student_id,
            course_id,
            MAX(department_id) AS department_id,
            MAX(department_name) AS department_name,
            MAX(education_level) AS education_level,
            MAX(education_base) AS education_base,
            semester,
            MAX(course_year) AS course_year,
            MAX(final_grade) AS final_grade,
            SUM(weekly_events)::INTEGER AS total_events,
            ROUND(AVG(weekly_events)::NUMERIC, 2) AS avg_weekly_events,
            SUM(weekly_course_views)::INTEGER AS total_course_views,
            SUM(weekly_quiz_views)::INTEGER AS total_quiz_views,
            SUM(weekly_module_views)::INTEGER AS total_module_views,
            SUM(weekly_submissions)::INTEGER AS total_submissions,
            MAX(week_number) FILTER (WHERE activity_rank = 1) AS peak_activity_week,
            ROUND(
                CASE
                    WHEN AVG(weekly_events) = 0 THEN 0
                    ELSE GREATEST(
                        0,
                        LEAST(1, 1 - STDDEV_POP(weekly_events) / AVG(weekly_events))
                    )
                END::NUMERIC,
                2
            ) AS consistency_score
        FROM weekly_ranked
        GROUP BY student_id, course_id, semester
    )
    INSERT INTO dmr.analytics_student_performance (
        student_id,
        course_id,
        department_id,
        department_name,
        education_level,
        education_base,
        semester,
        course_year,
        final_grade,
        total_events,
        avg_weekly_events,
        total_course_views,
        total_quiz_views,
        total_module_views,
        total_submissions,
        peak_activity_week,
        consistency_score,
        activity_category
    )
    SELECT
        student_id,
        course_id,
        department_id,
        department_name,
        education_level,
        education_base,
        semester,
        course_year,
        final_grade,
        total_events,
        avg_weekly_events,
        total_course_views,
        total_quiz_views,
        total_module_views,
        total_submissions,
        peak_activity_week,
        consistency_score,
        CASE
            WHEN avg_weekly_events < 5 THEN 'низкая'
            WHEN avg_weekly_events < 20 THEN 'средняя'
            ELSE 'высокая'
        END AS activity_category
    FROM aggregated
    ON CONFLICT (student_id, course_id, semester)
    DO UPDATE SET
        department_id = EXCLUDED.department_id,
        department_name = EXCLUDED.department_name,
        education_level = EXCLUDED.education_level,
        education_base = EXCLUDED.education_base,
        course_year = EXCLUDED.course_year,
        final_grade = EXCLUDED.final_grade,
        total_events = EXCLUDED.total_events,
        avg_weekly_events = EXCLUDED.avg_weekly_events,
        total_course_views = EXCLUDED.total_course_views,
        total_quiz_views = EXCLUDED.total_quiz_views,
        total_module_views = EXCLUDED.total_module_views,
        total_submissions = EXCLUDED.total_submissions,
        peak_activity_week = EXCLUDED.peak_activity_week,
        consistency_score = EXCLUDED.consistency_score,
        activity_category = EXCLUDED.activity_category,
        last_update = CURRENT_TIMESTAMP;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        affected_rows = cur.rowcount
    conn.commit()
    print(f"Витрина обновлена. Добавлено/обновлено записей: {affected_rows}")


def create_performance_mart():
    conn = None
    try:
        conn = get_connection()
        create_schema(conn)
        create_table(conn)
        refresh_data_mart(conn)
        print("Все операции выполнены успешно.")
    except Exception as error:
        print(f"Ошибка в процессе выполнения: {error}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            print("Соединение с БД закрыто.")


if __name__ == "__main__":
    create_performance_mart()
