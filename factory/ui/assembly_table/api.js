function renderApi(){
  const c=document.getElementById("factoryCanvas");
  c.className="api-board";
  c.innerHTML="";
  window.FATHER_API.flows.forEach(f=>{
    const card=document.createElement("article");
    card.className="api-card";
    card.innerHTML=`
      <div class="api-meta">${f.id}</div>
      <h3>${f.name}</h3>
      <div class="api-arrow">${f.producer} → ${f.consumer}</div>
      <div class="api-grid">
        <div class="k">Event</div><div class="v">${f.endpoint_or_event}</div>
        <div class="k">Protocol</div><div class="v">${f.protocol}</div>
        <div class="k">Schema</div><div class="v">${f.payload_schema}</div>
        <div class="k">Validation</div><div class="v">${f.validation}</div>
        <div class="k">Status</div><div class="v">${f.test_status}</div>
      </div>`;
    card.onclick=()=>inspectApi(f,card);
    c.appendChild(card);
  });
  document.querySelector(".canvas-title h1").textContent="Слой 3. API / Event Design";
  document.querySelector(".canvas-title p").textContent="Каждая стрелка фабрики превращена в формальный контракт передачи.";
}
function inspectApi(f,card){
  document.querySelectorAll(".api-card.selected").forEach(x=>x.classList.remove("selected"));
  card.classList.add("selected");
  document.getElementById("selectedStatus").textContent="SELECTED: "+f.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${f.name}</h2>
    ${Object.entries(f).map(([k,v])=>`<div class="kv"><div class="k">${k}</div><div class="v">${v ?? "UNKNOWN"}</div></div>`).join("")}
  `;
}
