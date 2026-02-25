import { getSelectedDomains, calculateAreaScore, calculateDomainScore, calculateOverallScore, saveLocal, loadLocal, buildDefaultSelection, validateSelection } from './helpers.js';

const LS_SELECTION = 'afs_selection';
const LS_ANSWERS = 'afs_answers';

let config = null;
let selectionState = null;
let answersByArea = null;

async function loadConfig(url) {
  const res = await fetch(url);
  return res.json();
}

function showModal() {
  const modalEl = document.getElementById('introModal');
  if (!modalEl) {
    // Fallback: if modal markup isn't present, continue to selection
    document.getElementById('selection-stage').classList.remove('d-none');
    return;
  }
  const bs = (window.bootstrap || window.Bootstrap || null);
  try {
    if (bs && typeof bs.Modal === 'function') {
      const modal = new bs.Modal(modalEl, { backdrop: 'static', keyboard: false });
      modal.show();
      document.getElementById('introContinueBtn').addEventListener('click', () => {
        modal.hide();
        document.getElementById('selection-stage').classList.remove('d-none');
      });
    } else {
      // Minimal fallback if Bootstrap JS isn't available
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
      document.getElementById('introContinueBtn').addEventListener('click', () => {
        modalEl.classList.remove('show');
        modalEl.style.display = 'none';
        document.getElementById('selection-stage').classList.remove('d-none');
      });
    }
  } catch (e) {
    console.warn('Intro modal initialization failed:', e);
    document.getElementById('selection-stage').classList.remove('d-none');
  }
}

function renderSelection() {
  const accordion = document.getElementById('domainsAccordion');
  accordion.innerHTML = '';

  let selectedDomainsCount = 0;
  let selectedAreasCount = 0;

  config.domains.forEach((domain, idx) => {
    const domSel = selectionState.domains[domain.id];
    const cardId = `dom-${domain.id}`;
    const collapseId = `collapse-${domain.id}`;

    const areaItems = domain.areas.map(area => {
      const checked = !!domSel.areas[area.id];
      if (checked) selectedAreasCount++;
      return `
        <div class="form-check ms-3">
          <input class="form-check-input area-checkbox" type="checkbox" data-domain="${domain.id}" data-area="${area.id}" ${checked ? 'checked' : ''}>
          <label class="form-check-label">${area.name}</label>
        </div>`;
    }).join('');

    if (domSel.selected) selectedDomainsCount++;

    const item = `
      <div class="accordion-item">
        <h2 class="accordion-header" id="${cardId}">
          <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="true" aria-controls="${collapseId}">
            <div class="form-check me-3">
              <input class="form-check-input domain-checkbox" type="checkbox" data-domain="${domain.id}" ${domSel.selected ? 'checked' : ''}>
            </div>
            <span class="fw-semibold">${domain.name}</span>
          </button>
        </h2>
        <div id="${collapseId}" class="accordion-collapse collapse show" aria-labelledby="${cardId}" data-bs-parent="#domainsAccordion">
          <div class="accordion-body">
            ${areaItems}
          </div>
        </div>
      </div>`;

    accordion.insertAdjacentHTML('beforeend', item);
  });

  document.getElementById('selDomains').textContent = selectedDomainsCount;
  document.getElementById('selAreas').textContent = selectedAreasCount;

  // Bind interactions
  accordion.querySelectorAll('.domain-checkbox').forEach(cb => {
    cb.addEventListener('change', e => {
      const domId = e.target.dataset.domain;
      const checked = e.target.checked;
      const domSel = selectionState.domains[domId];
      domSel.selected = checked;
      // enforce consistency: toggle all areas under domain
      for (const a of Object.keys(domSel.areas)) {
        domSel.areas[a] = checked ? true : domSel.areas[a];
      }
      updateSelectionUI();
    });
  });

  accordion.querySelectorAll('.area-checkbox').forEach(cb => {
    cb.addEventListener('change', e => {
      const domId = e.target.dataset.domain;
      const areaId = e.target.dataset.area;
      const checked = e.target.checked;
      const domSel = selectionState.domains[domId];
      domSel.areas[areaId] = checked;
      // auto-fix domain selection: if all areas unchecked, domain becomes unselected
      const areaCount = Object.values(domSel.areas).filter(Boolean).length;
      domSel.selected = areaCount > 0;
      updateSelectionUI();
    });
  });
}

function updateSelectionUI() {
  const isValid = validateSelection(selectionState);
  const err = document.getElementById('selectionErrors');
  const startBtn = document.getElementById('startAssessmentBtn');
  if (!isValid) {
    err.textContent = 'Please select at least one area.';
    err.classList.remove('d-none');
    startBtn.disabled = true;
  } else {
    err.classList.add('d-none');
    startBtn.disabled = false;
  }
  saveLocal(LS_SELECTION, selectionState);
  renderSelection();
}

function bindSelectionGlobalControls() {
  document.getElementById('btnSelectAll').addEventListener('click', () => {
    selectionState = buildDefaultSelection(config);
    updateSelectionUI();
  });
  document.getElementById('btnDeselectAll').addEventListener('click', () => {
    selectionState = { domains: {} };
    for (const d of config.domains) {
      selectionState.domains[d.id] = { selected: false, areas: {} };
      for (const a of d.areas) selectionState.domains[d.id].areas[a.id] = false;
    }
    updateSelectionUI();
  });
  document.getElementById('startAssessmentBtn').addEventListener('click', () => {
    const isValid = validateSelection(selectionState);
    if (!isValid) return;
    document.getElementById('selection-stage').classList.add('d-none');
    document.getElementById('runner-stage').classList.remove('d-none');
    renderRunner();
  });
}

