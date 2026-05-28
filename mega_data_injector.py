import sqlite3
import random

DB_PATH = 'db.sqlite3'

def mega_insert():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = WAL")

    # 1. Inject 100 Teachers
    print("👨‍🏫 Injecting 100 Teachers...")
    teachers = []
    wings = ['BOYS', 'GIRLS']
    sections = ['A', 'B', 'C', 'D', 'E']

    for i in range(1, 101):
        teachers.append((
            f"Teacher {i}", f"Father {i}", f"35202-{i:07d}-1", '1990-01-01',
            'Islam', f"0300{i:07d}", "Okara, Punjab",
            1, str(random.randint(1, 10)), random.choice(sections), random.choice(wings)
        ))

    cur.executemany("""
        INSERT INTO apsokara_teacher (full_name, father_name, cnic, dob, religion, contact, address, is_class_teacher, assigned_class, assigned_section, assigned_wing)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, teachers)

    # 2. Inject 90,000 Students
    print("🎓 Injecting 90,000 Students...")

    def student_generator():
        for i in range(1, 90001):
            cl = str(random.randint(1, 10))
            sec = random.choice(sections)
            wing = random.choice(wings)
            # Generating unique B-Forms and Roll Numbers
            b_form = f"35202-{i:07d}-1"
            roll = f"R-{i:05d}"

            yield (
                f"Student {i}", f"Father {i}", b_form, '2015-05-15',
                cl, sec, wing, roll, 'Pakistani', 'Punjab',
                'Islam', f"0321{i:07d}", "Okara, Pakistan"
            )

    gen = student_generator()
    chunk_size = 5000
    total_processed = 0

    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(gen))
            cur.executemany("""
                INSERT INTO apsokara_student
                (full_name, father_name, b_form, dob, student_class, student_section, wing, roll_number, nationality, province, religion, parents_phone, address)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, chunk)
            total_processed += len(chunk)
            print(f"--- Processed {total_processed} students")
        except StopIteration:
            if chunk:
                cur.executemany("""
                    INSERT INTO apsokara_student
                    (full_name, father_name, b_form, dob, student_class, student_section, wing, roll_number, nationality, province, religion, parents_phone, address)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, chunk)
            break

    conn.commit()
    conn.close()
    print(f"✅ MISSION ACCOMPLISHED: 90,000 Students & 100 Teachers Injected!")

if __name__ == "__main__":
    mega_insert()
