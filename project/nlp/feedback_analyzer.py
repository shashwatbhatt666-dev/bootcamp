import os
import nltk
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from textblob import TextBlob
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class FeedbackAnalyzer:
    def __init__(self):
        # Ensure NLTK resources
        for res in ['punkt', 'punkt_tab', 'stopwords']:
            try:
                nltk.download(res, quiet=True)
            except Exception:
                pass
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {"the", "a", "an", "and", "in", "on", "of", "to", "for", "with", "is", "was"}

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.15:
            sentiment = "POSITIVE"
            emoji = "😊"
        elif polarity < -0.10:
            sentiment = "NEGATIVE"
            emoji = "😟"
        else:
            sentiment = "NEUTRAL"
            emoji = "😐"
            
        return {
            "text": text,
            "sentiment": sentiment,
            "emoji": emoji,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3)
        }

    def analyze_dataset_feedback(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
        df = pd.read_csv(data_path)
        feedbacks = df["feedback"].dropna().tolist()
        
        results = [self.analyze_sentiment(f) for f in feedbacks]
        res_df = pd.DataFrame(results)
        
        counts = res_df["sentiment"].value_counts().to_dict()
        avg_polarity = res_df["polarity"].mean()
        avg_subjectivity = res_df["subjectivity"].mean()
        
        summary = {
            "total_reviews": len(feedbacks),
            "sentiment_counts": counts,
            "positive_percentage": round((counts.get("POSITIVE", 0) / len(feedbacks)) * 100, 1),
            "neutral_percentage": round((counts.get("NEUTRAL", 0) / len(feedbacks)) * 100, 1),
            "negative_percentage": round((counts.get("NEGATIVE", 0) / len(feedbacks)) * 100, 1),
            "average_polarity": round(avg_polarity, 3),
            "average_subjectivity": round(avg_subjectivity, 3)
        }
        return res_df, summary

    def generate_wordcloud(self, data_path=None, output_path=None):
        if data_path is None:
            data_path = os.path.join(PROJECT_ROOT, "data", "student_records.csv")
        if output_path is None:
            output_path = os.path.join(PROJECT_ROOT, "data", "feedback_wordcloud.png")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df = pd.read_csv(data_path)
        combined_text = " ".join(df["feedback"].dropna().tolist())
        
        try:
            words = word_tokenize(combined_text.lower())
        except Exception:
            words = combined_text.lower().split()
            
        filtered = [w for w in words if w.isalpha() and w not in self.stop_words]
        freq = Counter(filtered)
        
        wc = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=60
        ).generate_from_frequencies(freq)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title("Classroom Feedback Themes WordCloud", fontsize=14, pad=15)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Feedback WordCloud saved to {output_path}")
        return output_path, freq.most_common(8)

if __name__ == "__main__":
    analyzer = FeedbackAnalyzer()
    _, summary = analyzer.analyze_dataset_feedback()
    print("Classroom Feedback Sentiment Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    img_path, top_words = analyzer.generate_wordcloud()
    print("\nTop Feedback Keywords:", top_words)
