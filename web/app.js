const form = document.querySelector('#analysisForm');
const input = document.querySelector('#query');
const button = document.querySelector('#analyzeButton');
const note = document.querySelector('#formNote');
const emptyState = document.querySelector('#emptyState');
const results = document.querySelector('#results');

const apiStatus = document.querySelector('#apiStatus');
const score = document.querySelector('#score');
const scoreBar = document.querySelector('#scoreBar');
const classification = document.querySelector('#classification');
const sourceCount = document.querySelector('#sourceCount');
const summary = document.querySelector('#summary');
const signalText = document.querySelector('#signalText');
const reportTitle = document.querySelector('#reportTitle');
const reportDate = document.querySelector('#reportDate');
const trendList = document.querySelector('#trendList');
const trendCount = document.querySelector('#trendCount');
const opportunityList = document.querySelector('#opportunityList');
const evidenceList = document.querySelector('#evidenceList');
const traceList = document.querySelector('#traceList');
const whyTrending = document.querySelector('#whyTrending');
const keyDrivers = document.querySelector('#keyDrivers');
const metricsTable = document.querySelector('#metricsTable');
const growthAnalysis = document.querySelector('#growthAnalysis');
const platformDetails = document.querySelector('#platformDetails');
const developments = document.querySelector('#developments');
const sentimentOutlook = document.querySelector('#sentimentOutlook');
const downstreamSummary = document.querySelector('#downstreamSummary');
const mustNotClaim = document.querySelector('#mustNotClaim');

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
}[char]));

function setLoading(loading) {
  button.disabled = loading;
  button.querySelector('span').textContent = loading ? 'Investigating...' : 'Run analysis';
  if (loading) {
    note.classList.remove('error');
    note.textContent = 'The agent is collecting signals across enabled sources.';
  } else if (!note.classList.contains('error')) {
    note.textContent = 'Demo mode is ready. Results are generated locally.';
  }
}

