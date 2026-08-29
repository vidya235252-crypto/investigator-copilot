function riskLevel(score) {
  if (score >= 80) return "high";
  if (score >= 40) return "medium";
  return "low";
}

function topSignal(evidence) {
  if (!evidence || evidence.length === 0) return "no signals";
  const sorted = [...evidence].sort((a, b) => b.weight - a.weight);
  return sorted[0].signal.replaceAll("_", " ");
}

function renderCaseCard(c) {
  const level = riskLevel(c.ml_risk_score);
  return `
    <a class="case-card risk-${level}" href="case.html?id=${c.case_id}">
      <div class="case-card-header">
        <span class="account-id">${c.account_id}</span>
        <span class="status-badge status-${c.status}">${c.status}</span>
      </div>
      <div class="case-card-scores">
        <div class="score-block">
          <span class="score-label">ML Risk</span>
          <span class="score-value">${c.ml_risk_score}</span>
        </div>
        <div class="score-block">
          <span class="score-label">Rule Risk</span>
          <span class="score-value">${c.rule_risk_score}</span>
        </div>
      </div>
      <div class="top-signal">${topSignal(c.evidence)}</div>
    </a>
  `;
}

async function loadQueue() {
  const container = document.getElementById("case-list");
  container.innerHTML = "<p class='loading'>Loading cases...</p>";
  try {
    const cases = await fetchCases();
    if (cases.length === 0) {
      container.innerHTML = "<p class='empty'>No cases found.</p>";
      return;
    }
    container.innerHTML = cases.map(renderCaseCard).join("");
  } catch (err) {
    container.innerHTML = `<p class='error'>Failed to load cases: ${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", loadQueue);