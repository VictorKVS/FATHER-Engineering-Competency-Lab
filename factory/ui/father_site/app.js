const blocks=[
 {id:"agentDiscovery",stableId:"FBLK-001",type:"FACTORY_BLOCK",title:"BLOCK-01 · Поиск агентов",desc:"READ ONLY · обнаружение агентов и профилей",x:55,y:48,cls:"factory discovery"},
 {id:"agentCatalog",stableId:"FBLK-002",type:"FACTORY_BLOCK",title:"BLOCK-02 · Список агентов",desc:"Каталог · описание · maturity · gaps",x:265,y:48,cls:"factory catalog"},
 {id:"input",stableId:"BLK-001",type:"INPUT",title:"Входной контракт",desc:"Явный вход агента",x:55,y:120},
 {id:"role",stableId:"BLK-002",type:"ROLE",title:"Роль",desc:"Кто агент и за что отвечает",x:245,y:70},
 {id:"prompt",stableId:"BLK-003",type:"PROMPT",title:"Промпт",desc:"Версионируемая инструкция",x:245,y:180},
 {id:"rag",stableId:"BLK-004",type:"RAG",title:"RAG",desc:"Поиск релевантного знания",x:435,y:70},
 {id:"kb",stableId:"BLK-005",type:"KB",title:"База знаний",desc:"База знаний профиля",x:435,y:180},
 {id:"model",stableId:"BLK-006",type:"MODEL_SLOT",title:"Слот модели",desc:"Сменная локальная LLM",x:625,y:125,cls:"model"},
 {id:"output",stableId:"BLK-007",type:"OUTPUT",title:"Выходной контракт",desc:"Структурированный результат",x:815,y:70},
 {id:"eval",stableId:"BLK-008",type:"EVAL",title:"Оценки",desc:"Контракт + качество",x:815,y:180},
 {id:"evidence",stableId:"BLK-009",type:"EVIDENCE",title:"Доказательства",desc:"Кто / что / версия / PASS",x:1005,y:125,cls:"evidence"}
];
const edges=[["agentDiscovery","agentCatalog"],["agentCatalog","role"],["input","role"],["role","rag"],["role","prompt"],["prompt","model"],["rag","model"],["kb","model"],["model","output"],["output","eval"],["eval","evidence"]];
const palette=[
 ["AGENT_DISCOVERY","01","Поиск агентов","READ ONLY · обнаружение кандидатов"],
 ["AGENT_CATALOG","02","Список агентов","Описание · maturity · gaps"],
 ["ROLE","R","Роль","Ответственность агента"],["PROMPT","P","Промпт","Версия инструкций"],["RAG","G","RAG","Извлечение знаний"],["KB","K","База знаний","Доменная база знаний"],["MODEL_SLOT","M","Слот модели","Сменная LLM"],["CONTRACT","C","Контракт","Вход / выход"],["EVAL","E","Оценка","Проверка качества"],["EVIDENCE","V","Доказательства","Доказательства"]
];
const models=[
 {id:"MDL-GIGACHAT20-Q4",name:"GigaChat 20B A3B Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT20-V15-Q4",name:"GigaChat 20B A3B v1.5 Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT3-10B-Q4KS",name:"GigaChat3 10B A1.8B Q4_K_S",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-QWEN25-14B-1M-Q4",name:"Qwen2.5 14B Instruct 1M Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-DEEPSEEK-CODER-V2-LITE-Q4",name:"DeepSeek Coder V2 Lite Q4_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"},
 {id:"MDL-DEEPSEEK-CODER-V2-LITE-Q5",name:"DeepSeek Coder V2 Lite Q5_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"},
 {id:"MDL-QWEN25-CODER-14B-Q4",name:"Qwen2.5 Coder 14B Q4_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"}
];
const config={
 agent_id:"AG-001",profile:"ALINA_LITERARY",capability:"STORY_CONTINUATION",
 role:"Литературный профиль ALINA. Продолжает рассказ, сохраняя канон, персонажей, POV и причинность.",
 prompt_version:"0.2.0",rag_version:"ALINA_LITERARY_RAG_V02",kb_version:"0.2.0",
 selected_model:"MDL-QWEN25-14B-1M-Q4"
};

const blockDocs={
  agentDiscovery:{
  purpose:"Ищет существующие агенты, профили и agent-like артефакты. Работает READ ONLY и выдаёт кандидатов с confidence и evidence.",
  repoPath:"factory/blocks/BLOCK_01_AGENT_DISCOVERY.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/factory/blocks/BLOCK_01_AGENT_DISCOVERY.yaml",
  editor:"Factory block / discovery contract",
  version:"FATHER_BLOCK_01_AGENT_DISCOVERY v1.0.0"
 },
 agentCatalog:{
  purpose:"Принимает результаты поиска и канонический AGENT_REGISTRY, нормализует их в единый список агентов с назначением, maturity, status, составом и gaps.",
  repoPath:"factory/blocks/BLOCK_02_AGENT_CATALOG.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/factory/blocks/BLOCK_02_AGENT_CATALOG.yaml",
  editor:"Factory block / catalog contract",
  version:"FATHER_BLOCK_02_AGENT_CATALOG v1.0.0"
 },
 input:{
  purpose:"Определяет явный вход агента: какие данные он принимает, какие поля обязательны и что считается некорректным входом.",
  repoPath:"agents/alina/profiles/literary/INPUT_CONTRACT.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/INPUT_CONTRACT.yaml",
  editor:"YAML contract",
  version:"father.alina.literary.input.v1"
 },
 role:{
  purpose:"Определяет идентичность, ответственность, границы и назначение агента. Это не модель, а постоянная роль изделия.",
  repoPath:"agents/alina/profiles/literary/README.md",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/",
  editor:"ALINA Literary profile",
  version:"0.2.0"
 },
 prompt:{
  purpose:"Версионируемая инструкция, которая управляет поведением агента при неизменных контрактах и доменной модели.",
  repoPath:"agents/alina/profiles/literary/PROMPT.md",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/PROMPT.md",
  editor:"Markdown prompt",
  version:"0.2.0"
 },
 rag:{
  purpose:"Определяет, откуда и по каким правилам агент извлекает релевантные знания перед вызовом LLM.",
  repoPath:"agents/alina/profiles/literary/RAG_MANIFEST.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/RAG_MANIFEST.yaml",
  editor:"YAML RAG manifest",
  version:"ALINA_LITERARY_RAG_V02"
 },
 kb:{
  purpose:"Доменная база знаний литературного профиля: канон, непротиворечивость, персонажи, причинность и правила продолжения.",
  repoPath:"agents/alina/profiles/literary/KNOWLEDGE_BASE.md",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/KNOWLEDGE_BASE.md",
  editor:"Markdown knowledge base",
  version:"0.2.0"
 },
 model:{
  purpose:"Сменный вычислительный двигатель агента. Меняется без изменения Роль, Промпт, RAG, KB и контрактов.",
  repoPath:"factory/model_fabric/LOCAL_MODEL_CATALOG.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/factory/model_fabric/LOCAL_MODEL_CATALOG.yaml",
  editor:"Зоопарк моделей / профиль запуска",
  version:"catalog 1.0.0"
 },
 output:{
  purpose:"Определяет обязательную структуру результата агента и делает разные LLM взаимозаменяемыми на одном интерфейсе.",
  repoPath:"agents/alina/profiles/literary/OUTPUT_CONTRACT.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/OUTPUT_CONTRACT.yaml",
  editor:"YAML contract",
  version:"father.alina.literary.output.v1"
 },
 eval:{
  purpose:"Проверяет качество результата и hard-fail условия: нарушение канона, переименование персонажа, сломанный контракт и другие дефекты.",
  repoPath:"agents/alina/profiles/literary/EVALS/continuity.yaml",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/agents/alina/profiles/literary/EVALS/continuity.yaml",
  editor:"YAML evaluation rubric",
  version:"ALINA_LITERARY_CONTINUITY_V02"
 },
 evidence:{
  purpose:"Фиксирует доказательства выполнения: model_id, версии Промпт/RAG/KB, latency, contract status, review status и run_id.",
  repoPath:"benchmark_results/alina_literary/<RUN_ID>/",
  localPath:"G:/1/FATHER-Engineering-Competency-Lab-git/benchmark_results/alina_literary/<RUN_ID>/",
  editor:"Сгенерированные доказательства / пакет проверки",
  version:"доказательства выполнения"
 }
};
const blockDrafts={};

const naming=window.NEXUS_NAMING;
if(naming){
 document.getElementById("systemName").textContent=naming.name("SYS-001","NEXUS");
 document.getElementById("workspaceName").textContent=naming.name("WS-001","Agent Designer");
 blocks.forEach(b=>{ if(b.stableId) b.title=naming.name(b.stableId,b.title); });
}

const paletteEl=document.getElementById("palette");
palette.forEach(([type,icon,title,desc])=>{
 const b=document.createElement("button");b.className="palette-item";
 b.innerHTML='<span class="palette-icon">'+icon+'</span><span><b>'+title+'</b><small>'+desc+'</small></span>';
 b.onclick=()=>toast(type+" уже представлен на canvas");paletteEl.appendChild(b);
});
const nodes=document.getElementById("nodes"),canvas=document.getElementById("canvas"),svg=document.getElementById("wires");
function renderNodes(){
 nodes.innerHTML="";
 blocks.forEach(b=>{
  const n=document.createElement("article");n.className="node "+(b.cls||"");n.dataset.id=b.id;n.style.left=b.x+"px";n.style.top=b.y+"px";
  const st=factoryBlockState[b.id];
  const stateClass=st ? (' state-'+st.status.toLowerCase()) : '';
  const actions=b.id==="agentDiscovery"
    ? '<div class="node-actions"><button type="button" class="node-action '+(st?.activated?"active-tone":"")+'" data-action="run-discovery">RUN</button></div>'
    : b.id==="agentCatalog"
      ? '<div class="node-actions"><button type="button" class="node-action '+(st?.activated?"active-tone":"")+'" data-action="show-catalog">СПИСОК</button></div>'
      : '';
  n.className+=" "+stateClass;
  n.innerHTML='<div class="nhead"><span class="nid">'+b.type+'</span><span class="state"></span></div><h3>'+b.title+'</h3><p>'+b.desc+'</p>'+actions;
  n.onclick=()=>selectBlock(b.id);n.ondblclick=e=>{e.stopPropagation();openBlockModal(b.id)};nodes.appendChild(n);
  const runBtn=n.querySelector('[data-action="run-discovery"]');
  if(runBtn)runBtn.onclick=e=>{e.stopPropagation();runAgentDiscoveryFromCard()};
  const listBtn=n.querySelector('[data-action="show-catalog"]');
  if(listBtn)listBtn.onclick=e=>{e.stopPropagation();openAgentCatalogFromCard()};
 });
 requestAnimationFrame(()=>{drawWires();enableNodeDragging();});
}
function edgeGeometry(A,B){
 const ax=A.offsetLeft+A.offsetWidth, ay=A.offsetTop+A.offsetHeight/2;
 const bx=B.offsetLeft, by=B.offsetTop+B.offsetHeight/2;
 const distance=Math.hypot(bx-ax,by-ay);
 return {ax,ay,bx,by,distance};
}
function proximityOpacity(distance){
 const SNAP_DISTANCE=150;
 const FADE_DISTANCE=420;
 if(distance<=SNAP_DISTANCE)return 1;
 if(distance>=FADE_DISTANCE)return 0;
 const t=(distance-SNAP_DISTANCE)/(FADE_DISTANCE-SNAP_DISTANCE);
 return 1-(t*t*(3-2*t));
}
function curvedPath({ax,ay,bx,by}){
 const span=Math.max(60,Math.abs(bx-ax));
 const bend=Math.min(180,Math.max(70,span*.46));
 return `M ${ax} ${ay} C ${ax+bend} ${ay}, ${bx-bend} ${by}, ${bx} ${by}`;
}
let flowMode=false;
function drawWires(){
 svg.innerHTML="";
 edges.forEach(([a,b],edgeIndex)=>{
  const A=document.querySelector('[data-id="'+a+'"]'),B=document.querySelector('[data-id="'+b+'"]');if(!A||!B)return;
  const g=edgeGeometry(A,B);
  const opacity=proximityOpacity(g.distance);
  if(opacity<=.01)return;

  const group=document.createElementNS("http://www.w3.org/2000/svg","g");
  group.setAttribute("class","wire-group"+(g.distance<=150?" magnetic":""));
  group.style.opacity=String(opacity);

  const base=document.createElementNS("http://www.w3.org/2000/svg","path");
  base.setAttribute("class","wire");
  base.setAttribute("d",curvedPath(g));
  base.dataset.edge=String(edgeIndex);
  group.appendChild(base);

  const pulse=document.createElementNS("http://www.w3.org/2000/svg","path");
  pulse.setAttribute("class","wire-pulse"+(flowMode?" active":""));
  pulse.setAttribute("d",curvedPath(g));
  pulse.style.animationDelay=(edgeIndex*.12)+"s";
  group.appendChild(pulse);

  const p1=document.createElementNS("http://www.w3.org/2000/svg","circle");
  p1.setAttribute("class","wire-port");
  p1.setAttribute("cx",g.ax);p1.setAttribute("cy",g.ay);p1.setAttribute("r",g.distance<=150?4:2.5);
  group.appendChild(p1);
  const p2=p1.cloneNode();
  p2.setAttribute("cx",g.bx);p2.setAttribute("cy",g.by);
  group.appendChild(p2);

  svg.appendChild(group);
 });
}
function setFlowMode(value,duration=2600){
 flowMode=value;
 drawWires();
 document.querySelectorAll(".node").forEach(n=>n.classList.toggle("processing",value));
 if(value){
  clearTimeout(window.__flowTimer);
  window.__flowTimer=setTimeout(()=>{flowMode=false;drawWires();document.querySelectorAll(".node").forEach(n=>n.classList.remove("processing"));},duration);
 }
}
function enableNodeDragging(){
 let drag=null;
 document.querySelectorAll(".node").forEach(node=>{
  node.addEventListener("pointerdown",e=>{
   if(e.button!==0)return;
   const b=blocks.find(x=>x.id===node.dataset.id);if(!b)return;
   drag={node,b,startX:e.clientX,startY:e.clientY,originX:b.x,originY:b.y,moved:false};
   node.setPointerCapture(e.pointerId);
   node.classList.add("dragging");
  });
  node.addEventListener("pointermove",e=>{
   if(!drag||drag.node!==node)return;
   const dx=e.clientX-drag.startX,dy=e.clientY-drag.startY;
   if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;
   drag.b.x=Math.max(8,drag.originX+dx);
   drag.b.y=Math.max(46,drag.originY+dy);
   node.style.left=drag.b.x+"px";node.style.top=drag.b.y+"px";
   drawWires();
  });
  node.addEventListener("pointerup",e=>{
   if(!drag||drag.node!==node)return;
   const moved=drag.moved;
   node.classList.remove("dragging");
   node.releasePointerCapture(e.pointerId);
   drag=null;
   drawWires();
   if(moved)e.stopPropagation();
  });
 });
}
function selectBlock(id){
 document.querySelectorAll(".node").forEach(n=>n.classList.toggle("selected",n.dataset.id===id));
 const b=blocks.find(x=>x.id===id);const ins=document.getElementById("inspector");document.getElementById("inspectorType").textContent=b.type;
 let html='<div class="info-box"><b>'+b.title+'</b><p>'+b.desc+'</p></div>';
 if(id==="role")html+=field("Agent ID",config.agent_id)+area("Роль",config.role);
 else if(id==="prompt")html+=field("Промпт version",config.prompt_version)+area("Промпт","Продолжай исходный рассказ. Сохраняй канон, POV, время, персонажей и открытые сюжетные линии. Возвращай JSON по Выходной контракт.");
 else if(id==="rag")html+=field("RAG version",config.rag_version)+field("Mode","LOCAL_SIMPLE_RETRIEVAL");
 else if(id==="kb")html+=field("KB version",config.kb_version)+'<div class="info-box"><b>Sections</b><p><span class="tag">Canon</span><span class="tag">Continuity</span><span class="tag">Characters</span><span class="tag">Causality</span></p></div>';
 else if(id==="model")html+='<div class="info-box"><b>Сменяемый движок</b><p>Модель меняется без изменения Роль / Промпт / RAG / KB / Контрактs.</p></div>'+field("Выбрано",config.selected_model);
 else if(id==="input")html+=area("Схема",'story_text: string\ntarget_length: integer\nconstraints: string[]');
 else if(id==="output")html+=area("Обязательные поля",'continuation\ncontinuity\ncanon_delta\nproposals\nmodel_id');
 else if(id==="eval")html+='<div class="info-box"><b>Критический отказ</b><p>contract invalid · canon contradiction · renamed character · rewrite instead of continuation</p></div>';
 else html+='<div class="info-box"><b>Происхождение данных</b><p>model_id · agent_id · prompt/RAG/KB versions · latency · contract status · review status</p></div>';
 ins.innerHTML=html;
}
function field(label,value){return '<div class="field"><label>'+label+'</label><input value="'+String(value).replaceAll('"','&quot;')+'"></div>'}
function area(label,value){return '<div class="field"><label>'+label+'</label><textarea>'+value+'</textarea></div>'}
const sel=document.getElementById("modelSelect");
models.forEach(m=>{const o=document.createElement("option");o.value=m.id;o.textContent=m.name+(m.status==="EXPERIMENTAL"?" · EXP":"");sel.appendChild(o)});sel.value=config.selected_model;
function renderModel(){const m=models.find(x=>x.id===sel.value);config.selected_model=m.id;document.getElementById("modelMeta").innerHTML='<b>'+m.id+'</b><br>'+m.type+' · '+m.runtime+' · '+m.status;document.getElementById("modelStatus").textContent=models.length+" candidates";}
sel.onchange=()=>{renderModel();selectBlock("model")};renderModel();
const checks=["Роль defined","Промпт versioned","RAG подключён","База знаний attached","Слот модели replaceable","Входной контракт","Выходной контракт","Оценки","Доказательства"];
document.getElementById("checklist").innerHTML=checks.map(x=>'<div class="check"><span>'+x+'</span><b>ГОТОВО</b></div>').join("");
document.getElementById("loadDemo").onclick=()=>{selectBlock("role");toast("ALINA Literary demo загружен")};
document.getElementById("validate").onclick=()=>{setFlowMode(true,3400);document.getElementById("gateStatus").textContent="CHECKING";document.getElementById("gateStatus").className="hold";toast("Проверка связей: импульс проходит по активной цепочке");setTimeout(()=>{document.getElementById("gateStatus").textContent="DESIGN PASS";document.getElementById("gateStatus").className="";},3200)};
document.getElementById("runDemo").onclick=()=>{setFlowMode(true,4200);toast("AG-001: визуальный проход данных через активные связи · "+config.selected_model)};
document.getElementById("exportBtn").onclick=()=>{
 const data={...config,model_candidates:models.map(x=>x.id),blocks:blocks.map(({id,type,title})=>({id,type,title})),edges};
 const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="father-agent-design.json";a.click();URL.revokeObjectURL(a.href);toast("Agent design JSON экспортирован");
};
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.remove("show"),2200)}

