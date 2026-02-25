/**
 * Assessment Creator – Client-Side SPA  (Full Flow)
 *
 * Flow:  Intro Modal → Org Info → Domain/Area Selection → Question Runner → Review Report → Submit to Server → Redirect
 *
 * This mirrors the seed_completed_assessment.py script but lets the
 * user choose which areas to include and interactively answer Yes/No.
 *
 * After the user reviews the inline preview the assessment is POSTed
 * to the server which creates the Assessment + Responses, runs
 * ScoringService, and returns the ID.  The client then redirects to
 * the canonical /assessment/<id>/report page.
 */

import {
  getSelectedDomains,
  calculateAreaScore,
  calculateDomainScore,
  calculateOverallScore,
  saveLocal,
  loadLocal,
  buildDefaultSelection,
  validateSelection
} from './helpers.js';

/* ------------------------------------------------------------------ */
/*  Constants                                                         */
/* ------------------------------------------------------------------ */
const LS_SELECTION = 'afs_selection';
const LS_ANSWERS   = 'afs_answers';
const LS_ORGINFO   = 'afs_orginfo';

/* ------------------------------------------------------------------ */
/*  State                                                             */
/* ------------------------------------------------------------------ */
let config         = null;   // parsed assessment_config.json
let selectionState = null;   // { domains: { [domId]: { selected, areas } } }
let answersByArea  = null;   // { [areaId]: [bool|null, …] }
let orgInfo        = null;   // { organization_name, first_name, … }
let lang           = 'en';
let submitUrl      = '';     // server endpoint for final submission
let currentStep    = 'org';  // 'org' | 'select' | 'runner' | 'report'

/* ------------------------------------------------------------------ */
/*  Language helpers                                                   */
/* ------------------------------------------------------------------ */

function detectLang() {
  const root = document.getElementById('create-root');
  if (root?.dataset?.lang) return root.dataset.lang;
  const htmlLang = document.documentElement.lang;
  if (htmlLang) return htmlLang.substring(0, 2).toLowerCase();
  return 'en';
}

function t(obj) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  return obj[lang] || obj.en || obj.pt || '';
}

function yesNoLabels() {
  return lang === 'pt'
    ? { yes: 'Sim', no: 'Não' }
    : { yes: 'Yes', no: 'No' };
}

/* ------------------------------------------------------------------ */
/*  Step Indicator                                                     */
/* ------------------------------------------------------------------ */

const STEPS = ['org', 'select', 'runner', 'report'];
const STAGE_IDS = {
  org:    'org-info-stage',
  select: 'selection-stage',
  runner: 'runner-stage',
  report: 'report-stage',
};

function showStep(step) {
  currentStep = step;
  // Hide all stages
  for (const sid of Object.values(STAGE_IDS)) {
    const el = document.getElementById(sid);
    if (el) el.classList.add('d-none');
  }
  // Show current
  const target = document.getElementById(STAGE_IDS[step]);
  if (target) target.classList.remove('d-none');

  // Update badges
  const idx = STEPS.indexOf(step);
  STEPS.forEach((s, i) => {
    const badge = document.getElementById(`stepBadge-${s}`);
    if (!badge) return;
    badge.classList.remove('bg-primary', 'bg-success', 'text-white');
    if (i < idx) {
      badge.classList.add('bg-success', 'text-white');
    } else if (i === idx) {
      badge.classList.add('bg-primary', 'text-white');
    }
  });
}

