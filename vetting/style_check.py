def check_style(content):
    style_keywords = ["DYOR", "To the moon", "HODL", "Altseason"]
    style_score = sum(1 for kw in style_keywords if kw in content)
    return style_score >= 2
