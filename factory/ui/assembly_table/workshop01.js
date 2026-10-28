function renderWorkshop01(){
  const c=document.getElementById("factoryCanvas");
  c.className="workshop-board";
  c.innerHTML="";
  window.WORKSHOP01.stages.forEach((s,i)=>{
    const el=document.createElement("article");
    el.className="workshop-step "+(i===window.WORKSHOP01.stages.length-1?"workshop-gate":"");
    el.innerHTML=`<div class="id">${s.id}</div><h3>${s.name}</h3><div class="out">OUTPUT: ${s.output}</div><span class="badge ${s.status}">${s.status}</span>`;
    el.onclick=()=>inspectWorkshopStep(s,el);
    c.appendChild(el);
  });
  document.querySelector(".canvas-title h1").textContent="Workshop 01. Business Analysis";
  document.querySelector(".canvas-title p").textContent="Детализация цеха от Customer Intent до Business Design Package.";
}
function inspectWorkshopStep(s,el){
  document.querySelectorAll(".workshop-step.selected").forEach(x=>x.classList.remove("selected"));
  el.classList.add("selected");
  document.getElementById("selectedStatus").textContent="SELECTED: "+s.id;
  const gate=s.id==="BA14" ? window.WORKSHOP01.gate.conditions : [];
  document.getElementById("inspector").innerHTML=`
    <h2>${s.name}</h2>
    <div class="kv"><div class="k">ID</div><div class="v">${s.id}</div></div>
    <div class="kv"><div class="k">Output</div><div class="v">${s.output}</div></div>
    <div class="kv"><div class="k">Status</div><div class="v">${s.status}</div></div>
    ${gate.length?'<div class="section"><h3>Gate conditions</h3><ul class="list">'+gate.map(x=>'<li>'+x+'</li>').join('')+'</ul></div>':''}
  `;
}
