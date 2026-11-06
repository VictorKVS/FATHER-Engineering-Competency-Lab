function renderAutomation(){
  const c=document.getElementById("factoryCanvas");
  c.className="automation-board";
  c.innerHTML='<div class="signal-line l1"></div><div class="signal-line l2"></div>';
  window.FATHER_AUTOMATION.zones.forEach(z=>{
    const zone=document.createElement("section");
    zone.className="automation-zone";
    zone.dataset.zone=z.id;
    zone.innerHTML=`<h3>${z.name}</h3>`;
    z.nodes.forEach(n=>{
      const el=document.createElement("div");
      el.className="automation-node";
      el.textContent=n.name;
      el.onclick=()=>inspectAutomationNode(n,z,el);
      zone.appendChild(el);
    });
    c.appendChild(zone);
  });
  const core=document.createElement("section");
  core.className="pipeline-core";
  core.innerHTML='<div class="core-title">FATHER PIPELINE CORE</div><div class="core-sub">Design → Run → Replay</div><div class="pipeline-status"><span class="mode-pill active">DESIGN</span><span class="mode-pill">RUN</span><span class="mode-pill">REPLAY</span></div>';
  c.appendChild(core);
  const tpl=document.createElement("section");
  tpl.className="templates";
  window.FATHER_AUTOMATION.templates.forEach(t=>{
    const card=document.createElement("article");
    card.className="template-card";
    card.innerHTML=`<h4>${t.name}</h4><div class="template-path">${t.graph.join(" → ")}</div>`;
    card.onclick=()=>inspectAutomationTemplate(t);
    tpl.appendChild(card);
  });
  c.appendChild(tpl);
  document.querySelector(".canvas-title h1").textContent="FATHER Automation Assembly Table";
  document.querySelector(".canvas-title p").textContent="Источники → workflow → AI-агенты → системы → выходы. Центральное ядро исполняет и записывает pipeline.";
}
function inspectAutomationNode(n,z,el){
  document.querySelectorAll(".automation-node.active").forEach(x=>x.classList.remove("active"));
  if(el) el.classList.add("active");
  document.getElementById("selectedStatus").textContent="SELECTED: "+n.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${n.name}</h2>
    <div class="kv"><div class="k">ID</div><div class="v">${n.id}</div></div>
    <div class="kv"><div class="k">Zone</div><div class="v">${z.name}</div></div>
    <div class="kv"><div class="k">Kind</div><div class="v">${n.kind}</div></div>
    <div class="section"><h3>Design contract</h3><ul class="list"><li>inputs</li><li>outputs</li><li>schema</li><li>auth</li><li>retry</li><li>tests</li><li>security</li><li>metrics</li></ul></div>`;
}
function inspectAutomationTemplate(t){
  document.getElementById("selectedStatus").textContent="SELECTED: "+t.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${t.name}</h2>
    <div class="section"><h3>Workflow</h3><p>${t.graph.join(" → ")}</p></div>
    <div class="section"><h3>Pipeline modes</h3><ul class="list"><li>DESIGN — схема и контракты</li><li>RUN — исполнение узлов</li><li>REPLAY — пошаговый просмотр событий</li></ul></div>
    <div class="section"><h3>Next action</h3><p>Шаблон клонируется в продукт и заменяет абстрактные узлы реальными adapters/services/agents.</p></div>`;
}