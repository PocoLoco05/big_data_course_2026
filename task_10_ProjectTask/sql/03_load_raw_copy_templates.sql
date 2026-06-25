-- Run from psql, replacing :project_dir with the absolute path to task_10_ProjectTask.
-- Example:
-- \set project_dir '/Users/glebzilenkov/big_data_course_2026/task_10_ProjectTask'

\copy raw.users FROM :'project_dir'/data/raw/users.csv WITH (FORMAT csv, HEADER true);
\copy raw.categories FROM :'project_dir'/data/raw/categories.csv WITH (FORMAT csv, HEADER true);
\copy raw.support_staff FROM :'project_dir'/data/raw/support_staff.csv WITH (FORMAT csv, HEADER true);
\copy raw.tickets FROM :'project_dir'/data/raw/tickets.csv WITH (FORMAT csv, HEADER true);
