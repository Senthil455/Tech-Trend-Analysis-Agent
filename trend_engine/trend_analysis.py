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


def classify_score(score, emerging_threshold=70, minimum_score=60):
    if score >= 85:
        return "Explosive"
    if score >= emerging_threshold:
        return "Emerging"
    if score >= minimum_score:
        return "Promising"
    return "Watch"


def calculate_observed_factors(evidence, previous_score=None):
    """Derive transparent 0-100 factors from the evidence returned by tools."""
    valid_sources = [item for item in evidence if item.get("items")]
    items = [entry for source in valid_sources for entry in source["items"]]
    source_count = len(valid_sources)
    total_items = len(items)
    metadata_items = sum(
        1 for item in items if isinstance(item, dict) and any(key in item for key in ("score", "num_comments", "stargazers_count", "engagement"))
    )
    growth = 50 if previous_score is None else max(0, min(100, 50 + (previous_score - 50) * 0.5))
    return {
        "volume": min(100, total_items * 10),
        "growth": round(growth, 2),
        "engagement": round(min(100, 50 + metadata_items / max(1, total_items) * 50), 2),
        "cross_platform": round(min(100, source_count / 3 * 100), 2),
        "recency": 50,
        "authority": round(sum(75 if source["source"] in {"news", "github"} else 55 for source in valid_sources) / max(1, source_count), 2),
        "novelty": 50,
    }

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