/* ------------------------------------------------------------------ */
/*  Config loader                                                      */
/* ------------------------------------------------------------------ */
async function loadConfig(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load config: ${res.status}`);
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Intro Modal                                                        */
/* ------------------------------------------------------------------ */
function showModal() {
  const modalEl = document.getElementById('introModal');
  if (!modalEl) {
    showStep('org');
    return;
  }
  const bs = window.bootstrap || window.Bootstrap || null;
  try {
    if (bs && typeof bs.Modal === 'function') {
      const modal = new bs.Modal(modalEl, { backdrop: 'static', keyboard: false });
      modal.show();
      document.getElementById('introContinueBtn').addEventListener('click', () => {
        modal.hide();
        showStep('org');
      });
    } else {
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
      document.getElementById('introContinueBtn').addEventListener('click', () => {
        modalEl.classList.remove('show');
        modalEl.style.display = 'none';
        showStep('org');
      });
    }
  } catch (e) {
    console.warn('Intro modal init failed:', e);
    showStep('org');
  }
}

/* ------------------------------------------------------------------ */
/*  Org Info Stage                                                     */
/* ------------------------------------------------------------------ */

function bindOrgInfo() {
  const fields = {
    organization_name: document.getElementById('orgName'),
    account_name:      document.getElementById('accountName'),
    first_name:        document.getElementById('firstName'),
    last_name:         document.getElementById('lastName'),
    email:             document.getElementById('emailField'),
    assessor_name:     document.getElementById('assessorName'),
    assessor_email:    document.getElementById('assessorEmail'),
  };

  const nextBtn    = document.getElementById('orgInfoNextBtn');
  const errBox     = document.getElementById('orgInfoErrors');
  let selectedIndustry = orgInfo.industry || '';

  // Restore values from saved state
  for (const [key, el] of Object.entries(fields)) {
    if (el && orgInfo[key]) el.value = orgInfo[key];
  }

  // Industry buttons
  document.querySelectorAll('.industry-btn').forEach(btn => {
    if (btn.dataset.industry === selectedIndustry) btn.classList.add('active');
    btn.addEventListener('click', () => {
      document.querySelectorAll('.industry-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedIndustry = btn.dataset.industry;
      validateOrgForm();
    });
  });

  function collectOrgInfo() {
    return {
      organization_name: (fields.organization_name?.value || '').trim(),
      account_name:      (fields.account_name?.value || '').trim(),
      first_name:        (fields.first_name?.value || '').trim(),
      last_name:         (fields.last_name?.value || '').trim(),
      email:             (fields.email?.value || '').trim(),
      industry:          selectedIndustry,
      assessor_name:     (fields.assessor_name?.value || '').trim(),
      assessor_email:    (fields.assessor_email?.value || '').trim(),
    };
  }

  function validateOrgForm() {
    const data = collectOrgInfo();
    const errors = [];
    if (!data.organization_name) errors.push(lang === 'pt' ? 'Nome da organização é obrigatório' : 'Organization name is required');
    if (!data.first_name)        errors.push(lang === 'pt' ? 'Primeiro nome é obrigatório' : 'First name is required');
    if (!data.last_name)         errors.push(lang === 'pt' ? 'Sobrenome é obrigatório' : 'Last name is required');
    if (!data.email)             errors.push(lang === 'pt' ? 'Email é obrigatório' : 'Email is required');
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.push(lang === 'pt' ? 'Email inválido' : 'Invalid email address');
    }
    if (!data.industry)          errors.push(lang === 'pt' ? 'Selecione uma indústria' : 'Please select an industry');

    if (errors.length) {
      errBox.textContent = errors.join('. ');
      errBox.classList.remove('d-none');
      nextBtn.disabled = true;
    } else {
      errBox.classList.add('d-none');
      nextBtn.disabled = false;
    }
    return errors.length === 0;
  }

  // Bind input events for live validation
  Object.values(fields).forEach(el => {
    if (el) {
      el.addEventListener('input', validateOrgForm);
      el.addEventListener('blur', validateOrgForm);
    }
  });

  nextBtn.addEventListener('click', () => {
    if (!validateOrgForm()) return;
    orgInfo = collectOrgInfo();
    saveLocal(LS_ORGINFO, orgInfo);
    showStep('select');
    renderSelection();
  });

  // Initial validation
  validateOrgForm();
}

/* ------------------------------------------------------------------ */
/*  Selection Stage                                                    */
/* ------------------------------------------------------------------ */

function renderSelection() {
  const accordion = document.getElementById('domainsAccordion');
  accordion.innerHTML = '';

  config.domains.forEach((domain) => {
    const domSel     = selectionState.domains[domain.id];
    if (!domSel) return;
    const cardId     = `dom-${domain.id}`;
    const collapseId = `collapse-${domain.id}`;

    const areaItems = domain.areas.map(area => {
      const checked = !!domSel.areas[area.id];
      return `
        <div class="form-check ms-3 py-1">
          <input class="form-check-input area-checkbox" type="checkbox"
                 data-domain="${domain.id}" data-area="${area.id}"
                 id="area-${area.id}" ${checked ? 'checked' : ''}>
          <label class="form-check-label" for="area-${area.id}">
            ${t(area.name)}
            <span class="badge bg-secondary bg-opacity-25 text-dark ms-1">${area.questions.length}</span>
          </label>
        </div>`;
    }).join('');

    const domColor = domain.color || '#6c757d';
    const item = `
      <div class="accordion-item">
        <h2 class="accordion-header" id="${cardId}">
          <button class="accordion-button collapsed" type="button"
                  data-bs-toggle="collapse" data-bs-target="#${collapseId}"
                  aria-expanded="false" aria-controls="${collapseId}">
            <div class="form-check me-3" style="pointer-events:auto;">
              <input class="form-check-input domain-checkbox" type="checkbox"
                     data-domain="${domain.id}" id="dom-cb-${domain.id}"
                     ${domSel.selected ? 'checked' : ''}>
            </div>
            <span class="fw-semibold" style="color:${domColor}">
              <i class="bi ${domain.icon || 'bi-folder'} me-2"></i>${t(domain.name)}
            </span>
            <span class="badge bg-light text-muted ms-auto me-2">${domain.areas.length} areas</span>
          </button>
        </h2>
        <div id="${collapseId}" class="accordion-collapse collapse"
             aria-labelledby="${cardId}" data-bs-parent="#domainsAccordion">
          <div class="accordion-body pt-2 pb-3">
            <p class="text-muted small mb-2">${t(domain.description)}</p>
            ${areaItems}
          </div>
        </div>
      </div>`;

    accordion.insertAdjacentHTML('beforeend', item);
  });

  // Bind checkbox events only once (event delegation on the accordion)
  if (!accordion._delegated) {
    accordion._delegated = true;

    accordion.addEventListener('click', e => {
      // Stop domain checkbox click from toggling the accordion
      if (e.target.classList.contains('domain-checkbox')) {
        e.stopPropagation();
      }
    });

    accordion.addEventListener('change', e => {
      const cb = e.target;
      if (cb.classList.contains('domain-checkbox')) {
        const domId   = cb.dataset.domain;
        const checked = cb.checked;
        const domSel  = selectionState.domains[domId];
        domSel.selected = checked;
        for (const a of Object.keys(domSel.areas)) domSel.areas[a] = checked;
        // Sync child area checkboxes in-place (no re-render)
        accordion.querySelectorAll(`.area-checkbox[data-domain="${domId}"]`).forEach(aCb => {
          aCb.checked = checked;
        });
        updateSelectionCounters();
      } else if (cb.classList.contains('area-checkbox')) {
        const domId   = cb.dataset.domain;
        const areaId  = cb.dataset.area;
        const checked = cb.checked;
        const domSel  = selectionState.domains[domId];
        domSel.areas[areaId] = checked;
        const anyAreaSelected = Object.values(domSel.areas).some(Boolean);
        domSel.selected = anyAreaSelected;
        // Sync parent domain checkbox in-place
        const domCb = document.getElementById(`dom-cb-${domId}`);
        if (domCb) domCb.checked = anyAreaSelected;
        updateSelectionCounters();
      }
    });
  }

  // Initial counter update
  updateSelectionCounters();
}

/** Light-weight update: counters, button state, save — no DOM rebuild. */
function updateSelectionCounters() {
  let selectedDomainsCount = 0;
  let selectedAreasCount   = 0;
  let totalQuestionsCount  = 0;

  config.domains.forEach(domain => {
    const domSel = selectionState.domains[domain.id];
    if (!domSel) return;
    if (domSel.selected) selectedDomainsCount++;
    domain.areas.forEach(area => {
      if (domSel.areas[area.id]) {
        selectedAreasCount++;
        totalQuestionsCount += area.questions.length;
      }
    });
  });

  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setEl('selDomains', selectedDomainsCount);
  setEl('selAreas', selectedAreasCount);
  setEl('selQuestions', totalQuestionsCount);

  // Validate & update button / error
  const isValid  = validateSelection(selectionState);
  const err      = document.getElementById('selectionErrors');
  const startBtn = document.getElementById('startAssessmentBtn');

  if (!isValid) {
    const msg = lang === 'pt'
      ? 'Selecione pelo menos uma área.'
      : 'Please select at least one area.';
    if (err) { err.textContent = msg; err.classList.remove('d-none'); }
    if (startBtn) startBtn.disabled = true;
  } else {
    if (err) err.classList.add('d-none');
    if (startBtn) startBtn.disabled = false;
  }

  saveLocal(LS_SELECTION, selectionState);
}

function bindSelectionGlobalControls() {
  document.getElementById('btnSelectAll').addEventListener('click', () => {
    selectionState = buildDefaultSelection(config);
    renderSelection();   // full re-render for bulk change
  });

  document.getElementById('btnDeselectAll').addEventListener('click', () => {
    selectionState = { domains: {} };
    for (const d of config.domains) {
      selectionState.domains[d.id] = { selected: false, areas: {} };
      for (const a of d.areas) selectionState.domains[d.id].areas[a.id] = false;
    }
    renderSelection();   // full re-render for bulk change
  });

  document.getElementById('startAssessmentBtn').addEventListener('click', () => {
    if (!validateSelection(selectionState)) return;
    showStep('runner');
    renderRunner();
  });

  // Back to org info
  const backOrgBtn = document.getElementById('backToOrgInfoBtn');
  if (backOrgBtn) {
    backOrgBtn.addEventListener('click', () => {
      showStep('org');
    });
  }
}

/* ------------------------------------------------------------------ */
/*  Runner Stage                                                       */
/* ------------------------------------------------------------------ */

function renderRunner() {
  const selectedDomains = getSelectedDomains(config, selectionState);
  const runner = document.getElementById('runnerContainer');
  runner.innerHTML = '';

  const totalDomains   = selectedDomains.length;
  const totalAreas     = selectedDomains.reduce((a, d) => a + d.areas.length, 0);
  const totalQuestions = selectedDomains.reduce(
    (a, d) => a + d.areas.reduce((s, ar) => s + ar.questions.length, 0), 0);

  const countAnswered = () => Object.values(answersByArea)
    .reduce((a, arr) => a + arr.filter(v => v === true || v === false).length, 0);

  const setStats = () => {
    const setEl = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    setEl('statDomains', totalDomains);
    setEl('statAreas', totalAreas);
    setEl('statAnswered', countAnswered());
    setEl('statTotal', totalQuestions);
    // Update progress bar
    const pct = totalQuestions > 0 ? Math.round(countAnswered() / totalQuestions * 100) : 0;
    const bar = document.getElementById('runnerProgress');
    if (bar) bar.style.width = `${pct}%`;
  };
  setStats();

  const labels = yesNoLabels();

  selectedDomains.forEach(domain => {
    const domColor = domain.color || '#6c757d';
    const domBlock = document.createElement('div');
    domBlock.className = 'mb-4';
    domBlock.innerHTML = `
      <h5 class="border-bottom pb-2 mb-3" style="color:${domColor}">
        <i class="bi ${domain.icon || 'bi-folder'} me-2"></i>${t(domain.name)}
      </h5>`;

    domain.areas.forEach(area => {
      const areaKey = area.id;
      if (!answersByArea[areaKey]) {
        answersByArea[areaKey] = new Array(area.questions.length).fill(null);
      }

      const questionsHTML = area.questions.map((q, idx) => {
        const val = answersByArea[areaKey][idx];
        const yesActive = val === true  ? 'active btn-success' : 'btn-outline-success';
        const noActive  = val === false ? 'active btn-danger'  : 'btn-outline-danger';
        return `
          <div class="d-flex align-items-start py-2 border-top gap-3">
            <div class="flex-grow-1 small">${t(q.text)}</div>
            <div class="btn-group flex-shrink-0" role="group">
              <button class="btn btn-sm ${yesActive} answer-btn"
                      data-answer="yes" data-area="${areaKey}" data-index="${idx}">
                ${labels.yes}
              </button>
              <button class="btn btn-sm ${noActive} answer-btn"
                      data-answer="no" data-area="${areaKey}" data-index="${idx}">
                ${labels.no}
              </button>
            </div>
          </div>`;
      }).join('');

      const areaScore = calculateAreaScore(answersByArea[areaKey] || []);
      const areaDiv = document.createElement('div');
      areaDiv.className = 'card mb-3 shadow-sm';
      areaDiv.innerHTML = `
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="mb-0">${t(area.name)}</h6>
            <span class="badge bg-light text-dark border">
              ${lang === 'pt' ? 'Pontuação' : 'Score'}:
              <strong data-area-score="${areaKey}">${areaScore.toFixed(2)}</strong> / 5
            </span>
          </div>
          ${questionsHTML}
        </div>`;

      domBlock.appendChild(areaDiv);
    });

    runner.appendChild(domBlock);
  });

  // Bind answer buttons (event delegation)
  runner.addEventListener('click', e => {
    const btn = e.target.closest('.answer-btn');
    if (!btn) return;

    const areaId = btn.dataset.area;
    const idx    = parseInt(btn.dataset.index, 10);
    const val    = btn.dataset.answer === 'yes';
    answersByArea[areaId][idx] = val;

    // Update score badge
    const score = calculateAreaScore(answersByArea[areaId]);
    const el = runner.querySelector(`[data-area-score="${areaId}"]`);
    if (el) el.textContent = score.toFixed(2);

    // Update button states
    const group = btn.closest('.btn-group');
    if (group) {
      group.querySelectorAll('.answer-btn').forEach(b => {
        b.classList.remove('active', 'btn-success', 'btn-danger');
        if (b.dataset.answer === 'yes') {
          b.classList.add(answersByArea[areaId][idx] === true ? 'active' : '', 'btn-outline-success');
          if (answersByArea[areaId][idx] === true) {
            b.classList.remove('btn-outline-success');
            b.classList.add('btn-success', 'active');
          }
        } else {
          b.classList.add(answersByArea[areaId][idx] === false ? 'active' : '', 'btn-outline-danger');
          if (answersByArea[areaId][idx] === false) {
            b.classList.remove('btn-outline-danger');
            b.classList.add('btn-danger', 'active');
          }
        }
      });
    }

    saveLocal(LS_ANSWERS, answersByArea);
    setStats();
  });

  // Navigation
  document.getElementById('backToSelectionBtn').onclick = () => {
    showStep('select');
    renderSelection();
  };
  document.getElementById('finishAssessmentBtn').onclick = () => {
    renderReport();
  };
}

/* ------------------------------------------------------------------ */
/*  Report / Review Stage                                              */
/* ------------------------------------------------------------------ */

function renderReport() {
  const selectedDomains = getSelectedDomains(config, selectionState);
  const report = document.getElementById('reportContainer');
  report.innerHTML = '';

  const overall = calculateOverallScore(selectedDomains, answersByArea);
  const overallEl = document.getElementById('overallScore05');
  if (overallEl) overallEl.textContent = overall.toFixed(2);

  const scoreLabel = lang === 'pt' ? 'Pontuação' : 'Score';

  selectedDomains.forEach(domain => {
    const dScore   = calculateDomainScore(domain.areas, answersByArea);
    const domColor = domain.color || '#6c757d';

    const domCard = document.createElement('div');
    domCard.className = 'card mb-4 shadow-sm';
    domCard.innerHTML = `
      <div class="card-header d-flex justify-content-between align-items-center"
           style="background:${domColor}15; border-left:4px solid ${domColor}">
        <h6 class="mb-0" style="color:${domColor}">
          <i class="bi ${domain.icon || 'bi-folder'} me-2"></i>${t(domain.name)}
        </h6>
        <span class="badge" style="background:${domColor}; color:#fff">
          ${scoreLabel}: ${dScore.toFixed(2)} / 5
        </span>
      </div>
      <div class="card-body p-0">
        <div class="list-group list-group-flush" data-domain-areas="${domain.id}"></div>
      </div>`;
    report.appendChild(domCard);

    const listGroup = domCard.querySelector(`[data-domain-areas="${domain.id}"]`);
    domain.areas.forEach(area => {
      const aScore = calculateAreaScore(answersByArea[area.id] || []);
      const pct    = Math.round((aScore / 5) * 100);
      const barColor = pct >= 70 ? '#198754' : pct >= 40 ? '#ffc107' : '#dc3545';

      const areaItem = document.createElement('div');
      areaItem.className = 'list-group-item';
      areaItem.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-1">
          <span>${t(area.name)}</span>
          <span class="text-muted small">${aScore.toFixed(2)} / 5</span>
        </div>
        <div class="progress" style="height:6px">
          <div class="progress-bar" role="progressbar"
               style="width:${pct}%; background:${barColor}"
               aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"></div>
        </div>`;
      listGroup.appendChild(areaItem);
    });
  });

  showStep('report');

  // Navigation
  const backBtn = document.getElementById('backToRunnerBtn');
  if (backBtn) {
    backBtn.onclick = () => {
      showStep('runner');
    };
  }

  const restartBtn = document.getElementById('restartBtn');
  if (restartBtn) {
    restartBtn.onclick = () => {
      answersByArea = {};
      orgInfo = {};
      selectionState = buildDefaultSelection(config);
      saveLocal(LS_ANSWERS, answersByArea);
      saveLocal(LS_SELECTION, selectionState);
      saveLocal(LS_ORGINFO, orgInfo);
      showStep('org');
      bindOrgInfo();
      renderSelection();
    };
  }

  // Submit to server
  const submitBtn = document.getElementById('submitAssessmentBtn');
  if (submitBtn) {
    submitBtn.onclick = () => submitToServer(selectedDomains);
  }
}

