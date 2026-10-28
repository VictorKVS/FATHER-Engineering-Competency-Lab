function renderAutomation(){
  const c=document.getElementById("factoryCanvas");
  c.className="automation-board";
  c.innerHTML="";
  window.FATHER_AUTOMATION.zones.forEach(z=>{
    const zone=document.createElement("section");
    zone.className="automation-zone";
    zone.innerHTML=`<h3>${z.name}</h3>`;
    z.nodes.forEach(n=>{
      const el=document.createElement("div");
      el.className="automation-node";
      el.textContent=n.name;
      el.onclick=()=>inspectAutomationNode(n,z);
      zone.appendChild(el);
    });
    c.appendChild(zone);
  });
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
  document.querySelector(".canvas-title h1").textContent="FATHER Automation Canvas";
  document.querySelector(".canvas-title p").textContent="Поле проектирования автоматизаций, workflow-графов и multi-agent сценариев.";
}
function inspectAutomationNode(n,z){
  document.getElementById("selectedStatus").textContent="SELECTED: "+n.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${n.name}</h2>
    <div class="kv"><div class="k">ID</div><div class="v">${n.id}</div></div>
    <div class="kv"><div class="k">Zone</div><div class="v">${z.name}</div></div>
    <div class="kv"><div class="k">Kind</div><div class="v">${n.kind}</div></div>
    <div class="section"><h3>Design contract</h3><ul class="list"><li>inputs</li><li>outputs</li><li>schema</li><li>auth</li><li>retry</li><li>tests</li><li>security</li></ul></div>`;
}
function inspectAutomationTemplate(t){
  document.getElementById("selectedStatus").textContent="SELECTED: "+t.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${t.name}</h2>
    <div class="section"><h3>Workflow</h3><p>${t.graph.join(" → ")}</p></div>
    <div class="section"><h3>Next action</h3><p>Шаблон можно клонировать в конкретный продукт и заменить узлы на реальные adapters/services/agents.</p></div>`;
}