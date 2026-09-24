import os
import sys
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.clean_dataset import generate_and_clean_data
from models.academic_predictor import AcademicPredictor
from vision.attendance_detector import AttendanceDetector
from nlp.feedback_analyzer import FeedbackAnalyzer
from visualizer.dashboard import generate_analytics_dashboard

def run_full_pipeline():
    print("=" * 70)
    print("      SMART CLASSROOM & STUDENT ENGAGEMENT AI SUITE")
    print("=" * 70)

    # 1. Data Cleaning & Preparation
    print("\n[STEP 1/5] Data Preparation & RegEx Cleaning...")
    df = generate_and_clean_data()
    print(f"Loaded {len(df)} student profiles with cleaned names and academic records.")

    # 2. Machine Learning Training & Evaluation
    print("\n[STEP 2/5] Training Academic Predictor Models (Decision Tree, Regression, K-Means)...")
    predictor = AcademicPredictor()
    metrics = predictor.train()
    predictor.save()
    print(f"-> Decision Tree Classification Accuracy: {metrics['classification_accuracy']:.2%}")
    print(f"-> Linear Regression Exam Score R2 Score: {metrics['regression_r2']:.3f}")
    print("-> Most Influential Factors (Feature Importances):")
    for feat, imp in metrics["feature_importances"].items():
        print(f"     * {feat.replace('_', ' ').title()}: {imp:.1%}")

    # 3. Computer Vision Attendance & Face Detection
    print("\n[STEP 3/5] Running Computer Vision Attendance Detection...")
    detector = AttendanceDetector()
    demo_img, count = detector.run_on_synthetic_classroom()
    print(f"-> Automated Headcount: {count} students detected.")
    print(f"-> Annotated frame saved to: {demo_img}")

    # 4. Natural Language Processing Feedback Analysis
    print("\n[STEP 4/5] Analyzing Student Feedback Sentiment & WordCloud...")
    analyzer = FeedbackAnalyzer()
    _, nlp_summary = analyzer.analyze_dataset_feedback()
    wc_path, top_words = analyzer.generate_wordcloud()
    print(f"-> Classroom Mood Breakdown: {nlp_summary['positive_percentage']}% Positive | {nlp_summary['neutral_percentage']}% Neutral")
    print(f"-> Top Voice Keywords: {', '.join([w for w, _ in top_words[:5]])}")
    print(f"-> WordCloud saved to: {wc_path}")

    # 5. Visualizer Dashboard Generation
    print("\n[STEP 5/5] Synthesizing Multi-Panel Executive Analytics Dashboard...")
    dash_path = generate_analytics_dashboard()
    print(f"-> Complete analytics infographic generated: {dash_path}")

    print("\n" + "=" * 70)
    print("               SUITE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

def interactive_mode():
    predictor = AcademicPredictor()
    predictor.train()
    
    print("\n" + "=" * 55)
    print("       INTERACTIVE STUDENT OUTCOME PREDICTOR")
    print("=" * 55)
    
    try:
        hours = float(input("\nEnter Weekly Study Hours (e.g. 5.5): ").strip() or "5.5")
        att = float(input("Enter Attendance Percentage % (e.g. 85): ").strip() or "85")
        assign = float(input("Enter Assignments Completed (0 - 20, e.g. 14): ").strip() or "14")
        
        result = predictor.predict_student(hours, att, assign)
        print("\n--- Model Prediction Result ---")
        print(f"Academic Outcome    : {result['result']}")
        print(f"Pass Probability    : {result['pass_probability']}%")
        print(f"Estimated Exam Score: {result['predicted_score']} / 100")
        print(f"Student Profile     : {result['profile_category']}")
        print("-------------------------------")
    except Exception as e:
        print(f"Error reading inputs: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Classroom AI Suite")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive student predictor")
    parser.add_argument("--webcam", action="store_true", help="Launch live camera attendance tracker")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.webcam:
        detector = AttendanceDetector()
        detector.run_live_webcam()
    else:
        run_full_pipeline()