let currentModalBlock=null,currentModalTab="about";
const modal=document.getElementById("blockModal"),modalBody=document.getElementById("blockModalBody");
function openBlockModal(id){
 currentModalBlock=id;currentModalTab="about";
 const b=blocks.find(x=>x.id===id),d=blockDocs[id]||{};
 document.getElementById("blockModalEyebrow").textContent=b.type+" · "+id.toUpperCase();
 document.getElementById("blockModalTitle").textContent=b.title;
 document.getElementById("blockModalSubtitle").textContent=b.desc;
 document.querySelectorAll(".modal-tab").forEach(x=>x.classList.toggle("active",x.dataset.modalTab==="about"));
 renderModalTab();
 modal.classList.add("open");modal.setAttribute("aria-hidden","false");
}
function closeBlockModal(){modal.classList.remove("open");modal.setAttribute("aria-hidden","true")}
function demoLaunchpadHtml(){
 return '<div class="modal-section demo-launchpad">'+
  '<div class="demo-launchpad-head"><div><h4>ДЕМО-ПРОДУКТЫ</h4><p>Один вход фабрики · один процесс 000–100 · разные изделия.</p></div><span>ПРЕСЕТЫ ФАБРИКИ</span></div>'+
  '<div class="demo-launchpad-grid">'+
   '<button class="demo-product-card" data-demo-product="story"><b>DEMO 1</b><strong>Рассказ / Смена модели</strong><small>Рассказ · сменяемая LLM · failover · eval · evidence</small><i>СТАРТ 000 →</i></button>'+
   '<button class="demo-product-card" data-demo-product="osint"><b>DEMO 2</b><strong>OSINT-исследование</strong><small>Research Request · sources · corroboration · evidence</small><i>СТАРТ 000 →</i></button>'+
   '<button class="demo-product-card" data-demo-product="security"><b>DEMO 3</b><strong>Анализ безопасности</strong><small>Assets · threats · risks · controls · acceptance</small><i>СТАРТ 000 →</i></button>'+
  '</div></div>';
}
function bindDemoLaunchpad(){
 document.querySelectorAll("[data-demo-product]").forEach(btn=>{
  btn.onclick=()=>{
   const demo=btn.dataset.demoProduct;
   closeBlockModal();
   location.href="./stage000.html?demo="+encodeURIComponent(demo);
  };
 });
}
function renderModalTab(){
 const b=blocks.find(x=>x.id===currentModalBlock),d=blockDocs[currentModalBlock]||{};
 if(currentModalTab==="about"){
  modalBody.innerHTML=
   (currentModalBlock==="input"?demoLaunchpadHtml():"")+
   '<div class="modal-grid">'+
    '<div class="modal-section"><h4>Назначение</h4><p>'+d.purpose+'</p></div>'+
    '<div class="modal-section"><h4>В составе агента</h4><p><b>'+b.type+'</b> · '+b.desc+'</p></div>'+
    '<div class="modal-section"><h4>Версия</h4><p>'+d.version+'</p></div>'+
    '<div class="modal-section"><h4>Связи</h4><p>'+edgeSummary(currentModalBlock)+'</p></div>'+
   '</div>';
  if(currentModalBlock==="input")requestAnimationFrame(bindDemoLaunchpad);
 }else if(currentModalTab==="location"){
  modalBody.innerHTML=
   '<div class="modal-section"><h4>GitHub / Репозиторий</h4><code>'+d.repoPath+'</code></div>'+
   '<div class="modal-section"><h4>Локальное расположение</h4><code>'+d.localPath+'</code></div>'+
   '<div class="modal-section"><h4>Чем редактируется</h4><p>'+d.editor+'</p></div>'+
   '<div class="modal-section"><h4>Как работает изменение</h4><p>Изменение сначала живёт как локальный draft в интерфейсе. Затем его можно экспортировать и перенести в канонический файл FATHER, после чего изменение должно пройти тесты и evidence.</p></div>';
 }else{
  const alinaEditable=["role","prompt","rag","kb"].includes(currentModalBlock);
  if(alinaEditable){
   modalBody.innerHTML=
    '<div class="modal-section alina-edit-launch">'+
    '<div class="alina-launch-orb">A</div>'+
    '<div><h4>Редактирование через ALINA Analyst</h4>'+
    '<p>Этот блок относится к интеллектуальной части агента. Его изменение выполняется через аналитическое ядро ALINA: цель → источники → граф знаний → proposal → eval → новая версия.</p>'+
    '<button class="primary alina-launch-btn" id="openAlinaEditor">'+editorRouteForBlock(currentModalBlock).label+'</button>'+
    '<p class="edit-note">ALINA не заменяет канон напрямую: новая редакция сначала создаётся как PROPOSAL и должна пройти проверки.</p></div>'+
    '</div>';
   requestAnimationFrame(()=>{
    const btn=document.getElementById("openAlinaEditor");
    if(btn)btn.onclick=()=>{location.href=editorRouteForBlock(currentModalBlock).url};
   });
  }else{
   const draft=blockDrafts[currentModalBlock]||defaultEditableValue(currentModalBlock);
   modalBody.innerHTML=
    '<div class="modal-section edit-section"><h4>Редактирование блока</h4>'+
    '<label>Заголовок<input id="modalEditTitle" value="'+escapeHtml(b.title)+'"></label>'+
    '<label>Описание<textarea id="modalEditDesc">'+escapeHtml(draft.desc)+'</textarea></label>'+
    '<label>Конфигурация / заметки<textarea id="modalEditConfig">'+escapeHtml(draft.config)+'</textarea></label>'+
    '<p class="edit-note">Сохранение здесь меняет только текущий UI draft. Канонический файл в GitHub изменяется отдельным инженерным коммитом после проверки.</p></div>';
  }
 }
}

