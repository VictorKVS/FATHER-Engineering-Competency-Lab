const blocks=[
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
const edges=[["input","role"],["role","rag"],["role","prompt"],["prompt","model"],["rag","model"],["kb","model"],["model","output"],["output","eval"],["eval","evidence"]];
const palette=[
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
  n.innerHTML='<div class="nhead"><span class="nid">'+b.type+'</span><span class="state"></span></div><h3>'+b.title+'</h3><p>'+b.desc+'</p>';
  n.onclick=()=>selectBlock(b.id);n.ondblclick=e=>{e.stopPropagation();openBlockModal(b.id)};nodes.appendChild(n);
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

window.addEventListener("resize",drawWires);renderNodes();selectBlock("role");