function renderRunner() {
  const selectedDomains = getSelectedDomains(config, selectionState);
  const runner = document.getElementById('runnerContainer');
  runner.innerHTML = '';

  // stats
  const totalDomains = selectedDomains.length;
  const totalAreas = selectedDomains.reduce((acc, d) => acc + d.areas.length, 0);
  const totalQuestions = selectedDomains.reduce((acc, d) => acc + d.areas.reduce((a, ar) => a + ar.questions.length, 0), 0);
  const answered = Object.values(answersByArea).reduce((acc, arr) => acc + arr.filter(v => v === true || v === false).length, 0);
  document.getElementById('statDomains').textContent = totalDomains;
  document.getElementById('statAreas').textContent = totalAreas;
  document.getElementById('statAnswered').textContent = answered;
  document.getElementById('statTotal').textContent = totalQuestions;

  selectedDomains.forEach(domain => {
    const domBlock = document.createElement('div');
    domBlock.className = 'mb-4';
    const domHeader = document.createElement('h5');
    domHeader.textContent = domain.name;
    domBlock.appendChild(domHeader);

    domain.areas.forEach(area => {
      const areaKey = area.id;
      if (!answersByArea[areaKey]) answersByArea[areaKey] = new Array(area.questions.length).fill(null);
      const areaDiv = document.createElement('div');
      areaDiv.className = 'card mb-3';
      areaDiv.innerHTML = `<div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h6 class="mb-0">${area.name}</h6>
          <span class="badge bg-light text-dark">Score: <span data-area-score="${areaKey}">0.00</span> / 5</span>
        </div>
        ${area.questions.map((q, idx) => `
          <div class="d-flex align-items-center py-1 border-top">
            <div class="flex-grow-1">${q.text}</div>
            <div class="btn-group ms-3" role="group">
              <button class="btn btn-sm btn-outline-success" data-answer="yes" data-area="${areaKey}" data-index="${idx}">Yes</button>
              <button class="btn btn-sm btn-outline-danger" data-answer="no" data-area="${areaKey}" data-index="${idx}">No</button>
            </div>
          </div>
        `).join('')}
      </div>`;
      runner.appendChild(areaDiv);
    });

    runner.appendChild(domBlock);
  });

  // Bind answer buttons
  runner.querySelectorAll('button[data-answer]').forEach(btn => {
    btn.addEventListener('click', e => {
      const areaId = e.target.dataset.area;
      const idx = parseInt(e.target.dataset.index, 10);
      const val = e.target.dataset.answer === 'yes';
      answersByArea[areaId][idx] = val;
      // update area score display
      const score = calculateAreaScore(answersByArea[areaId]);
      const el = runner.querySelector(`[data-area-score="${areaId}"]`);
      if (el) el.textContent = score.toFixed(2);
      saveLocal(LS_ANSWERS, answersByArea);
      // update stats
      const answered = Object.values(answersByArea).reduce((acc, arr) => acc + arr.filter(v => v === true || v === false).length, 0);
      document.getElementById('statAnswered').textContent = answered;
    });
  });

  document.getElementById('backToSelectionBtn').onclick = () => {
    document.getElementById('runner-stage').classList.add('d-none');
    document.getElementById('selection-stage').classList.remove('d-none');
  };
  document.getElementById('finishAssessmentBtn').onclick = () => {
    renderReport();
  };
}

function renderReport() {
  const selectedDomains = getSelectedDomains(config, selectionState);
  const report = document.getElementById('reportContainer');
  report.innerHTML = '';

  const overall = calculateOverallScore(selectedDomains, answersByArea);
  document.getElementById('overallScore05').textContent = overall.toFixed(2);

  selectedDomains.forEach(domain => {
    const dScore = calculateDomainScore(domain.areas, answersByArea);
    const domDiv = document.createElement('div');
    domDiv.className = 'mb-4';
    domDiv.innerHTML = `<h5 class="mb-2">${domain.name} — <span class="text-muted">${dScore.toFixed(2)} / 5</span></h5>`;
    report.appendChild(domDiv);

    domain.areas.forEach(area => {
      const aScore = calculateAreaScore(answersByArea[area.id] || []);
      const areaDiv = document.createElement('div');
      areaDiv.className = 'ms-3 mb-2';
      areaDiv.textContent = `${area.name}: ${aScore.toFixed(2)} / 5`;
      report.appendChild(areaDiv);
    });
  });

  document.getElementById('runner-stage').classList.add('d-none');
  document.getElementById('report-stage').classList.remove('d-none');
}

async function main() {
  const root = document.getElementById('create-root');
  const cfgUrl = root.dataset.configUrl;
  config = await loadConfig(cfgUrl);
  selectionState = loadLocal(LS_SELECTION, buildDefaultSelection(config));
  answersByArea = loadLocal(LS_ANSWERS, {});

  // Skip modal if embedded in org_information page
  const skip = root?.dataset?.skipModal === 'true';
  if (!skip) {
    showModal();
  }
  renderSelection();
  bindSelectionGlobalControls();
}

// Ensure init runs regardless of current readyState
function onReady(fn) {
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(fn, 0);
  } else {
    window.addEventListener('DOMContentLoaded', fn);
  }
}

onReady(main);
