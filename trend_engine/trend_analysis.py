def calculate_trend_score(volume, growth, engagement, cross_platform, recency, authority, novelty):
    """
    Calculate a trend score based on multiple factors.

    Args:
        volume (float): The volume of mentions or activity.
        growth (float): The growth rate of the trend.
        engagement (float): The level of user engagement.
        cross_platform (float): Cross-platform presence.
        recency (float): How recent the trend is.
        authority (float): Authority of the sources.
        novelty (float): Novelty of the trend.

    Returns:
        float: The calculated trend score.
    """
    values = [volume, growth, engagement, cross_platform, recency, authority, novelty]
    if any(value < 0 or value > 100 for value in values):
        raise ValueError("Trend factors must be between 0 and 100")
    score = (
        volume * 0.25 +
        growth * 0.20 +
        engagement * 0.15 +
        cross_platform * 0.15 +
        recency * 0.10 +
        authority * 0.10 +
        novelty * 0.05
    )
    return round(score, 2)


def classify_score(score):
    if score >= 85:
        return "Explosive"
    if score >= 70:
        return "Emerging"
    if score >= 60:
        return "Promising"
    return "Watch"

def detect_emerging_trends(trend_scores, threshold):
    """
    Detect emerging trends based on a threshold.

    Args:
        trend_scores (dict): A dictionary of topics and their scores.
        threshold (float): The minimum score to consider a trend as emerging.

    Returns:
        list: A list of emerging trends.
    """
    return [topic for topic, score in trend_scores.items() if score >= threshold]