const state = { report: null, filter: 'all', selectedScenario: null };

const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const duration = (value) => `${Number(value || 0).toFixed(2)}s`;

function setLoading(isLoading, label = 'Verificando resultados') {
  document.body.classList.toggle('is-loading', isLoading);
  document.querySelector('#refresh').disabled = isLoading;
  document.querySelector('#loading-label').textContent = label;
}

function renderSummary(summary) {
  const items = [
    ['Features', summary.features, 'executadas'], ['Cenarios', summary.scenarios, 'avaliados'],
    ['Passaram', summary.passed, 'cenarios aprovados'], ['Erros', summary.failed, 'requerem analise'],
    ['Steps', summary.steps, `${summary.skipped} ignorados`],
  ];
  const target = document.querySelector('#summary');
  target.replaceChildren();
  items.forEach(([label, value, note]) => {
    const card = document.querySelector('#metric-template').content.cloneNode(true);
    card.querySelector('p').textContent = label;
    card.querySelector('strong').textContent = value;
    card.querySelector('span').textContent = note;
    target.append(card);
  });
}

function renderRunOverview(report) {
  const { meta, summary, analytics, failures } = report;
  const hasResults = summary.scenarios > 0;
  const isHealthy = hasResults && !failures.length;
  const status = document.querySelector('#run-status');
  const caption = document.querySelector('#run-status-caption');
  const dot = document.querySelector('#run-status-dot');
  status.textContent = !hasResults ? 'Aguardando execucao' : isHealthy ? 'Suite aprovada' : 'Requer atencao';
  caption.textContent = !hasResults ? 'Execute uma suite para popular os indicadores.' : isHealthy
    ? `${summary.steps} steps concluidos sem falhas registradas.`
    : `${failures.length} ponto(s) precisam de analise antes da proxima entrega.`;
  dot.className = `status-orb ${isHealthy ? 'passed' : hasResults ? 'failed' : 'unknown'}`;
  document.querySelector('#run-environment').textContent = meta.environment || 'Nao informado';
  document.querySelector('#run-version').textContent = meta.version || 'Nao informada';
  const velocity = meta.duration ? (summary.steps / meta.duration) * 60 : 0;
  document.querySelector('#run-velocity').textContent = hasResults ? `${velocity.toFixed(1)} steps/min` : '-';
}

function renderIntelligence(report) {
  const { analytics, summary, failures } = report;
  if (!summary.scenarios) {
    document.querySelector('#pass-rate').textContent = '—';
    document.querySelector('#pass-rate-bar').style.width = '0%';
    document.querySelector('#quality-caption').textContent = 'Aguardando resultados reais.';
    document.querySelector('#step-distribution').textContent = 'Nenhum step executado.';
    document.querySelector('#slowest-name').textContent = 'Sem dados';
    document.querySelector('#slowest-meta').textContent = 'Aguardando execução.';
    document.querySelector('#failure-area').innerHTML = '<div class="empty-strip"><strong>Nenhum teste executado</strong><span>As falhas serão exibidas após uma execução real.</span></div>';
    return;
  }
  const rate = analytics.pass_rate;
  document.querySelector('#pass-rate').textContent = `${rate}%`;
  document.querySelector('#pass-rate-bar').style.width = `${rate}%`;
  document.querySelector('#quality-caption').textContent = `${summary.passed} de ${summary.scenarios} cenarios aprovados`;
  const statuses = analytics.step_statuses;
  const total = Object.values(statuses).reduce((sum, value) => sum + value, 0) || 1;
  document.querySelector('#step-distribution').innerHTML = ['passed', 'failed', 'skipped'].map((status) => `
    <div class="distribution-row ${status}"><span>${status === 'passed' ? 'Passaram' : status === 'failed' ? 'Falharam' : 'Ignorados'}</span><div class="distribution-track"><i style="width:${(statuses[status] / total) * 100}%"></i></div><strong>${statuses[status]}</strong></div>`).join('');
  const slowest = analytics.slowest_scenario;
  document.querySelector('#slowest-name').textContent = slowest ? slowest.name : 'Sem dados';
  document.querySelector('#slowest-meta').textContent = slowest ? `${duration(slowest.duration)} | media de ${duration(analytics.average_scenario_duration)}` : 'Execute uma suite para coletar dados.';
  const failureArea = document.querySelector('#failure-area');
  if (!failures.length) {
    failureArea.innerHTML = '<div class="success-strip"><strong>Execucao limpa</strong><span>Nenhuma falha registrada neste relatorio.</span></div>';
    return;
  }
  failureArea.innerHTML = `<div class="failure-strip"><div><p class="eyebrow">ATENCAO</p><h2>${failures.length} falha(s) para analisar</h2></div><div>${failures.slice(0, 3).map((failure) => `<p><strong>${escapeHtml(failure.scenario)}</strong> - ${escapeHtml(failure.step?.actual || 'Cenario falhou sem detalhe de step.')}</p>`).join('')}</div></div>`;
}