function editorRouteForBlock(id){
 const routes={
  role:{workspace:"ALINA",url:"./artifact.html?artifact=role",label:"Редактировать в Knowledge & Reasoning Engineer"},
  prompt:{workspace:"ALINA",url:"./artifact.html?artifact=prompt",label:"Редактировать в Knowledge & Reasoning Engineer"},
  rag:{workspace:"ALINA",url:"./artifact.html?artifact=rag",label:"Редактировать в Knowledge & Reasoning Engineer"},
  kb:{workspace:"ALINA",url:"./knowledge.html",label:"Открыть Knowledge Architecture Studio"}
 };
 return routes[id]||{workspace:"LOCAL",url:null,label:"Редактировать"};
}

function defaultEditableValue(id){
 const b=blocks.find(x=>x.id===id),d=blockDocs[id]||{};
 return {desc:b.desc,config:"repo: "+(d.repoPath||"")+"\nversion: "+(d.version||"")};
}
function edgeSummary(id){
 const incoming=edges.filter(x=>x[1]===id).map(x=>blocks.find(b=>b.id===x[0])?.title);
 const outgoing=edges.filter(x=>x[0]===id).map(x=>blocks.find(b=>b.id===x[1])?.title);
 return "Входы: "+(incoming.join(", ")||"—")+"<br>Выходы: "+(outgoing.join(", ")||"—");
}
function escapeHtml(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
document.getElementById("blockModalClose").onclick=closeBlockModal;
document.getElementById("blockModalBackdrop").onclick=closeBlockModal;
document.querySelectorAll(".modal-tab").forEach(tab=>tab.onclick=()=>{currentModalTab=tab.dataset.modalTab;document.querySelectorAll(".modal-tab").forEach(x=>x.classList.toggle("active",x===tab));renderModalTab()});
document.getElementById("blockModalSave").onclick=()=>{
 if(currentModalTab!=="edit"){currentModalTab="edit";document.querySelectorAll(".modal-tab").forEach(x=>x.classList.toggle("active",x.dataset.modalTab==="edit"));renderModalTab();toast(["role","prompt","rag","kb"].includes(currentModalBlock)?"Редактирование передано в ALINA":"Режим редактирования открыт");return}
 if(["role","prompt","rag","kb"].includes(currentModalBlock)){location.href=editorRouteForBlock(currentModalBlock).url;return}
 const b=blocks.find(x=>x.id===currentModalBlock);
 const title=document.getElementById("modalEditTitle")?.value?.trim()||b.title;
 const desc=document.getElementById("modalEditDesc")?.value??b.desc;
 const cfg=document.getElementById("modalEditConfig")?.value??"";
 b.title=title;b.desc=desc;blockDrafts[currentModalBlock]={desc,config:cfg};
 renderNodes();selectBlock(currentModalBlock);toast("Локальный draft блока сохранён");
};
document.getElementById("blockModalExport").onclick=()=>{
 const b=blocks.find(x=>x.id===currentModalBlock),d=blockDocs[currentModalBlock]||{};
 const payload={block_id:currentModalBlock,type:b.type,title:b.title,description:b.desc,repository_path:d.repoPath,local_path:d.localPath,version:d.version,draft:blockDrafts[currentModalBlock]||null};
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="father-block-"+currentModalBlock+".json";a.click();URL.revokeObjectURL(a.href);toast("Карточка блока экспортирована");
};
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&modal.classList.contains("open"))closeBlockModal()});


