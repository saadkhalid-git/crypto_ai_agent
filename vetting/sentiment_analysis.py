from textblob import TextBlob


def analyze_sentiment(content):
    analysis = TextBlob(content)
    return analysis.sentiment.polarity > 0  # Ensure positive/neutral sentiment