function renderDetail(feature, scenario) {
  const passedSteps = scenario.steps.filter((step) => step.status === 'passed').length;
  const failedSteps = scenario.steps.filter((step) => step.status === 'failed').length;
  const steps = scenario.steps.map((step) => `
    <article class="step ${step.status}">
      <div class="step-label"><span class="status ${step.status}">${escapeHtml(step.status)}</span><span>${duration(step.duration)}</span></div>
      <strong class="step-name">${escapeHtml(step.keyword)} ${escapeHtml(step.name)}</strong>
      ${step.status === 'failed' ? `<span class="step-error">${escapeHtml(step.actual || 'Step falhou sem mensagem adicional.')}</span>` : ''}
    </article>`).join('');
  document.querySelector('#detail-content').innerHTML = `
    <p class="eyebrow">${escapeHtml(feature.name)}</p>
    <div class="detail-heading"><h2 class="detail-title">${escapeHtml(scenario.name)}</h2><span class="status ${scenario.status}">${escapeHtml(scenario.status)}</span></div>
    <p class="detail-meta">${escapeHtml(scenario.location)} | ${duration(scenario.duration)}</p>
    <div class="detail-summary">
      <span>${scenario.steps.length} steps</span><span>${passedSteps} aprovados</span>
      ${failedSteps ? `<span class="has-error">${failedSteps} com erro</span>` : '<span>sem falhas</span>'}
    </div>
    <div class="step-list">${steps || '<p class="no-results">Sem steps registrados.</p>'}</div>`;
}

function renderFeatures(features) {
  const visibleFeatures = features.map((feature) => ({ ...feature, scenarios: feature.scenarios.filter((scenario) => state.filter === 'all' || scenario.status === state.filter) })).filter((feature) => feature.scenarios.length);
  const target = document.querySelector('#feature-list');
  target.replaceChildren();
  if (!visibleFeatures.length) { target.innerHTML = `<p class="no-results">${features.length ? 'Nenhum cenário corresponde ao filtro.' : 'Nenhum cenário executado nesta aplicação.'}</p>`; return; }
  visibleFeatures.forEach((feature) => {
    const featureElement = document.createElement('article');
    featureElement.className = `feature ${feature.status}`;
    featureElement.innerHTML = `<div class="feature-head"><div><p class="feature-name">${escapeHtml(feature.name)}</p><span class="scenario-location">${escapeHtml(feature.location)}</span></div><span class="status ${feature.status}">${escapeHtml(feature.status)}</span></div>`;
    feature.scenarios.forEach((scenario) => {
      const button = document.createElement('button');
      const scenarioId = `${feature.name}::${scenario.name}`;
      button.type = 'button';
      button.className = `scenario ${state.selectedScenario === scenarioId ? 'is-selected' : ''}`;
      button.setAttribute('aria-pressed', String(state.selectedScenario === scenarioId));
      button.innerHTML = `<span class="scenario-dot ${scenario.status}"></span><span class="scenario-name">${escapeHtml(scenario.name)}</span><span class="scenario-duration">${duration(scenario.duration)}</span>`;
      button.addEventListener('click', () => {
        state.selectedScenario = scenarioId;
        renderDetail(feature, scenario);
        renderFeatures(state.report.features);
      });
      featureElement.append(button);
    });
    target.append(featureElement);
  });
}