const cloneModal=document.getElementById("cloneModal");
function openCloneModal(){cloneModal.classList.add("open");cloneModal.setAttribute("aria-hidden","false")}
function closeCloneModal(){cloneModal.classList.remove("open");cloneModal.setAttribute("aria-hidden","true")}
document.getElementById("cloneAgent").onclick=openCloneModal;
document.getElementById("cloneClose").onclick=closeCloneModal;
document.getElementById("cloneCancel").onclick=closeCloneModal;
document.getElementById("cloneBackdrop").onclick=closeCloneModal;
document.getElementById("cloneCreate").onclick=()=>{
 const stableId=document.getElementById("cloneStableId").value.trim();
 const publicName=document.getElementById("clonePublicName").value.trim();
 const codeName=document.getElementById("cloneCodeName").value.trim();
 const purpose=document.getElementById("clonePurpose").value.trim();
 const domain=document.getElementById("cloneDomain").value.trim();
 if(!stableId||!publicName||!codeName||!purpose||!domain){toast("Заполните identity, purpose и domain");return}
 const payload={
  schema:"AGENT_CLONE_REQUEST_V1",
  clone_id:"CLONE-"+Date.now(),
  source_template:{agent_id:"AGENT-TEMPLATE-001",version:"1.0.0",required_gate:"PASS"},
  target_identity:{stable_id:stableId,public_name:publicName,code_name:codeName,purpose,domain},
  state:"CLONED_DRAFT",
  inherited:["package_structure","evidence_contract","handoff_contract","versioning","provenance","security_baseline","naming_registry_binding"],
  rebuild_required:["role","prompt","rag","knowledge_base","tools","model_policy","training_program","eval_profile","acceptance"],
  validation_required:["schema_validation","contract_tests","intelligence_package_gate","eval_suite","security_gate","regression","evidence_gate"]
 };
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
 const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="agent-clone-"+stableId+".json";a.click();URL.revokeObjectURL(a.href);
 closeCloneModal();
 toast("CLONED_DRAFT создан: "+publicName);
};


