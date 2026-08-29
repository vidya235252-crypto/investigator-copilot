function getCaseId(){
  return new URLSearchParams(window.location.search).get("id");
}

function riskLevel(score){
  if(score>=80) return "high";
  if(score>=40) return "medium";
  return "low";
}

function formatFullTime(ts){
  return new Date(ts).toLocaleString(undefined,{
    year:"numeric",month:"short",day:"2-digit",
    hour:"2-digit",minute:"2-digit",second:"2-digit"
  });
}

function extractEntities(timeline){
  const devices={}, ips={}, geos={};
  timeline.forEach(e=>{
    if(!devices[e.device_id]) devices[e.device_id]={count:0,first:e.timestamp,last:e.timestamp};
    devices[e.device_id].count++;
    devices[e.device_id].last=e.timestamp;

    if(!ips[e.ip_address]) ips[e.ip_address]={count:0,first:e.timestamp,last:e.timestamp};
    ips[e.ip_address].count++;
    ips[e.ip_address].last=e.timestamp;

    if(!geos[e.geo_country]) geos[e.geo_country]={count:0};
    geos[e.geo_country].count++;
  });
  return {devices,ips,geos};
}

function renderEntityPanel(entities){
  const deviceRows=Object.entries(entities.devices).map(([id,v])=>`
    <div class="entity-item"><span>${id}</span><span class="entity-count">${v.count} events</span></div>
  `).join("");
  const ipRows=Object.entries(entities.ips).map(([id,v])=>`
    <div class="entity-item"><span>${id}</span><span class="entity-count">${v.count} events</span></div>
  `).join("");
  const geoRows=Object.entries(entities.geos).map(([id,v])=>`
    <div class="entity-item"><span>${id}</span><span class="entity-count">${v.count} events</span></div>
  `).join("");

  return `
    <div class="entity-group">
      <div class="entity-group-label">Devices (${Object.keys(entities.devices).length})</div>
      ${deviceRows}
    </div>
    <div class="entity-group">
      <div class="entity-group-label">IP Addresses (${Object.keys(entities.ips).length})</div>
      ${ipRows}
    </div>
    <div class="entity-group">
      <div class="entity-group-label">Geographies (${Object.keys(entities.geos).length})</div>
      ${geoRows}
    </div>
  `;
}

function renderEntityGraph(accountId,entities){
  const deviceIds=Object.keys(entities.devices).slice(0,4);
  const ipIds=Object.keys(entities.ips).slice(0,4);
  const nodes=[...deviceIds.map(d=>({id:d,type:"device"})),...ipIds.map(i=>({id:i,type:"ip"}))];
  const cx=160, cy=90, r=62;
  const total=nodes.length||1;

  const nodeSvg=nodes.map((n,i)=>{
    const angle=(i/total)*Math.PI*2 - Math.PI/2;
    const x=cx+r*Math.cos(angle);
    const y=cy+r*Math.sin(angle);
    const label=n.id.length>14?n.id.slice(0,14)+"…":n.id;
    return `
      <line class="eg-edge" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"></line>
      <g class="eg-node" transform="translate(${x},${y})">
        <circle r="16"></circle>
        <text class="eg-label" text-anchor="middle" y="30">${label}</text>
        <text class="eg-label" text-anchor="middle" y="4" font-size="8">${n.type}</text>
      </g>
    `;
  }).join("");

  return `
    <svg class="entity-graph" viewBox="0 0 320 180">
      ${nodeSvg}
      <g class="eg-node-account" transform="translate(${cx},${cy})">
        <circle r="22"></circle>
        <text class="eg-label-center" text-anchor="middle" y="4">acct</text>
      </g>
    </svg>
  `;
}

function renderTimeline(timeline){
  return timeline.map((e,i)=>{
    const amount=e.amount?`<span class="timeline-amount">₹${e.amount.toLocaleString()}</span>`:"";
    const isLast=i===timeline.length-1;
    return `
      <div class="timeline-row">
        <span class="timeline-time">${formatFullTime(e.timestamp)}</span>
        <span class="timeline-rail">
          <span class="timeline-dot"></span>
          ${isLast?"":'<span class="timeline-line"></span>'}
        </span>
        <span class="timeline-body">
          <span class="timeline-event">${e.event_type.replaceAll("_"," ")}${amount}</span>
          <div class="timeline-meta">${e.ip_address} · ${e.device_id} · ${e.geo_country}</div>
        </span>
      </div>
    `;
  }).join("");
}

function renderEvidence(evidence){
  const sorted=[...evidence].sort((a,b)=>b.weight-a.weight);
  return sorted.map(ev=>`
    <div class="evidence-row">
      <span class="evidence-weight">+${ev.weight}</span>
      <span class="evidence-signal">${ev.signal.replaceAll("_"," ")}</span>
      <span class="evidence-value">${ev.value}</span>
    </div>
  `).join("");
}

function splitAiSummary(summary){
  const match=summary.match(/RECOMMENDED_ACTION:\s*(\w+)/i);
  const action=match?match[1].toLowerCase():null;
  const body=summary.replace(/RECOMMENDED_ACTION:\s*\w+/i,"").trim();
  return {body,action};
}

function notesKey(caseId){
  return `investigator_notes_${caseId}`;
}

function loadNotes(caseId){
  try{
    const raw=localStorage.getItem(notesKey(caseId));
    return raw?JSON.parse(raw):[];
  }catch(e){
    return [];
  }
}

function saveNotes(caseId,notes){
  localStorage.setItem(notesKey(caseId),JSON.stringify(notes));
}

