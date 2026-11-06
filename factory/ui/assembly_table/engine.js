function renderEngine(){
  const c=document.getElementById("factoryCanvas");
  c.className="engine-board";
  c.innerHTML="";
  window.FATHER_ENGINE.layers.forEach(l=>{
    const el=document.createElement("section");
    el.className="engine-layer";
    el.innerHTML=`<h3>${l.name}</h3><div class="engine-items">${l.items.map(x=>`<span class="engine-chip">${x}</span>`).join("")}</div>`;
    el.onclick=()=>inspectEngineLayer(l);
    c.appendChild(el);
  });
  document.querySelector(".canvas-title h1").textContent="FATHER Engine — Agent Runtime";
  document.querySelector(".canvas-title p").textContent="Внутренний двигатель фабрики: каналы → orchestration → memory/context → models → tools → state → assurance → deployment.";
}
function inspectEngineLayer(l){
  document.getElementById("selectedStatus").textContent="SELECTED: "+l.id;
  document.getElementById("inspector").innerHTML=`
  <h2>${l.name}</h2>
  <div class="section"><h3>Capabilities</h3><ul class="list">${l.items.map(x=>'<li>'+x+'</li>').join('')}</ul></div>
  <div class="section"><h3>Factory relation</h3><p>Этот слой вызывается цехами через формальный контракт и возвращает artifact + evidence.</p></div>`;
}