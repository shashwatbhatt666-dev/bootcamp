import sqlite3
import os
import json
import pandas as pd
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "classroom.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            study_hours REAL NOT NULL,
            attendance INTEGER NOT NULL,
            assignments INTEGER NOT NULL,
            exam_score REAL NOT NULL,
            result INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Attendance & Engagement Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            headcount INTEGER NOT NULL,
            source TEXT DEFAULT 'webcam',
            notes TEXT,
            engagement_score REAL DEFAULT 85.0,
            active_count INTEGER DEFAULT 0,
            distracted_count INTEGER DEFAULT 0,
            alerts TEXT
        )
    ''')

    # Add columns if migrating existing DB
    for col, col_type in [
        ("engagement_score", "REAL DEFAULT 85.0"),
        ("active_count", "INTEGER DEFAULT 0"),
        ("distracted_count", "INTEGER DEFAULT 0"),
        ("alerts", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE attendance_sessions ADD COLUMN {col} {col_type}")
        except Exception:
            pass
    
    # 3. Behavior logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classroom_behavior_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            headcount INTEGER NOT NULL,
            handrise INTEGER DEFAULT 0,
            look_forward INTEGER DEFAULT 0,
            read INTEGER DEFAULT 0,
            sleep INTEGER DEFAULT 0,
            stand INTEGER DEFAULT 0,
            turn_head INTEGER DEFAULT 0,
            using_device INTEGER DEFAULT 0,
            write INTEGER DEFAULT 0,
            engagement_score REAL DEFAULT 85.0,
            source TEXT DEFAULT 'Live Vision'
        )
    ''')

    # 4. Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            comment TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL,
            subjectivity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # 5. Predictions Log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_hours REAL,
            attendance REAL,
            assignments REAL,
            predicted_result TEXT,
            pass_probability REAL,
            predicted_score REAL,
            profile_category TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # Populate initial students from student_records.csv if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    if count == 0:
        csv_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, r in df.iterrows():
                cursor.execute('''
                    INSERT OR IGNORE INTO students 
                    (student_id, name, study_hours, attendance, assignments, exam_score, result, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    r["student_id"], r["name"], float(r["study_hours"]),
                    int(r["attendance"]), int(r["assignments"]), float(r["exam_score"]),
                    int(r["result"]), str(r["risk_level"])
                ))
            
            # Populate initial feedback
            for _, r in df.iterrows():
                if "feedback" in r and pd.notna(r["feedback"]):
                    cursor.execute('''
                        INSERT INTO feedback (student_name, comment, sentiment, polarity, subjectivity, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        r["name"], r["feedback"], r.get("sentiment", "POSITIVE"),
                        float(r.get("polarity", 0.5)), float(r.get("subjectivity", 0.5)),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
            conn.commit()

    # Populate sample behavior log if empty
    cursor.execute("SELECT COUNT(*) FROM classroom_behavior_logs")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO classroom_behavior_logs 
            (timestamp, headcount, handrise, look_forward, read, sleep, stand, turn_head, using_device, write, engagement_score, source)
            VALUES (?, 24, 6, 12, 4, 1, 1, 2, 0, 3, 87.5, 'Kaggle Model Baseline')
        ''', (now,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized & upgraded at:", DB_PATH)
