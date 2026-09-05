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


def calculate_observed_factors(evidence, previous_score=None, minimum_sources=3, query=""):
    """Derive transparent 0-100 factors from the evidence returned by tools."""
    valid_sources = [item for item in evidence if item.get("items") and item.get("mode", "live") == "live"]
    items = [entry for source in valid_sources for entry in source["items"]]
    source_count = len(valid_sources)
    total_items = len(items)
    query_terms = {term for term in query.lower().split() if len(term) > 2}
    engagement_values = []
    relevance_values = []
    recency_values = []
    unique_text = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        text = " ".join(str(item.get(key, "")) for key in ("title", "name", "description", "selftext"))
        text_terms = set(text.lower().split())
        if query_terms:
            relevance_values.append(len(query_terms & text_terms) / len(query_terms) * 100)
        unique_text.add(text.strip().lower())
        metrics = []
        for key in ("score", "num_comments", "stargazers_count", "forks_count", "engagement"):
            try:
                value = float(item.get(key, 0))
            except (TypeError, ValueError):
                value = 0
            if value > 0:
                metrics.append(min(100, 20 * (value ** 0.5)))
        if metrics:
            engagement_values.append(sum(metrics) / len(metrics))
        for key in ("publishedAt", "created_at", "createdAt"):
            raw_date = item.get(key)
            if raw_date:
                try:
                    from datetime import datetime, timezone
                    parsed = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                    age_days = max(0, (datetime.now(timezone.utc) - parsed).total_seconds() / 86400)
                    recency_values.append(max(0, min(100, 100 - age_days * 4)))
                except (TypeError, ValueError):
                    pass
    growth = 50 if previous_score is None else max(0, min(100, 50 + (previous_score - 50) * 0.5))
    engagement = sum(engagement_values) / len(engagement_values) if engagement_values else 35
    relevance = sum(relevance_values) / len(relevance_values) if relevance_values else 50
    recency = sum(recency_values) / len(recency_values) if recency_values else 45
    diversity = len(unique_text) / max(1, total_items) * 100
    return {
        "volume": min(100, total_items * 8 + diversity * 0.2),
        "growth": round(growth, 2),
        "engagement": round(min(100, engagement), 2),
        "cross_platform": round(min(100, source_count / max(1, minimum_sources) * 100), 2),
        "recency": round(recency, 2),
        "authority": round(sum(75 if source["source"] in {"news", "github"} else 55 for source in valid_sources) / max(1, source_count), 2),
        "novelty": round(min(100, relevance * 0.5 + diversity * 0.5), 2),
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