function renderNotesPanel(caseId){
  const notes=loadNotes(caseId);
  const list=notes.length===0
    ? `<p class="notes-empty">No analyst notes recorded.</p>`
    : `<div class="notes-list">${notes.map(n=>`
        <div class="note-item">
          <div class="note-text">${n.text}</div>
          <div class="note-time">${formatFullTime(n.time)}</div>
        </div>
      `).join("")}</div>`;

  return `
    <div class="panel-title">Analyst Notes</div>
    ${list}
    <div class="notes-input-row">
      <textarea id="notes-input" class="notes-input" placeholder="Add investigation note…"></textarea>
      <button id="add-note-btn" class="btn">Add</button>
    </div>
    <div class="notes-scope-tag">Stored locally in this browser, not synced to the case record.</div>
  `;
}

function bindNotes(caseId){
  document.getElementById("add-note-btn").addEventListener("click",()=>{
    const input=document.getElementById("notes-input");
    const text=input.value.trim();
    if(!text) return;
    const notes=loadNotes(caseId);
    notes.push({text,time:new Date().toISOString()});
    saveNotes(caseId,notes);
    document.getElementById("notes-panel-body").innerHTML=renderNotesPanel(caseId);
    bindNotes(caseId);
  });
}

async function loadCase(){
  const caseId=getCaseId();
  const root=document.getElementById("case-root");
  if(!caseId){
    root.innerHTML="<p class='error-state'>No case ID supplied in URL.</p>";
    return;
  }
  try{
    const c=await fetchCase(caseId);
    render(c);
  }catch(err){
    root.innerHTML=`<p class='error-state'>${err.message}</p>`;
  }
}

function render(c){
  const root=document.getElementById("case-root");
  const level=riskLevel(c.ml_risk_score);
  const entities=extractEntities(c.timeline);

  const aiParsed=c.ai_summary?splitAiSummary(c.ai_summary):null;

  root.innerHTML=`
    <div class="case-topbar">
      <div class="case-id-block">
        <a class="case-back" href="index.html">← Investigation Queue</a>
        <h1>${c.account_id}</h1>
        <div class="case-sub">${c.case_id} · opened ${formatFullTime(c.created_at)}</div>
      </div>
      <span class="status-tag status-${c.status}">${c.status}</span>
    </div>

    <div class="case-layout">
      <div class="case-main">

        <div class="panel">
          <div class="panel-title">Risk Assessment</div>
          <div class="risk-readout">
            <div class="risk-metric">
              <div class="risk-metric-label">ML Model</div>
              <div class="risk-metric-value ${level}">${c.ml_risk_score.toFixed(2)}</div>
              <div class="risk-bar-track"><div class="risk-bar-fill ${level}" style="width:${c.ml_risk_score}%"></div></div>
            </div>
            <div class="risk-metric">
              <div class="risk-metric-label">Rule Engine</div>
              <div class="risk-metric-value ${riskLevel(c.rule_risk_score)}">${c.rule_risk_score.toFixed(0)}</div>
              <div class="risk-bar-track"><div class="risk-bar-fill ${riskLevel(c.rule_risk_score)}" style="width:${c.rule_risk_score}%"></div></div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Investigation Timeline</div>
          <div class="timeline">${renderTimeline(c.timeline)}</div>
        </div>

        <div class="panel">
          <div class="panel-title">Evidence</div>
          ${renderEvidence(c.evidence)}
        </div>

        <div class="panel">
          <div class="panel-title">AI Investigator</div>
          <div id="ai-body">
            ${c.ai_summary?`
              <div class="ai-body">${aiParsed.body}</div>
              ${aiParsed.action?`
                <div class="ai-recommendation">
                  <span class="ai-recommendation-label">Recommended action</span>
                  <span>${aiParsed.action.toUpperCase()}</span>
                </div>
              `:""}
              <div class="ai-source-tag">Evidence-grounded synthesis · no independent risk assessment</div>
            `:`
              <button id="run-investigation" class="btn btn-run">Run AI Investigation</button>
            `}
          </div>
        </div>

      </div>

      <div class="case-sidebar">

        <div class="panel">
          <div class="panel-title">Case Actions</div>
          ${c.status==="open"?`
            <div class="action-row">
              <button class="btn btn-approve" data-action="approve">Approve</button>
              <button class="btn btn-hold" data-action="hold">Hold</button>
              <button class="btn btn-escalate" data-action="escalate">Escalate</button>
            </div>
          `:`
            <div class="review-record">
              action: <span class="action-value">${c.reviewer_action}</span><br>
              at: ${formatFullTime(c.reviewed_at)}
            </div>
          `}
        </div>

        <div class="panel">
          <div class="panel-title">Account / Device / IP</div>
          <div class="info-list">
            ${renderEntityPanel(entities)}
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Entity Relationships</div>
          ${renderEntityGraph(c.account_id,entities)}
        </div>

        <div class="panel" id="notes-panel-body">
          ${renderNotesPanel(c.case_id)}
        </div>

      </div>
    </div>
  `;

  bindNotes(c.case_id);

  const investigateBtn=document.getElementById("run-investigation");
  if(investigateBtn){
    investigateBtn.addEventListener("click",async()=>{
      investigateBtn.disabled=true;
      investigateBtn.textContent="Running…";
      try{
        const updated=await investigateCase(c.case_id);
        render(updated);
      }catch(err){
        document.getElementById("ai-body").innerHTML=`<p class="error-state">${err.message}</p>`;
      }
    });
  }

  document.querySelectorAll(".action-row button").forEach(btn=>{
    btn.addEventListener("click",async()=>{
      const action=btn.dataset.action;
      btn.disabled=true;
      try{
        const updated=await reviewCase(c.case_id,action);
        render(updated);
      }catch(err){
        alert(err.message);
        btn.disabled=false;
      }
    });
  });
}

document.addEventListener("DOMContentLoaded",loadCase);