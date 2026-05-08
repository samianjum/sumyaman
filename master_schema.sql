CREATE TABLE IF NOT EXISTS "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "auth_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
CREATE TABLE IF NOT EXISTS "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE TABLE IF NOT EXISTS "apsokara_schoolnews" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content" text NOT NULL, "target_role" varchar(50) NOT NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "apsokara_student" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "full_name" varchar(100) NOT NULL, "father_name" varchar(100) NOT NULL, "b_form" varchar(20) NOT NULL UNIQUE, "dob" date NOT NULL, "student_class" varchar(10) NOT NULL, "student_section" varchar(10) NOT NULL, "wing" varchar(10) NOT NULL, "roll_number" varchar(20) NOT NULL UNIQUE, "nationality" varchar(50) NOT NULL, "province" varchar(20) NOT NULL, "religion" varchar(20) NOT NULL, "parents_phone" varchar(15) NOT NULL, "address" text NOT NULL, profile_pic VARCHAR(255));
CREATE TABLE IF NOT EXISTS "apsokara_subject" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS "apsokara_teacher" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "full_name" varchar(100) NOT NULL, "father_name" varchar(100) NOT NULL, "cnic" varchar(15) NOT NULL UNIQUE, "dob" date NOT NULL, "religion" varchar(20) NOT NULL, "contact" varchar(15) NOT NULL, "address" text NOT NULL, "is_class_teacher" bool NOT NULL, "assigned_class" varchar(10) NULL, "assigned_section" varchar(10) NULL, "assigned_wing" varchar(10) NOT NULL, profile_pic VARCHAR(255));
CREATE TABLE IF NOT EXISTS "apsokara_attendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "status" varchar(10) NOT NULL, "marked_by" text NOT NULL, "student_id" bigint NOT NULL REFERENCES "apsokara_student" ("id") DEFERRABLE INITIALLY DEFERRED, face_status varchar(20) DEFAULT 'unknown', edit_count INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS "apsokara_subjectassignment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_class" varchar(10) NOT NULL, "section" varchar(10) NOT NULL, "wing" varchar(10) NOT NULL, "subject_id" bigint NOT NULL REFERENCES "apsokara_subject" ("id") DEFERRABLE INITIALLY DEFERRED, "teacher_id" bigint NOT NULL REFERENCES "apsokara_teacher" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "apsokara_attendance_student_id_f60b30a7" ON "apsokara_attendance" ("student_id");
CREATE UNIQUE INDEX "apsokara_subjectassignment_subject_id_student_class_section_wing_2369cd83_uniq" ON "apsokara_subjectassignment" ("subject_id", "student_class", "section", "wing");
CREATE INDEX "apsokara_subjectassignment_subject_id_04e6f632" ON "apsokara_subjectassignment" ("subject_id");
CREATE INDEX "apsokara_subjectassignment_teacher_id_59a1ab0d" ON "apsokara_subjectassignment" ("teacher_id");
CREATE TABLE IF NOT EXISTS "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE TABLE IF NOT EXISTS "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE TABLE IF NOT EXISTS "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS "auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "first_name" varchar(150) NOT NULL);
CREATE TABLE IF NOT EXISTS "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE exams (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class_group TEXT DEFAULT 'All', is_active INTEGER DEFAULT 1, start_date DATE, end_date DATE, created_at DATETIME);
CREATE TABLE marks_entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    sub_id INTEGER,
    student_id INTEGER,
    total_marks INTEGER,
    obtained_marks REAL,
    remarks TEXT,
    UNIQUE(exam_id, sub_id, student_id)
);
CREATE TABLE IF NOT EXISTS "apsokara_dailydiary" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER,
    teacher_name TEXT,
    class TEXT,
    section TEXT,
    wing TEXT,
    subject TEXT,
    content TEXT,
    date_posted TEXT,
    is_scheduled INTEGER DEFAULT 0,
    attachments TEXT
);
CREATE TABLE IF NOT EXISTS "apsokara_studentleave" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id BIGINT NOT NULL,
    from_date DATE,
    to_date DATE,
    start_date TEXT,
    end_date TEXT,
    full_name TEXT,
    roll_number TEXT,
    class TEXT,
    section TEXT,
    wing TEXT,
    reason TEXT,
    attachment TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(student_id) REFERENCES apsokara_student(id)
);
CREATE TABLE exam_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            subject_id INTEGER,
            total_marks INTEGER DEFAULT 100,
            passing_marks INTEGER DEFAULT 33,
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        );
CREATE TABLE student_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INT,
            subject_id INT,
            student_id INT,
            total_marks INT,
            obtained_marks REAL,
            remarks TEXT,
            teacher_id INTEGER, is_locked INTEGER DEFAULT 0,
            UNIQUE(exam_id, subject_id, student_id)
        );
CREATE TABLE IF NOT EXISTS "apsokara_academicsession" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(20) NOT NULL, "is_current" bool NOT NULL, "promotion_start" date NULL, "promotion_end" date NULL);
CREATE TABLE IF NOT EXISTS "apsokara_classlock" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_class" varchar(10) NOT NULL, "section" varchar(10) NOT NULL, "wing" varchar(10) NOT NULL, "is_locked" bool NOT NULL, "locked_at" datetime NOT NULL, "session_id" bigint NOT NULL REFERENCES "apsokara_academicsession" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "apsokara_enrollment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_class" varchar(10) NOT NULL, "section" varchar(10) NOT NULL, "wing" varchar(10) NOT NULL, "is_active" bool NOT NULL, "session_id" bigint NOT NULL REFERENCES "apsokara_academicsession" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "apsokara_student" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "apsokara_classlock_session_id_8a126c18" ON "apsokara_classlock" ("session_id");
CREATE UNIQUE INDEX "apsokara_enrollment_student_id_session_id_c59430c5_uniq" ON "apsokara_enrollment" ("student_id", "session_id");
CREATE INDEX "apsokara_enrollment_session_id_ca6cf0af" ON "apsokara_enrollment" ("session_id");
CREATE INDEX "apsokara_enrollment_student_id_bd7de8a7" ON "apsokara_enrollment" ("student_id");
CREATE TABLE IF NOT EXISTS "apsokara_promotionaudit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "executed_at" datetime NOT NULL, "students_total" integer unsigned NOT NULL CHECK ("students_total" >= 0), "students_passed" integer unsigned NOT NULL CHECK ("students_passed" >= 0), "students_failed" integer unsigned NOT NULL CHECK ("students_failed" >= 0), "students_graduated" integer unsigned NOT NULL CHECK ("students_graduated" >= 0), "session_id" bigint NOT NULL REFERENCES "apsokara_academicsession" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "apsokara_promotionsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start_date" datetime NOT NULL, "end_date" datetime NOT NULL, "passing_percentage" decimal NOT NULL, "executed" bool NOT NULL, "executed_at" datetime NULL, "session_id" bigint NOT NULL UNIQUE REFERENCES "apsokara_academicsession" ("id") DEFERRABLE INITIALLY DEFERRED, "target_session_id" bigint NOT NULL REFERENCES "apsokara_academicsession" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "apsokara_promotionaudit_session_id_04771a14" ON "apsokara_promotionaudit" ("session_id");
CREATE INDEX "apsokara_promotionsettings_target_session_id_04a34843" ON "apsokara_promotionsettings" ("target_session_id");
CREATE TABLE IF NOT EXISTS "super_admin_schoolclient" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "slug" varchar(50) NOT NULL UNIQUE, "db_name" varchar(100) NOT NULL UNIQUE, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "logo" varchar(100) NULL, "school_type" varchar(20) NOT NULL);