function renderReport(payload) {
  const report = payload.analysis || payload;
  const overview = report.trend_overview || {};
  const metrics = report.trend_metrics || {};
  const scoreValue = Number(metrics.overall_score || overview.trend_score || 0);
  score.textContent = scoreValue.toFixed(1);
  scoreBar.style.width = `${Math.min(100, scoreValue)}%`;
  classification.textContent = overview.trend_status || 'Unavailable';
  classification.className = `badge ${String(overview.trend_status || 'watch').toLowerCase()}`;
  sourceCount.textContent = `${report.cross_platform_analysis?.platform_count || 0} live sources`;
  signalText.textContent = report.cross_platform_analysis?.platform_count >= 3 ? 'Cross-platform signal detected' : 'More sources needed for confidence';
  summary.textContent = overview.executive_summary || 'No summary available.';
  reportTitle.textContent = overview.topic || report.request?.query || 'Trend report';
  reportDate.textContent = report.request?.analysis_timestamp ? `· ${report.request.analysis_timestamp.slice(0, 10)}` : '';

  const trend = overview.topic ? [{ topic: overview.topic, score: scoreValue, classification: overview.trend_status, source_count: report.cross_platform_analysis?.platform_count || 0 }] : [];
  trendCount.textContent = trend.length;
  trendList.innerHTML = trend.length ? trend.map((item, index) => `
    <div class="trend-row"><span class="trend-rank">0${index + 1}</span><div><strong>${escapeHtml(item.topic)}</strong><small>${escapeHtml(item.classification)} · ${item.source_count} live sources</small></div><b>${Number(item.score).toFixed(1)}</b></div>
  `).join('') : '<p class="muted">No trend overview returned.</p>';

  opportunityList.innerHTML = (report.content_opportunities || []).map((item) => `<li><span>↗</span><strong>${escapeHtml(item.platform)} · ${escapeHtml(item.format)}</strong><br>${escapeHtml(item.angle)}<small>${escapeHtml(item.hook)}</small></li>`).join('') || '<li class="muted">No opportunities returned.</li>';

  evidenceList.innerHTML = (report.evidence || []).map((source) => `
    <div class="evidence-row"><span class="source-icon">${escapeHtml(source.source.slice(0, 1).toUpperCase())}</span><div><strong>${escapeHtml(source.source)} <mark class="mode-${escapeHtml(source.mode || 'live')}">${escapeHtml(source.mode || 'live')}</mark></strong><small>${escapeHtml(source.title)} · ${escapeHtml(source.relevance || 'unavailable')}</small>${source.url ? `<a class="resource-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>` : '<small class="no-link">Reference link unavailable</small>'}</div></div>
  `).join('') || '<p class="muted">No evidence returned.</p>';

  traceList.innerHTML = (report.analysis_metadata?.tools_used || []).map((tool, index) => `<li><span class="trace-index">${index + 1}</span><div><strong>tool action</strong><small>${escapeHtml(tool)}</small></div></li>`).join('') || '<li class="muted">No tool actions recorded.</li>';

  const list = (items) => items?.length ? items.map((item) => `<li>${escapeHtml(item)}</li>`).join('') : '<li class="muted">Unavailable from collected evidence.</li>';
  whyTrending.innerHTML = list(report.why_trending);
  keyDrivers.innerHTML = list(report.key_drivers);
  metricsTable.innerHTML = Object.entries(metrics).map(([key, value]) => `<div><span>${escapeHtml(key.replaceAll('_', ' '))}</span><strong>${value === null || value === undefined ? 'unavailable' : escapeHtml(value)}</strong></div>`).join('');
  growthAnalysis.innerHTML = `<strong>Growth: ${escapeHtml(report.growth_analysis?.direction || 'unavailable')}</strong><br>${escapeHtml(report.growth_analysis?.explanation || 'No growth interpretation available.')}`;
  platformDetails.innerHTML = Object.entries(report.platform_analysis || {}).map(([name, item]) => `<div class="platform-detail"><strong>${escapeHtml(name)}</strong><span>${item.available ? 'available' : 'unavailable'} · ${item.mentions ?? item.repositories ?? 0} records</span><small>${escapeHtml(item.failure_reason || item.key_findings?.[0] || 'No additional finding')}</small></div>`).join('');
  developments.innerHTML = (report.key_developments || []).slice(0, 6).map((item) => `<div class="development"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.source)} · ${escapeHtml(item.date || 'date unavailable')}</small>${item.url ? `<a class="resource-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">Open reference ↗</a>` : '<small class="no-link">Reference link unavailable</small>'}</div>`).join('') || '<p class="muted">No verified developments returned.</p>';
  sentimentOutlook.innerHTML = `<p><strong>Sentiment:</strong> ${escapeHtml(report.sentiment_analysis?.overall || 'unavailable')}</p><p><strong>Short term:</strong> ${escapeHtml(report.future_outlook?.short_term || 'unavailable')}</p>`;
  downstreamSummary.textContent = report.downstream_agent_context?.content_generation_summary || 'No downstream context available.';
  mustNotClaim.innerHTML = list(report.downstream_agent_context?.must_not_claim);

  emptyState.hidden = true;
  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function checkApi() {
  try {
    const response = await fetch('/health');
    if (!response.ok) throw new Error('offline');
    apiStatus.textContent = 'API connected';
  } catch {
    apiStatus.textContent = 'API unavailable';
    document.querySelector('.status-dot').classList.add('offline');
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (!query) return input.focus();
  setLoading(true);
  try {
    const response = await fetch(`/analyze?query=${encodeURIComponent(query)}`, { method: 'POST' });
    if (!response.ok) throw new Error('Analysis failed');
    renderReport(await response.json());
  } catch (error) {
    note.textContent = 'Could not reach the agent. Make sure the FastAPI server is running.';
    note.classList.add('error');
  } finally {
    setLoading(false);
  }
});

document.querySelectorAll('[data-query]').forEach((suggestion) => {
  suggestion.addEventListener('click', () => { input.value = suggestion.dataset.query; input.focus(); });
});

document.querySelector('#newAnalysis').addEventListener('click', () => {
  results.hidden = true;
  emptyState.hidden = false;
  input.focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

checkApi();
