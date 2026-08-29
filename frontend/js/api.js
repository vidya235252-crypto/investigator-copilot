const API_BASE="http://127.0.0.1:8000";

async function fetchCases(status){
  const url=status?`${API_BASE}/cases?status=${status}`:`${API_BASE}/cases`;
  const res=await fetch(url);
  if(!res.ok) throw new Error("failed to load cases from API");
  return res.json();
}

async function fetchCase(caseId){
  const res=await fetch(`${API_BASE}/cases/${caseId}`);
  if(!res.ok) throw new Error("failed to load case from API");
  return res.json();
}

async function investigateCase(caseId){
  const res=await fetch(`${API_BASE}/cases/${caseId}/investigate`,{method:"POST"});
  if(!res.ok) throw new Error("investigation request failed");
  return res.json();
}

async function reviewCase(caseId,action){
  const res=await fetch(`${API_BASE}/cases/${caseId}/review`,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({action})
  });
  if(!res.ok) throw new Error("review submission failed");
  return res.json();
}