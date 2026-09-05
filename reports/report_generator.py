from datetime import datetime, timezone

from reports.schemas import (
    AudienceAnalysis,
    AnalysisMetadata,
    ContentOpportunity,
    CrossPlatformAnalysis,
    DownstreamAgentContext,
    EvidenceRecord,
    FutureOutlook,
    GrowthAnalysis,
    HistoricalComparison,
    KeyDevelopment,
    PlatformAnalysis,
    PlatformReport,
    Prediction,
    RequestInfo,
    SentimentAnalysis,
    TrendIntelligence,
    TrendMetrics,
    TrendOverview,
)


class ReportGenerator:
    def generate_report(
        self,
        query,
        trend_scores,
        evidence,
        histories,
        minimum_sources=3,
        lookback_days=7,
        tools_used=None,
        iterations=0,
        generation_mode="deterministic",
    ):
        leader = max(trend_scores, key=lambda item: item["score"], default=None)
        timestamp = datetime.now(timezone.utc).isoformat()
        evidence_records = self._evidence_records(evidence)
        live_sources = [item for item in evidence if item.get("mode") == "live" and item.get("items")]
        previous = histories.get(query, [])
        previous_score = previous[-1].get("score") if previous else None
        current_score = leader["score"] if leader else 0
        score_change = round(current_score - previous_score, 2) if previous_score is not None else None
        current_status = self._status(leader["classification"] if leader else "Watch")
        previous_status = self._status(previous[-1].get("classification")) if previous else None
        confidence = min(1.0, len(live_sources) / max(1, minimum_sources))
        summary = self._summary(query, leader, len(live_sources), score_change)
        platform_analysis = self._platform_analysis(evidence, evidence_records)
        content_opportunities = self._content_opportunities(query)
        key_facts = self._key_facts(query, leader, evidence_records, live_sources)
        limitations = [item.get("fallback_reason") for item in evidence if item.get("fallback_reason")]
        if not live_sources:
            limitations.append("No live source returned usable evidence.")
        if len(live_sources) < minimum_sources:
            limitations.append("Cross-platform confidence is limited by insufficient live sources.")

        analysis = TrendIntelligence(
            request=RequestInfo(query=query, analysis_timestamp=timestamp, lookback_days=lookback_days),
            trend_overview=TrendOverview(
                topic=query,
                category="technology",
                subcategories=[],
                trend_status=current_status,
                trend_score=current_score,
                confidence=confidence,
                executive_summary=summary,
            ),
            why_trending=key_facts[:3],
            key_drivers=[f"{item['source']} contributed {len(item.get('items', []))} observed signals." for item in live_sources],
            trend_metrics=TrendMetrics(
                volume=leader.get("factors", {}).get("volume") if leader else None,
                growth_percentage=None,
                engagement=leader.get("factors", {}).get("engagement") if leader else None,
                cross_platform_score=leader.get("factors", {}).get("cross_platform") if leader else None,
                recency_score=leader.get("factors", {}).get("recency") if leader else None,
                authority_score=leader.get("factors", {}).get("authority") if leader else None,
                novelty_score=leader.get("factors", {}).get("novelty") if leader else None,
                overall_score=current_score,
            ),
            growth_analysis=self._growth_analysis(previous_score, score_change, lookback_days),
            platform_analysis=platform_analysis,
            cross_platform_analysis=CrossPlatformAnalysis(
                platform_count=len(live_sources),
                platforms=[item["source"] for item in live_sources],
                signal_strength=leader.get("factors", {}).get("cross_platform", 0) if leader else 0,
                explanation="Live source coverage is sufficient." if len(live_sources) >= minimum_sources else "Live source coverage is incomplete.",
            ),
            key_developments=self._key_developments(evidence_records),
            key_entities=[],
            related_topics=[],
            emerging_subtopics=[],
            audience_analysis=AudienceAnalysis(),
            sentiment_analysis=SentimentAnalysis(),
            evidence=evidence_records,
            risks_and_uncertainties=limitations,
            future_outlook=FutureOutlook(
                short_term="Unavailable without validated time-series data.",
                medium_term=None,
                long_term=None,
            ),
            prediction=None,
            content_opportunities=content_opportunities,
            recommended_content_angles=[item.angle for item in content_opportunities],
            historical_comparison=HistoricalComparison(
                available=previous_score is not None,
                previous_score=previous_score,
                score_change=score_change,
                previous_status=previous_status,
                current_status=current_status,
                trend_change=self._trend_change(score_change),
                explanation="Compared with stored history." if previous_score is not None else "No historical baseline is available.",
            ),
            downstream_agent_context=DownstreamAgentContext(
                content_generation_summary=summary,
                key_facts=key_facts,
                important_statistics=self._statistics(leader, live_sources),
                important_entities=[],
                recommended_angles=[item.angle for item in content_opportunities],
                must_not_claim=["Do not present unavailable metrics as facts.", *limitations],
            ),
            analysis_metadata=AnalysisMetadata(
                tools_used=tools_used or [],
                sources_checked=[item["source"] for item in evidence],
                iterations=iterations,
                analysis_completed=True,
                source_status={item["source"]: item.get("mode", "error") for item in evidence},
                generation_mode=generation_mode,
            ),
        )
        return analysis.model_dump(mode="json")

    def _status(self, classification):
        return {"Explosive": "Peak", "Emerging": "Rising", "Promising": "Stable", "Watch": "Declining"}.get(classification, "Stable")

    def _summary(self, query, leader, live_count, score_change):
        if not leader:
            return f"No verified live evidence was available for {query}."
        change = f" Score change: {score_change:+.2f}." if score_change is not None else " No historical baseline is available."
        return f"{query} has a measured score of {leader['score']} from {live_count} live sources.{change}"

    def _growth_analysis(self, previous_score, score_change, lookback_days):
        if previous_score is None:
            return GrowthAnalysis(direction="stable", percentage=None, period=f"{lookback_days} days", explanation="Unavailable without a historical baseline.")
        direction = "up" if score_change > 0 else "down" if score_change < 0 else "stable"
        return GrowthAnalysis(direction=direction, percentage=score_change, period=f"since previous analysis", explanation="Derived from stored trend scores; it is not a market growth percentage.")

    def _trend_change(self, score_change):
        if score_change is None:
            return None
        return "rising" if score_change > 0 else "declining" if score_change < 0 else "stable"

    def _evidence_records(self, evidence):
        records = []
        for source in evidence:
            for item in source.get("items", []):
                normalized = self._normalize_signal(source["source"], source.get("mode", "live"), item)
                records.append(EvidenceRecord(**normalized))
        return records

    def _normalize_signal(self, source, mode, item):
        if not isinstance(item, dict):
            return {"source": source, "mode": mode, "title": str(item), "metrics": {}}
        metrics = {key: item[key] for key in ("score", "num_comments", "stargazers_count", "forks_count", "engagement") if isinstance(item.get(key), (int, float))}
        url = item.get("html_url") or item.get("url")
        permalink = item.get("permalink")
        if not url and isinstance(permalink, str):
            url = permalink if permalink.startswith("http") else f"https://www.reddit.com{permalink}" if permalink.startswith("/") else None
        return {"source": source, "mode": mode, "title": item.get("title") or item.get("name") or item.get("description") or "Untitled signal", "url": url, "date": item.get("publishedAt") or item.get("created_at") or item.get("createdAt"), "relevance": "medium", "summary": item.get("description") or item.get("title"), "metrics": metrics}

    def _platform_analysis(self, evidence, records):
        result = {}
        for name in ("news", "reddit", "github"):
            source_records = [record for record in records if record.source == name]
            source = next((item for item in evidence if item["source"] == name), {})
            metrics = [record.metrics for record in source_records]
            result[name] = PlatformReport(
                available=source.get("mode") == "live" and bool(source_records),
                mentions=len(source_records) if name != "github" else None,
                engagement=sum(item.get("num_comments", 0) for item in metrics) if name == "reddit" and metrics else None,
                repositories=len(source_records) if name == "github" else None,
                stars=sum(item.get("stargazers_count", 0) for item in metrics) if name == "github" and metrics else None,
                forks=sum(item.get("forks_count", 0) for item in metrics) if name == "github" and metrics else None,
                key_findings=source.get("highlights", []),
                sources=source_records,
                failure_reason=source.get("fallback_reason") or source.get("error"),
            )
        return PlatformAnalysis(**result)

    def _key_developments(self, records):
        return [KeyDevelopment(title=item.title, description=item.summary, date=item.date, source=item.source, url=item.url, importance="medium") for item in records[:10]]

    def _content_opportunities(self, query):
        return [ContentOpportunity(platform="LinkedIn", format="post", angle=f"Practical implications of {query}", hook=f"What is changing in {query}?", target_audience="Technology professionals", reason="Translate observed signals into an evidence-led explainer.")]

    def _key_facts(self, query, leader, records, live_sources):
        facts = [f"{len(records)} source signals were collected for {query}.", f"{len(live_sources)} platforms returned live evidence."]
        if leader:
            facts.append(f"The deterministic trend score is {leader['score']}.")
        return facts

    def _statistics(self, leader, live_sources):
        if not leader:
            return []
        return [{"name": "trend_score", "value": leader["score"], "source": "deterministic trend engine"}, {"name": "live_source_count", "value": len(live_sources), "source": "tool observations"}]