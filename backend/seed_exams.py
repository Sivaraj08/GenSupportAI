import os
import sys

# Adjust Python path to import app correctly
sys.path.append(os.getcwd())

from app.database import engine, Base, SessionLocal
from app.models.exam_schedule import ExamSchedule

# Mock exam data for CSE, IT, and AIDS
mock_exams = [
    # CSE
    {"department": "cse", "course_code": "CS801", "course_name": "Artificial Intelligence", "exam_date": "2026-12-01", "exam_session": "FN"},
    {"department": "cse", "course_code": "CS802", "course_name": "Cryptography & Network Security", "exam_date": "2026-12-04", "exam_session": "AN"},
    {"department": "cse", "course_code": "CS803", "course_name": "Cloud Computing", "exam_date": "2026-12-08", "exam_session": "FN"},
    {"department": "cse", "course_code": "CS804", "course_name": "Professional Elective - Mobile App Development", "exam_date": "2026-12-11", "exam_session": "AN"},
    
    # IT
    {"department": "it", "course_code": "IT801", "course_name": "Web Technology", "exam_date": "2026-12-02", "exam_session": "FN"},
    {"department": "it", "course_code": "IT802", "course_name": "Mobile Computing", "exam_date": "2026-12-05", "exam_session": "AN"},
    {"department": "it", "course_code": "IT803", "course_name": "Software Project Management", "exam_date": "2026-12-09", "exam_session": "FN"},
    {"department": "it", "course_code": "IT804", "course_name": "Open Elective - Internet of Things", "exam_date": "2026-12-12", "exam_session": "AN"},
    
    # AIDS
    {"department": "aids", "course_code": "AD801", "course_name": "Deep Learning", "exam_date": "2026-12-03", "exam_session": "FN"},
    {"department": "aids", "course_code": "AD802", "course_name": "Big Data Analytics", "exam_date": "2026-12-06", "exam_session": "AN"},
    {"department": "aids", "course_code": "AD803", "course_name": "Natural Language Processing", "exam_date": "2026-12-10", "exam_session": "FN"},
    {"department": "aids", "course_code": "AD804", "course_name": "Computer Vision", "exam_date": "2026-12-14", "exam_session": "AN"}
]

def seed():
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if table already has data
        existing_count = db.query(ExamSchedule).count()
        if existing_count > 0:
            print(f"Table 'exam_schedules' already has {existing_count} records. Clearing for clean seed...")
            db.query(ExamSchedule).delete()
            db.commit()

        print("Seeding mock exam schedule records...")
        for exam in mock_exams:
            record = ExamSchedule(
                department=exam["department"],
                course_code=exam["course_code"],
                course_name=exam["course_name"],
                exam_date=exam["exam_date"],
                exam_session=exam["exam_session"]
            )
            db.add(record)
        
        db.commit()
        print(f"Successfully seeded {len(mock_exams)} exam schedule records.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding exams: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
