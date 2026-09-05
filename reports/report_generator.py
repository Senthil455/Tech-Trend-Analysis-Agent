from datetime import date

class ReportGenerator:
    """
    Generates structured reports based on analyzed trends.
    """
    def generate_report(self, query, trend_scores, evidence, histories, minimum_sources=3):
        """
        Generate a JSON report of the analyzed trends.

        Args:
            query (str): The analyzed topic.
            trend_scores (list): Calculated trend records.
            evidence (list): Source observations.
            histories (dict): Historical records keyed by topic.

        Returns:
            dict: Machine-readable trend report.
        """
        top_trends = sorted(trend_scores, key=lambda item: item["score"], reverse=True)
        emerging = [
            trend for trend in top_trends
            if trend["classification"] in ("Explosive", "Emerging")
            and trend["source_count"] >= minimum_sources
        ]
        report_date = date.today().isoformat()
        summary = self._summary(top_trends, histories)
        report = {
            "schema_version": "1.0",
            "report_date": report_date,
            "query": query,
            "executive_summary": summary,
            "top_trends": top_trends,
            "emerging_trends": emerging,
            "platform_analysis": {item["source"]: item["items"] for item in evidence},
            "cross_platform_signals": [
                trend["topic"] for trend in top_trends if trend["source_count"] >= minimum_sources
            ],
            "trend_predictions": [f"{trend['topic']} merits continued monitoring" for trend in emerging],
            "content_opportunities": [f"Explain practical {trend['topic']} use cases" for trend in emerging],
            "evidence": evidence,
        }
        report["platform_details"] = self._platform_details(evidence)
        report["downstream_input"] = self._downstream_input(
            query, report_date, summary, top_trends, evidence, minimum_sources, report
        )
        return report

    def _platform_details(self, evidence):
        return {
            item["source"]: {
                "mode": item.get("mode", "live"),
                "item_count": len(item.get("items", [])),
                "fallback_reason": item.get("fallback_reason"),
                "highlights": item.get("highlights", []),
            }
            for item in evidence
        }

    def _downstream_input(self, query, report_date, summary, trends, evidence, minimum_sources, report):
        leader = trends[0] if trends else None
        live_sources = sum(1 for item in evidence if item.get("mode") == "live" and item.get("items"))
        return {
            "contract": "tech-trend-analysis/v1",
            "task": "Use this trend intelligence as evidence for downstream content or research agents.",
            "topic": query,
            "report_date": report_date,
            "executive_summary": summary,
            "trend": leader,
            "confidence": {
                "live_source_count": live_sources,
                "minimum_sources_required": minimum_sources,
                "sufficient_cross_platform_evidence": live_sources >= minimum_sources,
            },
            "signals": [
                signal
                for source in evidence
                for signal in [self._normalize_signal(source["source"], source.get("mode", "live"), item) for item in source.get("items", [])]
            ],
            "recommendations": {
                "predictions": report["trend_predictions"],
                "content_opportunities": report["content_opportunities"],
                "cross_platform_topics": report["cross_platform_signals"],
            },
            "limitations": [
                source.get("fallback_reason")
                for source in evidence
                if source.get("fallback_reason")
            ],
            "guardrails": [
                "Separate observed facts from predictions.",
                "Cite live source signals when generating downstream content.",
                "Do not treat demo or fallback evidence as verified external fact.",
            ],
        }

    def _normalize_signal(self, source, mode, item):
        if not isinstance(item, dict):
            return {"source": source, "mode": mode, "title": str(item), "metrics": {}}
        metrics = {
            key: item[key]
            for key in ("score", "num_comments", "stargazers_count", "forks_count", "engagement")
            if key in item and isinstance(item[key], (int, float))
        }
        return {
            "source": source,
            "mode": mode,
            "title": item.get("title") or item.get("name") or item.get("description") or "Untitled signal",
            "url": item.get("url") or item.get("html_url"),
            "published_at": item.get("publishedAt") or item.get("created_at") or item.get("createdAt"),
            "metrics": metrics,
        }

    def _summary(self, trends, histories):
        if not trends:
            return "No trend signals met the configured evidence threshold."
        leader = trends[0]
        previous = histories.get(leader["topic"], [])
        change = f" Historical score: {previous[-1]['score']}." if previous else ""
        return f"{leader['topic']} leads with a score of {leader['score']} across {leader['source_count']} sources.{change}"