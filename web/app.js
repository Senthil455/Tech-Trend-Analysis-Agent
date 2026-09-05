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

function renderReport(report) {
  const leader = report.top_trends?.[0] || {};
  const scoreValue = Number(leader.score || 0);
  score.textContent = scoreValue.toFixed(1);
  scoreBar.style.width = `${Math.min(100, scoreValue)}%`;
  classification.textContent = leader.classification || 'Watch';
  classification.className = `badge ${String(leader.classification || 'watch').toLowerCase()}`;
  sourceCount.textContent = `${leader.source_count || 0} sources`;
  signalText.textContent = leader.evidence_sufficient ? 'Cross-platform signal detected' : 'More sources needed for confidence';
  summary.textContent = report.executive_summary || 'No summary available.';
  reportTitle.textContent = report.query || 'Trend report';
  reportDate.textContent = report.report_date ? `· ${report.report_date}` : '';

  const trends = report.emerging_trends || [];
  trendCount.textContent = trends.length;
  trendList.innerHTML = trends.length ? trends.map((trend, index) => `
    <div class="trend-row"><span class="trend-rank">0${index + 1}</span><div><strong>${escapeHtml(trend.topic)}</strong><small>${escapeHtml(trend.classification)} · ${trend.source_count} sources</small></div><b>${Number(trend.score).toFixed(1)}</b></div>
  `).join('') : '<p class="muted">No emerging trends met the configured threshold.</p>';

  opportunityList.innerHTML = (report.content_opportunities || []).map((item) => `<li><span>↗</span>${escapeHtml(item)}</li>`).join('') || '<li class="muted">No opportunities returned.</li>';

  evidenceList.innerHTML = (report.evidence || []).map((source) => `
    <div class="evidence-row"><span class="source-icon">${escapeHtml(source.source.slice(0, 1).toUpperCase())}</span><div><strong>${escapeHtml(source.source)}</strong><small>${source.items.length} signal${source.items.length === 1 ? '' : 's'} collected</small></div><span class="evidence-count">${source.items.length}</span></div>
  `).join('') || '<p class="muted">No evidence returned.</p>';

  traceList.innerHTML = (report.react_trace || []).map((step, index) => `
    <li><span class="trace-index">${index + 1}</span><div><strong>${escapeHtml(step.step)}</strong><small>${escapeHtml(step.decision || step.tool || `${step.sources || 0} sources observed`)}</small></div></li>
  `).join('');

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
