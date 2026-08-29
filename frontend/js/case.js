function getCaseIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

function riskLevel(score) {
  if (score >= 80) return "high";
  if (score >= 40) return "medium";
  return "low";
}

function formatTimestamp(ts) {
  const d = new Date(ts);
  return d.toLocaleString();
}

function renderTimeline(timeline) {
  return timeline.map((e, i) => {
    const amountStr = e.amount ? `<span class="event-amount">₹${e.amount.toLocaleString()}</span>` : "";
    return `
      <div class="timeline-item">
        <div class="timeline-marker"></div>
        <div class="timeline-content">
          <div class="timeline-time">${formatTimestamp(e.timestamp)}</div>
          <div class="timeline-event">${e.event_type.replaceAll("_", " ")} ${amountStr}</div>
          <div class="timeline-meta">${e.ip_address} · ${e.device_id} · ${e.geo_country}</div>
        </div>
      </div>
    `;
  }).join("");
}

function renderEvidence(evidence) {
  const sorted = [...evidence].sort((a, b) => b.weight - a.weight);
  return sorted.map(ev => `
    <div class="evidence-item">
      <span class="evidence-weight">+${ev.weight}</span>
      <span class="evidence-signal">${ev.signal.replaceAll("_", " ")}</span>
      <span class="evidence-value">${ev.value}</span>
    </div>
  `).join("");
}

function renderReviewStatus(c) {
  if (c.status === "open") return "";
  return `
    <div class="review-status">
      Reviewed: <strong>${c.reviewer_action}</strong> at ${formatTimestamp(c.reviewed_at)}
    </div>
  `;
}

async function loadCase() {
  const caseId = getCaseIdFromUrl();
  const container = document.getElementById("case-detail");
  if (!caseId) {
    container.innerHTML = "<p class='error'>No case ID provided.</p>";
    return;
  }
  try {
    const c = await fetchCase(caseId);
    renderCase(c);
  } catch (err) {
    container.innerHTML = `<p class='error'>Failed to load case: ${err.message}</p>`;
  }
}

function renderCase(c) {
  const level = riskLevel(c.ml_risk_score);
  const container = document.getElementById("case-detail");

  container.innerHTML = `
    <div class="case-header risk-${level}">
      <div>
        <h2>${c.account_id}</h2>
        <span class="status-badge status-${c.status}">${c.status}</span>
      </div>
      <div class="score-summary">
        <div class="score-block-large">
          <span class="score-label">ML Risk</span>
          <span class="score-value-large">${c.ml_risk_score}</span>
        </div>
        <div class="score-block-large">
          <span class="score-label">Rule Risk</span>
          <span class="score-value-large">${c.rule_risk_score}</span>
        </div>
      </div>
    </div>

    <div class="case-grid">
      <section class="panel">
        <h3>Investigation Timeline</h3>
        <div class="timeline">${renderTimeline(c.timeline)}</div>
      </section>

      <section class="panel">
        <h3>Evidence</h3>
        <div class="evidence-list">${renderEvidence(c.evidence)}</div>
      </section>
    </div>

    <section class="panel ai-panel">
      <h3>AI Investigator</h3>
      <div id="ai-summary-content">
        ${c.ai_summary
          ? `<p class="ai-summary-text">${c.ai_summary.replace(/\n/g, "<br>")}</p>`
          : `<button id="run-investigation-btn" class="btn-primary">Run AI Investigation</button>`
        }
      </div>
    </section>

    <section class="panel review-panel">
      <h3>Human Review</h3>
      ${renderReviewStatus(c)}
      ${c.status === "open" ? `
        <div class="review-actions">
          <button class="btn-approve" data-action="approve">Approve</button>
          <button class="btn-hold" data-action="hold">Hold</button>
          <button class="btn-escalate" data-action="escalate">Escalate</button>
        </div>
      ` : ""}
    </section>
  `;

  const investigateBtn = document.getElementById("run-investigation-btn");
  if (investigateBtn) {
    investigateBtn.addEventListener("click", async () => {
      investigateBtn.disabled = true;
      investigateBtn.textContent = "Investigating...";
      try {
        const updated = await investigateCase(c.case_id);
        renderCase(updated);
      } catch (err) {
        document.getElementById("ai-summary-content").innerHTML = `<p class="error">Investigation failed: ${err.message}</p>`;
      }
    });
  }

  document.querySelectorAll(".review-actions button").forEach(btn => {
    btn.addEventListener("click", async () => {
      const action = btn.dataset.action;
      try {
        const updated = await reviewCase(c.case_id, action);
        renderCase(updated);
      } catch (err) {
        alert(`Review failed: ${err.message}`);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", loadCase);