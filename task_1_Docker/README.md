# task_1_Docker

Учебный проект для запуска PostgreSQL в Docker и загрузки двух CSV-файлов:

- `user_logs` из `datasets/aggrigation_logs_per_week.csv`
- `departments` из `datasets/departments.csv`

## Запуск

1. Создать `.env` на основе `.env.example`
2. Запустить:

```bash
docker compose up -d --build
```

## Подключение

- Host: `localhost`
- Port: `5433`
- Database: `logs_db`
- User: `student`
- Password: `student_pass_2026`
