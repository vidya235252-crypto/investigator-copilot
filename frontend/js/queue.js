let currentStatus="";

function riskLevel(score){
  if(score>=80) return "high";
  if(score>=40) return "medium";
  return "low";
}

function topSignal(evidence){
  if(!evidence||evidence.length===0) return "no active signals";
  const sorted=[...evidence].sort((a,b)=>b.weight-a.weight);
  return sorted[0].signal.replaceAll("_"," ");
}

function formatTime(ts){
  const d=new Date(ts);
  return d.toLocaleDateString(undefined,{month:"short",day:"2-digit"})+" "+d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"});
}

function renderRow(c){
  const level=riskLevel(c.ml_risk_score);
  return `
    <a class="queue-row risk-${level}" href="case.html?id=${c.case_id}">
      <span class="qr-account">${c.account_id}</span>
      <span class="qr-score">${c.ml_risk_score.toFixed(1)}</span>
      <span class="qr-score">${c.rule_risk_score.toFixed(0)}</span>
      <span class="qr-signal">${topSignal(c.evidence)}</span>
      <span class="qr-time">${formatTime(c.created_at)}</span>
      <span class="status-tag status-${c.status}">${c.status}</span>
    </a>
  `;
}

async function loadQueue(status){
  const rows=document.getElementById("queue-rows");
  const count=document.getElementById("queue-count");
  rows.innerHTML="<p class='loading-state'>Querying case store…</p>";
  try{
    const cases=await fetchCases(status);
    if(cases.length===0){
      rows.innerHTML="<p class='empty-state'>No cases match this filter.</p>";
      count.textContent="0 cases";
      return;
    }
    const sorted=[...cases].sort((a,b)=>b.ml_risk_score-a.ml_risk_score);
    rows.innerHTML=sorted.map(renderRow).join("");
    count.textContent=`${cases.length} case${cases.length===1?"":"s"} in view`;
  }catch(err){
    rows.innerHTML=`<p class='error-state'>${err.message}</p>`;
    count.textContent="";
  }
}

function initFilters(){
  const tabs=document.querySelectorAll(".filter-tab");
  tabs.forEach(tab=>{
    tab.addEventListener("click",()=>{
      tabs.forEach(t=>t.classList.remove("active"));
      tab.classList.add("active");
      currentStatus=tab.dataset.status;
      loadQueue(currentStatus);
    });
  });
}

document.addEventListener("DOMContentLoaded",()=>{
  initFilters();
  loadQueue("");
});