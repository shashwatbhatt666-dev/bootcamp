import os
import re
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_and_clean_data(output_path=None):
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    np.random.seed(42)
    n_students = 60
    
    messy_names = [
        "  Rahul...Sharma ", "Aman///Kumar", "..Rohan@Singh..", " Vivek###Patel ", "Arjun$$Gupta",
        "  Priya..Verma/ ", "Ananya   Deshmukh..", "Kunal--Joshi ", "SNEHA//KAPOOR..", "Aditya   Rao",
        "Vikram##Mehta", "Neha...Shah//", "Tanvi$$Nair", "Karan   Malhotra..", "Pooja//Bansal ",
        "  Siddharth..Roy", "Divya###Sen ", "Rishi--Kapoor..", "Anjali   Iyer//", "Gaurav$$Pandey",
        "Deepak..Mishra ", "Meera//Chawla..", "Akash   Bhatia##", "Shruti..Saxena ", "Mohit$$Aggarwal",
        "Nidhi//Jain..", "Varun   Dutta ", "Simran###Kaur..", "Harsh..Trivedi ", "Kavita//Reddy",
        "Ayush   Gupta..", "Swati##Bose ", "Pranav$$Chopra", "Riya//Das..", "Naveen   Menon ",
        "Komal..Patil##", "Yash   Bansal..", "Isha//Seth ", "Alok$$Dubey..", "Tara   Pillai ",
        "Abhishek..Zade//", "Ashwini$$Mundaware ", "Gayatri   Gaikwad..", "Harshada##Shingane ", "Vaibhav//Kamble..",
        "Kedar   Adkar ", "Ashraf$$Pasha..", "Nandini..Bhende ", "Shankar//Rathod..", "Dilip   Kate ",
        "Pratiksha##Sanjay..", "Prajwal//Borkar ", "Shravani$$Sunil..", "Sakshi   Kale ", "Samruddhi..Sawant//",
        "Sayali$$Shinde..", "Shivani   Sawant ", "Suresh##Patil..", "Bhavna//Shah ", "Chetan   Verma$$"
    ]
    
    # Scale study hours, attendance, assignments to produce balanced pass/fail
    study_hours = np.round(np.random.uniform(0.5, 9.0, n_students), 1)
    attendance = np.random.randint(40, 100, n_students)
    assignments = np.random.randint(2, 20, n_students)
    
    # Passing threshold is 50
    exam_score = np.round(5.0 * study_hours + 0.35 * attendance + 1.2 * assignments + np.random.normal(0, 5, n_students), 1)
    exam_score = np.clip(exam_score, 15, 98)
    
    passed = (exam_score >= 50).astype(int)
    
    risk_level = []
    for sc in exam_score:
        if sc >= 75:
            risk_level.append("Low")
        elif sc >= 50:
            risk_level.append("Moderate")
        else:
            risk_level.append("High")
            
    sample_feedbacks = [
        "The practical sessions were super engaging and clear!",
        "Struggling a bit with recursion and tree math, need extra help.",
        "Loved the computer vision hands-on exercise with webcam!",
        "Excellent explanation of gradient descent and cost functions.",
        "Lectures feel a bit too fast in the afternoon slots.",
        "Really fun and practical bootcamp experience overall!",
        "Assignments are quite challenging but very rewarding.",
        "Could we get more code templates for neural networks?",
        "Great energy from instructors and very helpful lab mentors.",
        "The project was awesome and gave me real confidence in AI!"
    ]
    
    feedbacks = [sample_feedbacks[i % len(sample_feedbacks)] for i in range(n_students)]
    
    cleaned_names = []
    for nm in messy_names:
        c = nm.strip()
        c = re.sub(r'[^A-Za-z ]', ' ', c)
        c = re.sub(r'\s+', ' ', c).strip()
        cleaned_names.append(c)
        
    df = pd.DataFrame({
        "student_id": [f"STU{1001 + i}" for i in range(n_students)],
        "name": cleaned_names,
        "study_hours": study_hours,
        "attendance": attendance,
        "assignments": assignments,
        "exam_score": exam_score,
        "result": passed,
        "risk_level": risk_level,
        "feedback": feedbacks
    })
    
    df.to_csv(output_path, index=False)
    print(f"Generated and cleaned dataset saved to {output_path} ({len(df)} records).")
    return df

if __name__ == "__main__":
    generate_and_clean_data()
