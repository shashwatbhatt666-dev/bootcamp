import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_analytics_dashboard(data_path=None, output_image=None):
    if data_path is None:
        data_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
    if output_image is None:
        output_image = os.path.join(PROJECT_ROOT, "data", "smart_classroom_analytics.png")
    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    df = pd.read_csv(data_path)
    
    # 1. Train models for metrics & visual components
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.cluster import KMeans
    
    X = df[["study_hours", "attendance", "assignments"]]
    y = df["result"]
    
    tree = DecisionTreeClassifier(max_depth=3, random_state=42)
    tree.fit(X, y)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X)
    
    # Setup Figure Layout (2 rows, 3 columns)
    fig = plt.figure(figsize=(18, 11), dpi=120)
    fig.patch.set_facecolor('#f8f9fa')
    plt.suptitle("Smart Classroom & Student Engagement AI Suite - Analytics Dashboard",
                 fontsize=18, fontweight='bold', y=0.98, color='#2d3436')
    
    # ----------------------------------------------------
    # Subplot 1: Study Hours vs Attendance (Pass / Fail)
    # ----------------------------------------------------
    ax1 = plt.subplot(2, 3, 1)
    pass_mask = df["result"] == 1
    ax1.scatter(df[pass_mask]["study_hours"], df[pass_mask]["attendance"],
                color='#00b894', label='Passed', s=70, alpha=0.85, edgecolors='white')
    ax1.scatter(df[~pass_mask]["study_hours"], df[~pass_mask]["attendance"],
                color='#d63031', label='At Risk / Failed', s=70, alpha=0.85, edgecolors='white')
    ax1.set_title("Student Academic Outcomes", fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel("Weekly Study Hours", fontsize=10)
    ax1.set_ylabel("Attendance Percentage (%)", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc='lower right')
    
    # ----------------------------------------------------
    # Subplot 2: Decision Tree Feature Importances
    # ----------------------------------------------------
    ax2 = plt.subplot(2, 3, 2)
    features = ["Study Hours", "Attendance", "Assignments"]
    importances = tree.feature_importances_
    bars = ax2.bar(features, importances, color=['#0984e3', '#6c5ce7', '#00cec9'], width=0.55)
    ax2.set_title("ML Predictive Factor Importances", fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel("Relative Importance", fontsize=10)
    ax2.set_ylim(0, max(importances) * 1.25)
    ax2.grid(axis='y', linestyle="--", alpha=0.5)
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 0.02, f"{h:.1%}",
                 ha='center', va='bottom', fontsize=9, fontweight='bold')
                 
    # ----------------------------------------------------
    # Subplot 3: Behavioral Profiles (K-Means Clustering)
    # ----------------------------------------------------
    ax3 = plt.subplot(2, 3, 3)
    colors = ['#fdcb6e', '#00cec9', '#e17055']
    cluster_names = {0: "Cluster A", 1: "Cluster B", 2: "Cluster C"}
    for c in range(3):
        c_data = df[df["cluster"] == c]
        ax3.scatter(c_data["study_hours"], c_data["exam_score"],
                    label=f"Profile {c+1}", color=colors[c], s=65, alpha=0.85, edgecolors='black', linewidth=0.5)
    
    centers = kmeans.cluster_centers_
    # Center study_hours vs approx exam_score
    ax3.set_title("Student Behavioral Clustering (K-Means)", fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel("Weekly Study Hours", fontsize=10)
    ax3.set_ylabel("Exam Score (0 - 100)", fontsize=10)
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend(loc='upper left')

    # ----------------------------------------------------
    # Subplot 4: Student Feedback Sentiment Distribution
    # ----------------------------------------------------
    ax4 = plt.subplot(2, 3, 4)
    from textblob import TextBlob
    sentiments = []
    for fb in df["feedback"].dropna():
        pol = TextBlob(fb).sentiment.polarity
        if pol > 0.15:
            sentiments.append("Positive")
        elif pol < -0.10:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")
            
    s_counts = pd.Series(sentiments).value_counts()
    palette = {'Positive': '#00b894', 'Neutral': '#fdcb6e', 'Negative': '#d63031'}
    c_list = [palette.get(s, '#b2bec3') for s in s_counts.index]
    
    wedges, texts, autotexts = ax4.pie(
        s_counts,
        labels=s_counts.index,
        autopct='%1.1f%%',
        colors=c_list,
        startangle=140,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
    ax4.set_title("Classroom Sentiment Breakdown", fontsize=12, fontweight='bold', pad=10)

    # ----------------------------------------------------
    # Subplot 5: Feedback Themes WordCloud
    # ----------------------------------------------------
    ax5 = plt.subplot(2, 3, (5, 6))
    all_feedback = " ".join(df["feedback"].dropna().tolist())
    try:
        sw = set(stopwords.words('english'))
        tokens = [w.lower() for w in word_tokenize(all_feedback) if w.isalpha() and w.lower() not in sw]
    except Exception:
        sw = {"the", "a", "an", "and", "in", "on", "of", "to", "for", "with", "is", "was"}
        tokens = [w.lower() for w in all_feedback.split() if w.isalpha() and w.lower() not in sw]
        
    freq = Counter(tokens)
    wc = WordCloud(width=900, height=350, background_color='#f8f9fa',
                   colormap='viridis', max_words=50).generate_from_frequencies(freq)
    ax5.imshow(wc, interpolation='bilinear')
    ax5.axis('off')
    ax5.set_title("Student Voice & Feedback Themes WordCloud", fontsize=12, fontweight='bold', pad=10)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_image, dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Unified analytics dashboard generated and saved to {output_image}")
    return output_image

if __name__ == "__main__":
    generate_analytics_dashboard()
