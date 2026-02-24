// Helper functions for selection, scoring, and persistence

export function getSelectedDomains(config, selectionState) {
  const selected = [];
  for (const domain of config.domains) {
    const domSel = selectionState.domains[domain.id];
    if (!domSel) continue;
    const selectedAreas = domain.areas.filter(a => domSel.areas[a.id]);
    if (selectedAreas.length > 0) {
      selected.push({ ...domain, areas: selectedAreas });
    }
  }
  return selected;
}

export function calculateAreaScore(areaAnswers) {
  // areaAnswers: array of booleans (true for Yes)
  const yesCount = areaAnswers.filter(Boolean).length;
  const total = areaAnswers.length || 1;
  const normalized = Math.max(0, Math.min(1, yesCount / total));
  return +(normalized * 5).toFixed(2);
}

export function calculateDomainScore(domainAreas, answersByArea) {
  // domainAreas: [{id, questions:[]}] ; answersByArea: { [areaId]: bool[] }
  if (!domainAreas.length) return 0;
  let sum = 0;
  let count = 0;
  for (const area of domainAreas) {
    const arr = answersByArea[area.id] || [];
    if (arr.length === 0 && area.questions?.length) {
      // unanswered counts as 0
      sum += 0;
      count += 1;
      continue;
    }
    sum += calculateAreaScore(arr);
    count += 1;
  }
  return count ? +(sum / count).toFixed(2) : 0;
}

export function calculateOverallScore(selectedDomains, answersByArea) {
  if (!selectedDomains.length) return 0;
  let sum = 0;
  let count = 0;
  for (const domain of selectedDomains) {
    sum += calculateDomainScore(domain.areas, answersByArea);
    count += 1;
  }
  return count ? +(sum / count).toFixed(2) : 0;
}

export function saveLocal(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}
export function loadLocal(key, fallback) {
  try {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : fallback;
  } catch {
    return fallback;
  }
}

export function buildDefaultSelection(config) {
  const state = { domains: {} };
  for (const d of config.domains) {
    state.domains[d.id] = { selected: true, areas: {} };
    for (const a of d.areas) {
      state.domains[d.id].areas[a.id] = true;
    }
  }
  return state;
}

export function validateSelection(selectionState) {
  // must have at least one area selected total
  let total = 0;
  for (const domId in selectionState.domains) {
    const dom = selectionState.domains[domId];
    const areaCount = Object.values(dom.areas).filter(Boolean).length;
    if (dom.selected && areaCount === 0) {
      // auto-fix: deselect the domain if no areas
      dom.selected = false;
    }
    total += areaCount;
  }
  return total > 0;
}
