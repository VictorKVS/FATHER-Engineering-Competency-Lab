const script=document.createElement("script");
script.src="./model.js";
script.onload=init;
document.head.appendChild(script);

let currentLayer="business";

function init(){
  const model=window.FATHER_MODEL;
  renderTabs(model.layers);
  renderBusiness();
}
function renderTabs(layers){
  const el=document.getElementById("layerTabs");
  el.innerHTML="";
  layers.forEach((l)=>{
    const b=document.createElement("button");
    const enabled=["business","bpmn"].includes(l.id);
    b.className="tab "+(currentLayer===l.id?"active":enabled?"":"locked");
    b.textContent=l.name;
    b.onclick=()=>{
      if(!enabled){showLayerPlaceholder(l);return;}
      currentLayer=l.id;
      renderTabs(layers);
      if(l.id==="business") renderBusiness();
      if(l.id==="bpmn") renderBpmnLayer();
    };
    el.appendChild(b);
  });
}
function renderBusiness(){
  const model=window.FATHER_MODEL;
  const c=document.getElementById("factoryCanvas");
  c.className="factory-canvas";
  document.querySelector(".canvas-title h1").textContent="Слой 1. Бизнес-модель фабрики";
  document.querySelector(".canvas-title p").textContent="От идеи заказчика до выпуска продукта. Нажмите на цех или поток.";
  document.getElementById("modelStatus").textContent="MODEL: FATHER-FACTORY-L0";
  document.getElementById("modeStatus").textContent="MODE: BUSINESS DESIGN";
  document.getElementById("selectedStatus").textContent="SELECTED: —";
  document.getElementById("inspector").innerHTML='<div class="inspector-empty"><h2>Инспектор</h2><p>Выберите цех или поток на сборочном столе.</p></div>';
  renderCanvas(model.nodes,model.flows);
}
function renderBpmnLayer(){
  renderBpmn();
  document.getElementById("modelStatus").textContent="MODEL: FATHER-FACTORY-BPMN-L1";
  document.getElementById("modeStatus").textContent="MODE: PROCESS DESIGN";
  document.getElementById("selectedStatus").textContent="SELECTED: —";
}
function renderCanvas(nodes,flows){
  const c=document.getElementById("factoryCanvas");
  c.innerHTML="";
  nodes.forEach((n,i)=>{
    const card=document.createElement("article");
    card.className="node "+n.kind;
    card.dataset.id=n.id;
    card.innerHTML=`<div class="step">${n.step}</div><h3>${n.name}</h3><p>${n.purpose}</p><span class="badge ${n.status}">${n.status}</span>`;
    card.onclick=()=>inspectNode(n,card);
    c.appendChild(card);
    if(i<nodes.length-1){
      const f=flows.find(x=>x.producer===n.id && x.consumer===nodes[i+1].id);
      const flow=document.createElement("div");
      flow.className="flow";
      if(f){
        flow.title=f.name;
        flow.innerHTML=`<div class="flow-label">${f.name}</div>`;
        flow.onclick=()=>inspectFlow(f);
      }
      c.appendChild(flow);
    }
  });
}
function clearSelected(){
  document.querySelectorAll(".node.selected").forEach(x=>x.classList.remove("selected"));
}
function inspectNode(n,card){
  clearSelected();card.classList.add("selected");
  document.getElementById("selectedStatus").textContent="SELECTED: "+n.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${n.name}</h2>
    <div class="kv"><div class="k">ID</div><div class="v">${n.id}</div></div>
    <div class="kv"><div class="k">Статус</div><div class="v">${n.status}</div></div>
    <div class="kv"><div class="k">Назначение</div><div class="v">${n.purpose}</div></div>
    <div class="kv"><div class="k">Выход</div><div class="v">${n.output}</div></div>
    <div class="section"><h3>Следующий drill-down</h3><ul class="list"><li>BPMN L1/L2</li><li>Роли и activities</li><li>Информационные потоки</li><li>API contracts</li><li>Tests / Security / Evidence</li></ul></div>`;
}
function inspectFlow(f){
  clearSelected();
  document.getElementById("selectedStatus").textContent="SELECTED: "+f.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${f.name}</h2>
    <div class="kv"><div class="k">Flow ID</div><div class="v">${f.id}</div></div>
    <div class="kv"><div class="k">Producer</div><div class="v">${f.producer}</div></div>
    <div class="kv"><div class="k">Consumer</div><div class="v">${f.consumer}</div></div>
    <div class="kv"><div class="k">Payload</div><div class="v">${f.payload}</div></div>
    <div class="kv"><div class="k">Protocol</div><div class="v">${f.protocol}</div></div>
    <div class="kv"><div class="k">Quality/Gate</div><div class="v">${f.quality}</div></div>
    <div class="section"><h3>API Design fields</h3><ul class="list"><li>endpoint / event</li><li>schema</li><li>volume / peak</li><li>latency / timeout</li><li>retry / idempotency</li><li>authn / authz</li><li>validation</li><li>observability</li><li>error contract</li></ul></div>`;
}
function showLayerPlaceholder(layer){
  document.getElementById("inspector").innerHTML=`<h2>${layer.name}</h2><p>Слой зарезервирован. Он будет строиться из той же machine-readable модели после завершения предыдущего gate.</p>`;
}
