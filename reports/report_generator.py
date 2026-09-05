from datetime import date

class ReportGenerator:
    """
    Generates structured reports based on analyzed trends.
    """
    def generate_report(self, query, trend_scores, evidence, histories):
        """
        Generate a JSON report of the analyzed trends.

        Args:
            emerging_trends (list): List of emerging trends.
            trend_scores (dict): Dictionary of trend scores.

        Returns:
            str: JSON-formatted report.
        """
        top_trends = sorted(trend_scores, key=lambda item: item["score"], reverse=True)
        emerging = [trend for trend in top_trends if trend["classification"] in ("Explosive", "Emerging")]
        return {
            "report_date": date.today().isoformat(),
            "query": query,
            "executive_summary": self._summary(top_trends, histories),
            "top_trends": top_trends,
            "emerging_trends": emerging,
            "platform_analysis": {item["source"]: item["items"] for item in evidence},
            "cross_platform_signals": [trend["topic"] for trend in top_trends if trend["source_count"] >= 3],
            "trend_predictions": [f"{trend['topic']} merits continued monitoring" for trend in emerging],
            "content_opportunities": [f"Explain practical {trend['topic']} use cases" for trend in emerging],
            "evidence": evidence,
        }

    def _summary(self, trends, histories):
        if not trends:
            return "No trend signals met the configured evidence threshold."
        leader = trends[0]
        previous = histories.get(leader["topic"], [])
        change = f" Historical score: {previous[-1]['score']}." if previous else ""
        return f"{leader['topic']} leads with a score of {leader['score']} across {leader['source_count']} sources.{change}"