# Task 10 Project Task

Вариант 9: техподдержка, заявки и обращения.

Задача: создать витрину для анализа качества работы службы поддержки и нагрузки на сотрудников.

## Структура

- `src/generate_data.py` - генерация синтетических данных
- `src/create_marts.py` - transform и создание витрин в pandas
- `src/visualize.py` - построение графиков
- `run_pipeline.py` - единый запуск всего пайплайна
- `data/raw/` - сгенерированные raw CSV
- `data/stg/` - обогащённая staging-таблица
- `data/mart/` - итоговые витрины
- `outputs/figures/` - визуализации
- `sql/` - SQL-версия raw, transform и mart-слоя
- `dags/support_project_dag.py` - Airflow DAG

## Запуск

Из папки курса:

```bash
.venv/bin/python task_10_ProjectTask/run_pipeline.py
```

После запуска должны появиться:

- `data/raw/users.csv`
- `data/raw/categories.csv`
- `data/raw/support_staff.csv`
- `data/raw/tickets.csv`
- `data/stg/ticket_enriched.csv`
- `data/mart/support_kpi.csv`
- `data/mart/ticket_stats.csv`
- `outputs/figures/avg_resolution_by_staff.png`
- `outputs/figures/tickets_by_category.png`
- `outputs/figures/ticket_creation_daily.png`
- `outputs/figures/ticket_status_pie.png`

## Витрины

### mart.support_kpi

- `staff_id` - id сотрудника поддержки
- `full_name` - ФИО сотрудника
- `tickets_resolved` - количество заявок со статусом `решена` или `закрыта`
- `avg_resolution_time_hours` - среднее время решения в часах
- `backlog` - количество открытых заявок со статусом `новая` или `в работе`

### mart.ticket_stats

- `category` - категория заявки
- `priority` - приоритет заявки
- `avg_resolution_time` - среднее время решения по категории и приоритету
- `total_tickets` - количество заявок по категории и приоритету

## DAG

В DAG отражены шаги из задания:

1. `generate_data`
2. `load_raw`
3. `transform`
4. `create_mart`
5. `visualize`

Файл DAG: `dags/support_project_dag.py`.
