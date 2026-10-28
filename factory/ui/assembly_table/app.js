const script=document.createElement("script");
script.src="./model.js";
script.onload=init;
document.head.appendChild(script);

let currentLayer="business";

function init(){
  renderTabs(window.FATHER_MODEL.layers);
  renderBusiness();
}

function renderTabs(layers){
  const el=document.getElementById("layerTabs");
  el.innerHTML="";
  layers.forEach((l)=>{
    const enabled=["business","bpmn","api","engine","automation"].includes(l.id);
    const b=document.createElement("button");
    b.className="tab "+(currentLayer===l.id?"active":enabled?"":"locked");
    b.textContent=l.name;
    b.onclick=()=>{
      if(!enabled){showLayerPlaceholder(l);return;}
      currentLayer=l.id;
      renderTabs(layers);
      if(l.id==="business") renderBusiness();
      if(l.id==="bpmn") renderBpmnLayer();
      if(l.id==="api") renderApiLayer();
      if(l.id==="engine") renderEngineLayer();
      if(l.id==="automation") renderAutomationLayer();
    };
    el.appendChild(b);
  });
}

function resetInspector(text){
  document.getElementById("selectedStatus").textContent="SELECTED: —";
  document.getElementById("inspector").innerHTML='<div class="inspector-empty"><h2>Инспектор</h2><p>'+text+'</p></div>';
}

function renderBusiness(){
  const model=window.FATHER_MODEL;
  const c=document.getElementById("factoryCanvas");
  c.className="factory-canvas";
  document.querySelector(".canvas-title h1").textContent="Слой 1. Бизнес-модель фабрики";
  document.querySelector(".canvas-title p").textContent="От идеи заказчика до выпуска продукта. Нажмите на цех или поток.";
  document.getElementById("modelStatus").textContent="MODEL: FATHER-FACTORY-L0";
  document.getElementById("modeStatus").textContent="MODE: BUSINESS DESIGN";
  resetInspector("Выберите цех или поток на сборочном столе.");
  renderCanvas(model.nodes,model.flows);
}

function renderBpmnLayer(){
  renderBpmn();
  document.getElementById("modelStatus").textContent="MODEL: FATHER-FACTORY-BPMN-L1";
  document.getElementById("modeStatus").textContent="MODE: PROCESS DESIGN";
  document.getElementById("selectedStatus").textContent="SELECTED: —";
}

function renderApiLayer(){
  renderApi();
  document.getElementById("modelStatus").textContent="MODEL: FATHER-FACTORY-API-LAYER";
  document.getElementById("modeStatus").textContent="MODE: API / EVENT DESIGN";
  resetInspector("Выберите контракт передачи между цехами.");
}

function renderAutomationLayer(){
  renderAutomation();
  document.getElementById("modelStatus").textContent="MODEL: FATHER-AUTOMATION-CANVAS";
  document.getElementById("modeStatus").textContent="MODE: WORKFLOW DESIGN";
  resetInspector("Выберите узел или готовый workflow-шаблон.");
}

function renderEngineLayer(){
  renderEngine();
  document.getElementById("modelStatus").textContent="MODEL: FATHER-ENGINE";
  document.getElementById("modeStatus").textContent="MODE: AGENT RUNTIME";
  resetInspector("Выберите слой двигателя FATHER.");
}

function renderWorkshop01Layer(){
  currentLayer="business";
  renderTabs(window.FATHER_MODEL.layers);
  renderWorkshop01();
  document.getElementById("modelStatus").textContent="MODEL: W01-BUSINESS-ANALYSIS";
  document.getElementById("modeStatus").textContent="MODE: WORKSHOP DRILL-DOWN";
  resetInspector("Выберите операцию Business Analysis Workshop.");
}

function renderCanvas(nodes,flows){
  const c=document.getElementById("factoryCanvas");
  c.innerHTML="";
  nodes.forEach((n,i)=>{
    const card=document.createElement("article");
    card.className="node "+n.kind;
    card.dataset.id=n.id;
    card.innerHTML=`<div class="step">${n.step}</div><h3>${n.name}</h3><p>${n.purpose}</p><span class="badge ${n.status}">${n.status}</span>`;
    card.onclick=()=>{
      if(n.id==="W01"){ renderWorkshop01Layer(); return; }
      inspectNode(n,card);
    };
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
  clearSelected(); card.classList.add("selected");
  document.getElementById("selectedStatus").textContent="SELECTED: "+n.id;
  document.getElementById("inspector").innerHTML=`
    <h2>${n.name}</h2>
    <div class="kv"><div class="k">ID</div><div class="v">${n.id}</div></div>
    <div class="kv"><div class="k">Статус</div><div class="v">${n.status}</div></div>
    <div class="kv"><div class="k">Назначение</div><div class="v">${n.purpose}</div></div>
    <div class="kv"><div class="k">Выход</div><div class="v">${n.output}</div></div>
    <div class="section"><h3>Drill-down</h3><ul class="list"><li>BPMN L1/L2</li><li>Роли и activities</li><li>Информационные потоки</li><li>API contracts</li><li>Tests / Security / Evidence</li></ul></div>`;
}

function inspectFlow(f){
  clearSelected();
  document.getElementById("selectedStatus").textContent="SELECTED: "+f.id;
  const api=window.FATHER_API.flows.find(x=>x.producer===f.producer && x.consumer===f.consumer);
  document.getElementById("inspector").innerHTML=`
    <h2>${f.name}</h2>
    <div class="kv"><div class="k">Flow ID</div><div class="v">${f.id}</div></div>
    <div class="kv"><div class="k">Producer</div><div class="v">${f.producer}</div></div>
    <div class="kv"><div class="k">Consumer</div><div class="v">${f.consumer}</div></div>
    <div class="kv"><div class="k">Payload</div><div class="v">${f.payload}</div></div>
    <div class="kv"><div class="k">Protocol</div><div class="v">${f.protocol}</div></div>
    <div class="kv"><div class="k">Quality/Gate</div><div class="v">${f.quality}</div></div>
    ${api?'<div class="section"><h3>API/Event Contract</h3><ul class="list"><li>Event: '+api.endpoint_or_event+'</li><li>Validation: '+api.validation+'</li><li>Idempotency: '+api.idempotency+'</li><li>Observability: '+api.observability+'</li></ul></div>':''}
  `;
}

function showLayerPlaceholder(layer){
  document.getElementById("inspector").innerHTML=`<h2>${layer.name}</h2><p>Слой зарезервирован и будет подключён к той же machine-readable модели.</p>`;
}