let lastDiscoveryReport=null;
const factoryBlockState={
 agentDiscovery:{status:"IDLE",activated:false},
 agentCatalog:{status:"IDLE",activated:false}
};
const fatherAgents=[
 {id:"AG-000",name:"PRODUCT_MANAGER",domain:"product_discovery",maturity:"M2",desc:"Product discovery и работа с замыслом заказчика.",launch:"Factory runtime / профиль PRODUCT_MANAGER",connect:"К STAGE 000–009, входу заказчика, бизнес-требованиям и проектному контуру."},
 {id:"AG-001",name:"ALINA",domain:"analysis_knowledge_process",maturity:"M4",desc:"Аналитическое ядро и архитектор знаний.",launch:"alina-knowledge-worker / процессный runtime",connect:"К RAG, Knowledge Base, OSINT evidence и специализированным аналитическим профилям."},
 {id:"AG-002",name:"SECURITY_SPECIALIST",domain:"information_security",maturity:"M3",desc:"ИБ-архитектура, риски, требования и контроль безопасности.",launch:"SecGraph / security package",connect:"К Security Gate, threat model, risk register, compliance и DevSecOps."},
 {id:"AG-003",name:"TIMA",domain:"infrastructure_devsecops_runtime",maturity:"M3",desc:"DevOps / DevSecOps / инфраструктурный исполнитель.",launch:"TIMA profile / approved infrastructure executor",connect:"К CI/CD, Docker, Kubernetes, runtime, deployment, observability и инфраструктурным задачам."},
 {id:"AG-004",name:"FATHER_CODEX",domain:"software_engineering",maturity:"M2",desc:"Программирование и трассируемая реализация.",launch:"FATHER_CODEX runtime / coding workflow",connect:"К архитектурным заданиям, GitHub, тестам, SAST и сборке программных модулей."},
 {id:"AG-005",name:"PIONEER",domain:"infrastructure_architecture",maturity:"M4",desc:"Архитектор инфраструктуры и topology/dependency design.",launch:"PIONEER-00 / architecture workflow",connect:"Перед TIMA: topology, dependency graph, addressing, BOM и acceptance plan."},
 {id:"AG-006",name:"FATHER_TEST_ENGINEER",domain:"testing_verification",maturity:"M2",desc:"Проектирование тестов узлов, связей, цепочек и системы.",launch:"Factory test package",connect:"К любому блоку перед gate: node/edge/chain/subgraph/system tests."},
 {id:"AG-007",name:"QA_EVALS",domain:"quality_evaluation",maturity:"M1",desc:"Независимый quality/eval gate.",launch:"Factory QA/Eval profile",connect:"После исполнения агента и перед evidence/release gate."},
 {id:"AG-008",name:"OPTIMIZATION_ENGINE",domain:"optimization_experiments",maturity:"M1",desc:"A/B и многокритериальная оптимизация.",launch:"Factory optimization profile",connect:"После появления стабильного baseline; к Model Tournament и A/B экспериментам."},
 {id:"AG-009",name:"POLYGON",domain:"adversarial_verification",maturity:"M2",desc:"Независимое испытание frozen Release Candidate.",launch:"Polygon contour / independent verifier",connect:"Только к зафиксированному Release Candidate после Factory qualification."},
 {id:"AG-010",name:"OSINT_EXPERT",domain:"open_source_intelligence",maturity:"M4",desc:"Поиск, сбор, provenance и evidence supply.",launch:"OSINT_deepseek / FATHER OSINT runtime",connect:"К ALINA и исследовательским задачам как поставщик источников, provenance и evidence."}
];

