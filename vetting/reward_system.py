class RewardSystem:
    def __init__(self):
        self.reward = 0
        self.penalty = 0

    def evaluate_content(self, content):
        # Style alignment
        style_keywords = ["DYOR", "To the moon", "HODL", "Altseason"]
        style_score = sum(1 for kw in style_keywords if kw in content)
        if style_score >= 2:
            self.reward += 1
        else:
            self.penalty += 1

        # Fact-checking
        if check_facts(content):  # From fact_check.py
            self.reward += 1
        else:
            self.penalty += 1

        # Sentiment analysis
        if analyze_sentiment(content):  # From sentiment_analysis.py
            self.reward += 1
        else:
            self.penalty += 1

        # Engagement (simulated)
        if len(content) <= 280 and "?" in content:  # Questions increase engagement
            self.reward += 1

        return self.reward - self.penalty