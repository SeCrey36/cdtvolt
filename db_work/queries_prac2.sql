-- JOIN examples for practical work using db_work/database.sqlite3

-- 1) INNER JOIN: enrollments with timeslot and course
SELECT e.id AS enrollment_id, e.student_name, t.id AS timeslot_id, c.id AS course_id, c.title
FROM enrollments e
JOIN enrollment_timeslots et ON et.enrollment_id = e.id
JOIN timeslots t ON t.id = et.timeslot_id
JOIN courses c ON c.id = t.course_id
LIMIT 10;

-- 2) LEFT JOIN: courses with timeslots (show courses even without timeslots)
SELECT c.id AS course_id, c.title, t.id AS timeslot_id
FROM courses c
LEFT JOIN timeslots t ON t.course_id = c.id
LIMIT 10;

-- 3) CROSS JOIN: Cartesian product small sample
SELECT c.id AS course_id, c.title, t.id AS timeslot_id, t.room
FROM (SELECT * FROM courses LIMIT 5) c
CROSS JOIN (SELECT * FROM timeslots LIMIT 3) t
LIMIT 20;

-- 4) Aggregation with JOIN: number of enrollments per course
SELECT c.id, c.title, COUNT(DISTINCT e.id) AS enroll_count
FROM courses c
LEFT JOIN timeslots t ON t.course_id = c.id
LEFT JOIN enrollment_timeslots et ON et.timeslot_id = t.id
LEFT JOIN enrollments e ON e.id = et.enrollment_id
GROUP BY c.id
ORDER BY enroll_count DESC
LIMIT 10;

-- 5) Typical application query: course schedule with instructor names
SELECT c.title, t.day_of_week, t.time_slot, i.name AS instructor
FROM courses c
JOIN timeslots t ON t.course_id = c.id
LEFT JOIN course_instructors ci ON ci.course_id = c.id
LEFT JOIN instructors i ON i.id = ci.instructor_id
LIMIT 20;