function renderAgentBlockOutput(mode="ready"){
 const host=document.getElementById("agentBlockOutput");
 if(!host)return;
 const discovered=lastDiscoveryReport?.schema==="FATHER_AGENT_DISCOVERY_RESULTS_V2" ? lastDiscoveryReport.count : "—";
 host.innerHTML=
   '<div class="agent-output-head"><div><span>FACTORY BLOCK OUTPUT</span><h3>BLOCK-01 → BLOCK-02</h3><p>Запуск и просмотр результатов выполняются прямо из карточек на поле.</p></div>'+
   '<div class="agent-output-stats"><div><span>НАЙДЕНО</span><b>'+discovered+'</b></div><div><span>КАТАЛОГ</span><b>'+fatherAgents.length+'</b></div><div><span>STATUS</span><b class="'+(mode==="pass"?"pass":"hold")+'">'+(mode==="pass"?"PASS":"READY")+'</b></div></div></div>';
}

function refreshFactoryNodes(selectedId=null){
 const current=selectedId || document.querySelector(".node.selected")?.dataset.id || "role";
 renderNodes();
 selectBlock(current);
}

async function runAgentDiscoveryFromCard(){
 const n1=document.querySelector('[data-id="agentDiscovery"]');
 const n2=document.querySelector('[data-id="agentCatalog"]');
 factoryBlockState.agentDiscovery={status:"RUNNING",activated:true};
 factoryBlockState.agentCatalog={status:"IDLE",activated:false};
 refreshFactoryNodes("agentDiscovery");
 document.querySelector('[data-id="agentDiscovery"]')?.classList.add("processing");
 toast("BLOCK-01: поиск по доступным дискам...");
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("EXECUTION_START","BLOCK-01","RUNNING",{block:"AGENT_DISCOVERY"});
 try{
   const res=await fetch("http://127.0.0.1:8091/agent-discovery/run",{
     method:"POST",
     headers:{"Content-Type":"application/json"},
     body:JSON.stringify({})
   });
   if(!res.ok)throw new Error("HTTP "+res.status);
   lastDiscoveryReport=await res.json();
   factoryBlockState.agentDiscovery={status:"PASS",activated:true};
   factoryBlockState.agentCatalog={status:"READY",activated:false};
   refreshFactoryNodes("agentDiscovery");
   document.querySelector('[data-id="agentCatalog"]')?.classList.add("processing");
   await new Promise(r=>setTimeout(r,220));
   document.querySelector('[data-id="agentCatalog"]')?.classList.remove("processing");
   renderAgentBlockOutput("pass");
   document.getElementById("agentReportTitle").textContent="Отчёт поиска агентов";
   openAgentReport();
   if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("TEST_RESULT","BLOCK-01","PASS",{found:lastDiscoveryReport.count,sources:lastDiscoveryReport.sources?.length||0});
   toast("BLOCK-01 завершён: найдено "+lastDiscoveryReport.count+" кандидатов");
 }catch(err){
   factoryBlockState.agentDiscovery={status:"ERROR",activated:true};
   factoryBlockState.agentCatalog={status:"IDLE",activated:false};
   refreshFactoryNodes("agentDiscovery");
   toast("BLOCK-01 ERROR: runtime 8091 недоступен или поиск завершился ошибкой");
   if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("ERROR","BLOCK-01","ERROR",{message:String(err)});
 }
}