async function loadDashboard() {
  setLoading(true, 'Verificando resultados');
  try {
    const response = await fetch('/api/report', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Resposta ${response.status}`);
    state.report = await response.json();
    const { meta, summary, features, message } = state.report;
    document.querySelector('#report-notice').hidden = summary.scenarios > 0;
    document.querySelectorAll('.export-button').forEach((link) => { link.hidden = !summary.scenarios; });
    document.querySelector('#run-meta').textContent = message || `${meta.application || 'AutomacaoBDD'} | ${meta.environment || 'ambiente nao informado'} | ${meta.date || 'sem data'} | ${duration(meta.duration)}`;
    renderRunOverview(state.report);
    renderSummary(summary);
    renderIntelligence(state.report);
    renderFeatures(features);
  } catch (error) {
    document.querySelector('#run-meta').textContent = `Erro ao carregar relatorio: ${error.message}`;
    document.querySelectorAll('.export-button').forEach((link) => { link.hidden = true; });
  } finally {
    setLoading(false);
  }
}

document.querySelector('#refresh').addEventListener('click', loadDashboard);

const runForm = document.querySelector('#run-form');
const targetInput = document.querySelector('#target-url');
const runButton = document.querySelector('#run-button');
const runMessage = document.querySelector('#run-message');
const runLog = document.querySelector('#run-log');
let lastFinishedRun = null;
let pollTimer;
try { targetInput.value = localStorage.getItem('automacaobdd:local-target') || ''; } catch (_) { /* Optional. */ }

function showRunState(result) {
  runButton.disabled = result.status === 'running';
  runButton.textContent = result.status === 'running' ? 'Executando…' : 'Executar testes';
  runMessage.textContent = result.message || 'Aguardando execução.';
  runMessage.className = `target-message run-state-${result.status}`;
  runLog.hidden = !result.log_tail;
  runLog.textContent = result.log_tail || '';
  if (result.status === 'running') {
    clearTimeout(pollTimer);
    pollTimer = setTimeout(refreshRunStatus, 1800);
  } else if (result.run_id && lastFinishedRun !== result.run_id) {
    lastFinishedRun = result.run_id;
    loadDashboard();
  }
}

async function refreshRunStatus() {
  try {
    const response = await fetch('/api/run', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    showRunState(await response.json());
  } catch (error) {
    runMessage.textContent = `Não foi possível consultar o andamento: ${error.message}`;
    runMessage.className = 'target-message error';
    runButton.disabled = false;
  }
}

runForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearTimeout(pollTimer);
  runButton.disabled = true;
  runMessage.textContent = 'Iniciando o teste…';
  runMessage.className = 'target-message';
  runLog.hidden = true;
  try {
    const url = targetInput.value.trim();
    const response = await fetch('/api/run', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        url, suite: document.querySelector('#test-suite').value,
        expected_text: document.querySelector('#expected-text').value,
        show_browser: document.querySelector('#show-browser').checked,
      }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
    try { localStorage.setItem('automacaobdd:local-target', url); } catch (_) { /* Optional. */ }
    showRunState(result);
  } catch (error) {
    runButton.disabled = false;
    runMessage.textContent = `Não foi possível iniciar: ${error.message}`;
    runMessage.className = 'target-message error';
  }
});
refreshRunStatus();

document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => {
  state.filter = button.dataset.status;
  document.querySelectorAll('.filter').forEach((item) => item.classList.toggle('is-active', item === button));
  if (state.report) renderFeatures(state.report.features);
}));
loadDashboard();
