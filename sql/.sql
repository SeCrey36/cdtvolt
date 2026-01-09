-- Таблица пользователей Django (auth_user) автоматически

-- Профиль пользователя
CREATE TABLE userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL DEFAULT '',
    email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    email_confirmation_token VARCHAR(100) NOT NULL DEFAULT '',
    email_confirmation_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_userprofile_user FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Преподаватель
CREATE TABLE instructor (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    photo VARCHAR(255),
    bio TEXT NOT NULL DEFAULT '',
    CONSTRAINT fk_instructor_user FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Курс
CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    image VARCHAR(255),
    price NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Связующая таблица Курс-Преподаватель (Many-to-Many)
CREATE TABLE course_instructors (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    CONSTRAINT fk_course_instructors_course FOREIGN KEY (course_id) 
        REFERENCES course(id) ON DELETE CASCADE,
    CONSTRAINT fk_course_instructors_instructor FOREIGN KEY (instructor_id) 
        REFERENCES instructor(id) ON DELETE CASCADE,
    CONSTRAINT unique_course_instructor UNIQUE (course_id, instructor_id)
);

-- Ячейка расписания
CREATE TABLE timeslot (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    time_slot VARCHAR(5) NOT NULL,
    max_seats INTEGER NOT NULL DEFAULT 10,
    booked_seats INTEGER NOT NULL DEFAULT 0,
    room VARCHAR(100) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_timeslot_course FOREIGN KEY (course_id) 
        REFERENCES course(id) ON DELETE CASCADE,
    CONSTRAINT chk_timeslot_booked_seats CHECK (booked_seats >= 0),
    CONSTRAINT chk_timeslot_max_seats CHECK (max_seats >= 1),
    CONSTRAINT unique_timeslot_course_day_time UNIQUE (course_id, day_of_week, time_slot)
);

-- Запись на курс
CREATE TABLE enrollment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    student_name VARCHAR(100) NOT NULL,
    student_phone VARCHAR(20) NOT NULL,
    student_email VARCHAR(254) NOT NULL DEFAULT '',
    student_comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by INTEGER,
    approved_at TIMESTAMP WITH TIME ZONE,
    data_consent BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_enrollment_user FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) ON DELETE SET NULL,
    CONSTRAINT fk_enrollment_approved_by FOREIGN KEY (approved_by) 
        REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Связующая таблица Запись-Ячейка расписания (Many-to-Many)
CREATE TABLE enrollment_time_slots (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    timeslot_id INTEGER NOT NULL,
    CONSTRAINT fk_enrollment_time_slots_enrollment FOREIGN KEY (enrollment_id) 
        REFERENCES enrollment(id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_time_slots_timeslot FOREIGN KEY (timeslot_id) 
        REFERENCES timeslot(id) ON DELETE CASCADE,
    CONSTRAINT unique_enrollment_timeslot UNIQUE (enrollment_id, timeslot_id)
);

-- Новость
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    url VARCHAR(200) NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Создание индексов для улучшения производительности
CREATE INDEX idx_userprofile_user_id ON userprofile(user_id);
CREATE INDEX idx_instructor_user_id ON instructor(user_id);
CREATE INDEX idx_course_instructors_course_id ON course_instructors(course_id);
CREATE INDEX idx_course_instructors_instructor_id ON course_instructors(instructor_id);
CREATE INDEX idx_timeslot_course_id ON timeslot(course_id);
CREATE INDEX idx_timeslot_day_time ON timeslot(day_of_week, time_slot);
CREATE INDEX idx_enrollment_user_id ON enrollment(user_id);
CREATE INDEX idx_enrollment_created_at ON enrollment(created_at);
CREATE INDEX idx_enrollment_time_slots_enrollment_id ON enrollment_time_slots(enrollment_id);
CREATE INDEX idx_enrollment_time_slots_timeslot_id ON enrollment_time_slots(timeslot_id);
CREATE INDEX idx_news_created_at ON news(created_at);
CREATE INDEX idx_news_is_active ON news(is_active);

-- Комментарии к таблицам
COMMENT ON TABLE userprofile IS 'Профиль пользователя';
COMMENT ON TABLE instructor IS 'Преподаватель';
COMMENT ON TABLE course IS 'Курс';
COMMENT ON TABLE timeslot IS 'Ячейка расписания';
COMMENT ON TABLE enrollment IS 'Запись на курс';
COMMENT ON TABLE news IS 'Новость';