function openAgentCatalogFromCard(){
 factoryBlockState.agentCatalog={status:"OPEN",activated:true};
 refreshFactoryNodes("agentCatalog");
 lastDiscoveryReport={
   schema:"FATHER_AGENT_CATALOG_VIEW_V1",
   mode:"CATALOG",
   count:fatherAgents.length,
   candidates:fatherAgents.map(a=>({
     discovery_id:a.id,
     source:"FATHER_AGENT_REGISTRY",
     locator:"factory/agents/AGENT_REGISTRY.yaml",
     detected_name:a.name,
     confidence:"CANONICAL",
     description:a.desc,
     launch:a.launch,
     connect:a.connect,
     evidence:["agent_id:"+a.id,"domain:"+a.domain,"maturity:"+a.maturity]
   })),
   sources:[{root:"factory/agents/AGENT_REGISTRY.yaml",inspected:fatherAgents.length,truncated:false,skipped_dirs:0,errors:0}],
   confidence_counts:{CANONICAL:fatherAgents.length,HIGH:0,MEDIUM:0,LOW:0}
 };
 document.getElementById("agentReportTitle").textContent="Список агентов FATHER";
 openAgentReport();
}


const agentReportModal=document.getElementById("agentReportModal");
function closeAgentReport(){agentReportModal.classList.remove("open");agentReportModal.setAttribute("aria-hidden","true")}
function renderAgentReport(){
 const body=document.getElementById("agentReportBody");
 const summary=document.getElementById("agentReportSummary");
 if(!lastDiscoveryReport){summary.textContent="Результаты ещё не загружены.";body.innerHTML="";return}
 const filter=document.getElementById("agentReportFilter").value;
 const items=(lastDiscoveryReport.candidates||[]).filter(x=>filter==="ALL"||x.confidence===filter);
 const cc=lastDiscoveryReport.confidence_counts||{};
 summary.textContent="Найдено "+lastDiscoveryReport.count+" · CANONICAL "+(cc.CANONICAL||0)+" · HIGH "+(cc.HIGH||0)+" · MEDIUM "+(cc.MEDIUM||0)+" · LOW "+(cc.LOW||0);
 body.innerHTML=items.map(x=>{
   const details=x.description
     ? '<p class="agent-desc">'+escapeHtml(x.description)+'</p>'+
       '<div class="agent-how"><b>ЗАПУСК</b><span>'+escapeHtml(x.launch||"Не определён")+'</span></div>'+
       '<div class="agent-how"><b>ЛУЧШЕ ПОДКЛЮЧАТЬ</b><span>'+escapeHtml(x.connect||"Не определено")+'</span></div>'
     : '<p>'+escapeHtml((x.evidence||[]).join(" · "))+'</p>';
   return '<article class="agent-report-row">'+
   '<div class="agent-report-row-head"><b>'+escapeHtml(x.detected_name)+'</b><span class="conf '+escapeHtml(x.confidence.toLowerCase())+'">'+escapeHtml(x.confidence)+'</span></div>'+
   '<code>'+escapeHtml(x.locator)+'</code>'+details+
   '<small>'+escapeHtml(x.source)+' · '+escapeHtml(x.discovery_id)+'</small>'+
   '</article>';
 }).join("") || '<div class="agent-report-empty">По выбранному фильтру ничего нет.</div>';
}
function openAgentReport(){
 agentReportModal.classList.add("open");
 agentReportModal.setAttribute("aria-hidden","false");
 renderAgentReport();
}
document.getElementById("agentReportClose").onclick=closeAgentReport;
document.getElementById("agentReportBackdrop").onclick=closeAgentReport;
document.getElementById("agentReportFilter").onchange=renderAgentReport;
document.getElementById("agentReportShowSources").onclick=()=>{
 const body=document.getElementById("agentReportBody");
 const sources=lastDiscoveryReport?.sources||[];
 body.innerHTML=sources.map(s=>
  '<article class="agent-report-row source"><div class="agent-report-row-head"><b>'+escapeHtml(s.root)+'</b><span>'+ (s.truncated?"TRUNCATED":"DONE") +'</span></div>'+
  '<p>inspected: '+escapeHtml(s.inspected)+' · skipped_dirs: '+escapeHtml(s.skipped_dirs||0)+' · errors: '+escapeHtml(s.errors||0)+'</p></article>'
 ).join("") || '<div class="agent-report-empty">Источники отсутствуют.</div>';
};

window.addEventListener("resize",drawWires);renderNodes();selectBlock("role");renderAgentBlockOutput("ready");