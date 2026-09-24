import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, mean_squared_error, r2_score

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AcademicPredictor:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.clf_model = DecisionTreeClassifier(max_depth=3, random_state=random_state)
        self.reg_model = LinearRegression()
        self.kmeans_model = KMeans(n_clusters=3, random_state=random_state, n_init=10)
        self.feature_cols = ["study_hours", "attendance", "assignments"]
        self.is_trained = False
        
    def train(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
        df = pd.read_csv(data_path)
        X = df[self.feature_cols]
        y_class = df["result"]
        y_score = df["exam_score"]
        
        # 1. Classification (Pass / Fail)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_class, test_size=0.2, random_state=self.random_state, stratify=y_class
        )
        self.clf_model.fit(X_train, y_train)
        y_pred = self.clf_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
        cr = classification_report(y_test, y_pred, labels=[0, 1], target_names=["Fail", "Pass"], zero_division=0)
        
        # 2. Regression (Predict Continuous Score)
        X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(
            X, y_score, test_size=0.2, random_state=self.random_state
        )
        self.reg_model.fit(X_tr_r, y_tr_r)
        score_preds = self.reg_model.predict(X_te_r)
        r2 = r2_score(y_te_r, score_preds)
        mse = mean_squared_error(y_te_r, score_preds)
        
        # 3. Unsupervised Clustering (Student Behavioral Profiles)
        self.kmeans_model.fit(X)
        df["cluster"] = self.kmeans_model.labels_
        
        cluster_map = {}
        for c in range(3):
            avg_score = df[df["cluster"] == c]["exam_score"].mean()
            cluster_map[c] = avg_score
        
        sorted_clusters = sorted(cluster_map.items(), key=lambda item: item[1])
        self.cluster_labels_dict = {
            sorted_clusters[0][0]: "Needs Support",
            sorted_clusters[1][0]: "Consistent Performer",
            sorted_clusters[2][0]: "High Achiever"
        }
        
        self.is_trained = True
        
        metrics = {
            "classification_accuracy": acc,
            "confusion_matrix": cm,
            "classification_report": cr,
            "regression_r2": r2,
            "regression_mse": mse,
            "feature_importances": dict(zip(self.feature_cols, self.clf_model.feature_importances_)),
            "cluster_centers": self.kmeans_model.cluster_centers_
        }
        return metrics
    
    def predict_student(self, study_hours, attendance, assignments):
        if not self.is_trained:
            raise ValueError("Model is not trained yet. Call train() first.")
        
        X_sample = pd.DataFrame([{
            "study_hours": study_hours,
            "attendance": attendance,
            "assignments": assignments
        }])
        
        pred_pass = self.clf_model.predict(X_sample)[0]
        pass_prob = self.clf_model.predict_proba(X_sample)[0][1]
        pred_score = self.reg_model.predict(X_sample)[0]
        raw_cluster = self.kmeans_model.predict(X_sample)[0]
        cluster_name = self.cluster_labels_dict.get(raw_cluster, "Standard")
        
        return {
            "result": "PASS" if pred_pass == 1 else "FAIL",
            "pass_probability": round(float(pass_prob) * 100, 1),
            "predicted_score": round(float(pred_score), 1),
            "profile_category": cluster_name
        }
        
    def save(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.join(PROJECT_ROOT, "models")
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(self.clf_model, os.path.join(model_dir, "clf_model.joblib"))
        joblib.dump(self.reg_model, os.path.join(model_dir, "reg_model.joblib"))
        joblib.dump(self.kmeans_model, os.path.join(model_dir, "kmeans_model.joblib"))
        print(f"Models successfully saved to {model_dir}")

if __name__ == "__main__":
    predictor = AcademicPredictor()
    metrics = predictor.train()
    print("Academic Predictor Trained Successfully!")
    print(f"Decision Tree Accuracy: {metrics['classification_accuracy']:.2%}")
    print(f"Linear Regression R2: {metrics['regression_r2']:.3f}")
    sample = predictor.predict_student(study_hours=6.5, attendance=88, assignments=15)
    print("\nSample Student Prediction:")
    print(sample)
