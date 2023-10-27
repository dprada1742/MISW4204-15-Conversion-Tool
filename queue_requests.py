import time
from app.celery_app import convert_file
from app.crud import get_tasks_by_state
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@conversion-db.cfqplyz68hoi.us-east-1.rds.amazonaws.com:5432/conversion_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def perform_stress_test():
    db = SessionLocal()
    total_tasks_to_enqueue = 250  # Total number of unique tasks to enqueue
    tasks = get_tasks_by_state(db, "uploaded", total_tasks_to_enqueue)
    try:
        i = 0
        for task in tasks:
            convert_file.apply_async(args=[task.id, "mp4", "avi"]) 
            i += 1
            if i == 50:
                time.sleep(60)
                i=0

    except Exception as e:
        print(f'Error: {e}')
    
    db.close()


if __name__ == '__main__':
    perform_stress_test()