/* ------------------------------------------------------------------ */
/*  Submit to Server                                                   */
/* ------------------------------------------------------------------ */

async function submitToServer(selectedDomains) {
  const spinner  = document.getElementById('submitSpinner');
  const errBox   = document.getElementById('submitError');
  const actions  = document.getElementById('reportActions');
  const spinMsg  = document.getElementById('submitSpinnerMsg');

  // Show loading
  if (actions)  actions.classList.add('d-none');
  if (errBox)   errBox.classList.add('d-none');
  if (spinner)  spinner.classList.remove('d-none');
  if (spinMsg)  spinMsg.textContent = lang === 'pt'
    ? 'Enviando avaliação e gerando relatório…'
    : 'Submitting assessment and generating report…';

  // Build list of selected area IDs
  const selectedAreaIds = [];
  for (const dom of selectedDomains) {
    for (const area of dom.areas) {
      selectedAreaIds.push(area.id);
    }
  }

  // Build answers keyed by area ID (arrays of true/false/null)
  const answersPayload = {};
  for (const areaId of selectedAreaIds) {
    answersPayload[areaId] = answersByArea[areaId] || [];
  }

  const payload = {
    orgInfo:        orgInfo,
    selectedAreas:  selectedAreaIds,
    answers:        answersPayload,
  };

  try {
    const resp = await fetch(submitUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const result = await resp.json();

    if (resp.ok && result.status === 'success') {
      // Clear localStorage
      localStorage.removeItem(LS_SELECTION);
      localStorage.removeItem(LS_ANSWERS);
      localStorage.removeItem(LS_ORGINFO);

      if (spinMsg) spinMsg.textContent = lang === 'pt'
        ? 'Relatório gerado! Redirecionando…'
        : 'Report generated! Redirecting…';

      // Redirect to server-rendered report
      setTimeout(() => {
        window.location.href = result.redirect;
      }, 600);
    } else {
      throw new Error(result.message || 'Server error');
    }
  } catch (err) {
    console.error('Submit error:', err);
    if (spinner) spinner.classList.add('d-none');
    if (actions) actions.classList.remove('d-none');
    if (errBox) {
      errBox.textContent = lang === 'pt'
        ? `Erro ao enviar: ${err.message}. Tente novamente.`
        : `Submission error: ${err.message}. Please try again.`;
      errBox.classList.remove('d-none');
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Entry point                                                        */
/* ------------------------------------------------------------------ */

async function main() {
  const root = document.getElementById('create-root');
  if (!root) return;

  const cfgUrl = root.dataset.configUrl;
  submitUrl    = root.dataset.submitUrl || '';
  lang         = detectLang();

  config         = await loadConfig(cfgUrl);
  selectionState = loadLocal(LS_SELECTION, buildDefaultSelection(config));
  answersByArea  = loadLocal(LS_ANSWERS, {});
  orgInfo        = loadLocal(LS_ORGINFO, {});

  // Show intro modal first
  showModal();

  // Bind all stages
  bindOrgInfo();
  renderSelection();
  bindSelectionGlobalControls();
}

function onReady(fn) {
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(fn, 0);
  } else {
    window.addEventListener('DOMContentLoaded', fn);
  }
}

onReady(main);
