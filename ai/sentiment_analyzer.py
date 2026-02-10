from textblob import TextBlob

def analyze_feedback(feedback_text):
    if not isinstance(feedback_text, str) or not feedback_text.strip():
        return "Neutral"  # Default for empty or invalid input

    try:
        blob = TextBlob(feedback_text)
        polarity = blob.sentiment.polarity

        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        return "Neutral"
