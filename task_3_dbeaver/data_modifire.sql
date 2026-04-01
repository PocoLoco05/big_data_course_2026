select * from user_logs limit 30;

SELECT AVG(s_all_avg) FROM user_logs;

UPDATE user_logs 
SET s_all_avg = REPLACE(s_all_avg, ',', '.') 
WHERE s_all_avg LIKE '%,%';


ALTER TABLE user_logs 
ALTER COLUMN s_all_avg 
TYPE REAL 
USING s_all_avg::REAL;

UPDATE user_logs SET s_course_viewed_avg = REPLACE(s_course_viewed_avg, ',', '.') WHERE s_course_viewed_avg LIKE '%,%';
UPDATE user_logs SET s_q_attempt_viewed_avg = REPLACE(s_q_attempt_viewed_avg, ',', '.') WHERE s_q_attempt_viewed_avg LIKE '%,%';
UPDATE user_logs SET s_a_course_module_viewed_avg = REPLACE(s_a_course_module_viewed_avg, ',', '.') WHERE s_a_course_module_viewed_avg LIKE '%,%';
UPDATE user_logs SET s_a_submission_status_viewed_avg = REPLACE(s_a_submission_status_viewed_avg, ',', '.') WHERE s_a_submission_status_viewed_avg LIKE '%,%';

ALTER TABLE user_logs ALTER COLUMN s_course_viewed_avg TYPE REAL USING NULLIF(s_course_viewed_avg, '')::REAL;

ALTER TABLE user_logs ALTER COLUMN s_q_attempt_viewed_avg TYPE FLOAT4 USING NULLIF(s_q_attempt_viewed_avg, '')::FLOAT4;
ALTER TABLE user_logs ALTER COLUMN s_a_course_module_viewed_avg TYPE REAL USING NULLIF(s_a_course_module_viewed_avg, '')::REAL;
ALTER TABLE user_logs ALTER COLUMN s_a_submission_status_viewed_avg TYPE REAL USING NULLIF(s_a_submission_status_viewed_avg, '')::REAL;

ALTER TABLE user_logs ALTER COLUMN namer_level TYPE int4 USING namer_level::int4;




SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'user_logs'
  AND column_name IN (
    's_all_avg',
    's_course_viewed_avg',
    's_q_attempt_viewed_avg',
    's_a_course_module_viewed_avg',
    's_a_submission_status_viewed_avg',
    'depart',
    'namer_level',
    'name_osno',
    'level_id'
  )
ORDER BY column_name;

commit;