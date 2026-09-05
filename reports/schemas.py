from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequestInfo(StrictModel):
    query: str
    analysis_timestamp: str
    lookback_days: int = Field(ge=1)


class TrendOverview(StrictModel):
    topic: str
    category: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)
    trend_status: str
    trend_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    executive_summary: str


class TrendMetrics(StrictModel):
    volume: Optional[float] = Field(default=None, ge=0, le=100)
    growth_percentage: Optional[float] = None
    engagement: Optional[float] = Field(default=None, ge=0, le=100)
    cross_platform_score: Optional[float] = Field(default=None, ge=0, le=100)
    recency_score: Optional[float] = Field(default=None, ge=0, le=100)
    authority_score: Optional[float] = Field(default=None, ge=0, le=100)
    novelty_score: Optional[float] = Field(default=None, ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)


class GrowthAnalysis(StrictModel):
    direction: str
    percentage: Optional[float] = None
    period: Optional[str] = None
    explanation: str


class EvidenceRecord(StrictModel):
    source: str
    title: str
    url: Optional[str] = None
    date: Optional[str] = None
    relevance: Optional[str] = None
    summary: Optional[str] = None
    mode: str = "live"
    metrics: Dict[str, float] = Field(default_factory=dict)


class PlatformReport(StrictModel):
    available: bool
    mentions: Optional[int] = None
    engagement: Optional[float] = None
    repositories: Optional[int] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    sentiment: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    sources: List[EvidenceRecord] = Field(default_factory=list)
    failure_reason: Optional[str] = None


class PlatformAnalysis(StrictModel):
    news: PlatformReport
    reddit: PlatformReport
    github: PlatformReport


class CrossPlatformAnalysis(StrictModel):
    platform_count: int = Field(ge=0)
    platforms: List[str] = Field(default_factory=list)
    signal_strength: float = Field(ge=0, le=100)
    explanation: str


class KeyDevelopment(StrictModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    source: str
    url: Optional[str] = None
    importance: str


class AudienceAnalysis(StrictModel):
    primary_audience: List[str] = Field(default_factory=list)
    secondary_audience: List[str] = Field(default_factory=list)
    audience_interests: List[str] = Field(default_factory=list)
    audience_pain_points: List[str] = Field(default_factory=list)


class SentimentAnalysis(StrictModel):
    overall: Optional[str] = None
    positive_signals: List[str] = Field(default_factory=list)
    negative_signals: List[str] = Field(default_factory=list)
    controversies: List[str] = Field(default_factory=list)


class HistoricalComparison(StrictModel):
    available: bool
    previous_score: Optional[float] = None
    score_change: Optional[float] = None
    previous_status: Optional[str] = None
    current_status: str
    trend_change: Optional[str] = None
    explanation: str


class FutureOutlook(StrictModel):
    short_term: Optional[str] = None
    medium_term: Optional[str] = None
    long_term: Optional[str] = None


class Prediction(StrictModel):
    direction: str
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    prediction_type: str = "AI-generated prediction"


class ContentOpportunity(StrictModel):
    platform: str
    format: str
    angle: str
    hook: str
    target_audience: str
    reason: str


class DownstreamAgentContext(StrictModel):
    content_generation_summary: str
    key_facts: List[str] = Field(default_factory=list)
    important_statistics: List[Dict[str, Any]] = Field(default_factory=list)
    important_entities: List[str] = Field(default_factory=list)
    recommended_angles: List[str] = Field(default_factory=list)
    must_not_claim: List[str] = Field(default_factory=list)


class AnalysisMetadata(StrictModel):
    tools_used: List[str] = Field(default_factory=list)
    sources_checked: List[str] = Field(default_factory=list)
    iterations: int = Field(ge=0)
    analysis_completed: bool
    source_status: Dict[str, str] = Field(default_factory=dict)
    generation_mode: str


class TrendIntelligence(StrictModel):
    schema_version: str = "2.0"
    request: RequestInfo
    trend_overview: TrendOverview
    why_trending: List[str] = Field(default_factory=list)
    key_drivers: List[str] = Field(default_factory=list)
    trend_metrics: TrendMetrics
    growth_analysis: GrowthAnalysis
    platform_analysis: PlatformAnalysis
    cross_platform_analysis: CrossPlatformAnalysis
    key_developments: List[KeyDevelopment] = Field(default_factory=list)
    key_entities: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    emerging_subtopics: List[str] = Field(default_factory=list)
    audience_analysis: AudienceAnalysis
    sentiment_analysis: SentimentAnalysis
    evidence: List[EvidenceRecord] = Field(default_factory=list)
    risks_and_uncertainties: List[str] = Field(default_factory=list)
    future_outlook: FutureOutlook
    prediction: Optional[Prediction] = None
    content_opportunities: List[ContentOpportunity] = Field(default_factory=list)
    recommended_content_angles: List[str] = Field(default_factory=list)
    historical_comparison: HistoricalComparison
    downstream_agent_context: DownstreamAgentContext
    analysis_metadata: AnalysisMetadata


class AnalyzeResponse(StrictModel):
    success: bool
    analysis: TrendIntelligence
