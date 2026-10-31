const layers={
 common_foundation:{label:"Общая основа",nodes:[
  {id:"KF-001",type:"LANGUAGE_PATTERN",title:"Профессиональный русский язык",desc:"Терминология, ясность формулировок, структура профессиональных документов.",source:"CURATED",authority:"HIGH",skills:["clear_writing","terminology_control"]},
  {id:"KF-002",type:"PROCEDURE",title:"Критическое мышление",desc:"Отделение фактов, гипотез и выводов; проверка оснований.",source:"CURATED",authority:"HIGH",skills:["claim_validation","contradiction_detection"]},
  {id:"KF-003",type:"RULE",title:"Гигиена источников",desc:"Первичные источники, версии, даты, provenance и доверие.",source:"ENGINEERING_CANON",authority:"HIGH",skills:["source_assessment"]},
  {id:"KF-004",type:"PROCEDURE",title:"Работа с документами",desc:"Извлечение требований, ссылок, версий и взаимосвязей.",source:"CURATED",authority:"MEDIUM",skills:["document_analysis"]},
  {id:"KF-005",type:"RISK",title:"Базовая информационная безопасность",desc:"Минимальные правила безопасной обработки данных и инструментов.",source:"SECURITY_BASELINE",authority:"HIGH",skills:["safe_operation"]},
  {id:"KF-006",type:"RULE",title:"Корпоративная этика и границы",desc:"Эскалация, допустимые действия, разделение ответственности.",source:"CORPORATE_POLICY",authority:"HIGH",skills:["escalation","decision_boundaries"]}
 ]},
 corporate_common:{label:"Корпоративная база",nodes:[
  {id:"KC-001",type:"CONCEPT",title:"Оргструктура",desc:"Роли, подразделения, зоны ответственности.",source:"CORPORATE_DOCS",authority:"HIGH",skills:["organization_navigation"]},
  {id:"KC-002",type:"PROCEDURE",title:"Внутренние процессы",desc:"Согласование, handoff, change management, release.",source:"CORPORATE_DOCS",authority:"HIGH",skills:["process_execution"]},
  {id:"KC-003",type:"RULE",title:"Security Policy",desc:"Политики доступа, данные, классификация, ограничения.",source:"CORPORATE_POLICY",authority:"HIGH",skills:["policy_compliance"]}
 ]},
 profession_core:{label:"Ядро профессии",nodes:[
  {id:"KP-001",type:"CONCEPT",title:"Профессиональная терминология",desc:"Основной понятийный аппарат профессии.",source:"PROFESSIONAL_STANDARDS",authority:"HIGH",skills:["domain_language"]},
  {id:"KP-002",type:"PROCEDURE",title:"Типовые рабочие процессы",desc:"Повторяемые профессиональные операции и решения.",source:"STANDARDS+PRACTICE",authority:"HIGH",skills:["workflow_execution"]},
  {id:"KP-003",type:"DECISION_PATTERN",title:"Типовые решения",desc:"Условия, варианты, риски и критерии выбора.",source:"CASES",authority:"MEDIUM",skills:["professional_decision"]}
 ]},
 specialist_domain:{label:"Специализированная область",nodes:[
  {id:"KS-001",type:"RULE",title:"Специализированные правила",desc:"Правила конкретного домена, продукта или юрисдикции.",source:"DOMAIN_PACKAGE",authority:"HIGH",skills:["domain_application"]},
  {id:"KS-002",type:"CASE",title:"Сложные кейсы",desc:"Редкие и неоднозначные рабочие ситуации.",source:"CURATED_CASES",authority:"MEDIUM",skills:["edge_case_resolution"]}
 ]},
 research_acquired:{label:"Получено через OSINT",nodes:[
  {id:"KO-001",type:"FACT",title:"OSINT Evidence RR-018",desc:"Подтверждённый материал по закрытому knowledge gap.",source:"OSINT_EVIDENCE_PACKAGE",authority:"VARIABLE",skills:["evidence_use"]},
  {id:"KO-002",type:"CASE",title:"OSINT Case RR-024",desc:"Найденный практический кейс для обучения специалиста.",source:"OSINT_EVIDENCE_PACKAGE",authority:"VARIABLE",skills:["case_reasoning"]}
 ]},
 operational_dynamic:{label:"Динамические / RAG",nodes:[
  {id:"KD-001",type:"FACT",title:"Актуальные внешние данные",desc:"Изменяемая информация, которую не следует фиксировать как вечный KB-факт.",source:"RAG_OR_TOOL",authority:"DYNAMIC",skills:["runtime_information_use"]},
  {id:"KD-002",type:"TOOL",title:"Operational Lookup",desc:"Данные, которые правильнее получать инструментом во время выполнения.",source:"TOOL",authority:"DYNAMIC",skills:["tool_use"]}
 ]}
};
let activeLayer="common_foundation",view="catalog",selected=null;
const stage=document.getElementById("knowledgeStage");

function render(){
 const layer=layers[activeLayer];
 document.getElementById("activeLayerLabel").textContent=layer.label;
 document.getElementById("nodeCount").textContent=layer.nodes.length;
 if(view==="catalog"){
  stage.innerHTML='<div class="catalog-grid">'+layer.nodes.map(n=>'<article class="knowledge-node '+(selected?.id===n.id?'selected':'')+'" data-node="'+n.id+'"><div class="type">'+n.type+'</div><h4>'+n.title+'</h4><p>'+n.desc+'</p><footer><span>'+n.source+'</span><span>'+n.authority+'</span></footer></article>').join("")+'</div>';
  document.querySelectorAll(".knowledge-node").forEach(el=>el.onclick=()=>selectNode(el.dataset.node));
 }else if(view==="graph"){
  stage.innerHTML='<div class="graph-board">'+layer.nodes.map((n,i)=>'<div class="graph-bubble" style="left:'+(40+(i%3)*220)+'px;top:'+(55+Math.floor(i/3)*180)+'px">'+n.id+' · '+n.title+'</div>').join("")+'</div>';
 }else if(view==="skills"){
  stage.innerHTML='<div class="skill-chain">'+[
   ["1 · Узел знания","Проверяемый узел знания с источником и контекстом."],
   ["2 · Пример","Показывает применение знания."],
   ["3 · Процедура","Формализует способ действия."],
   ["4 · Практический кейс","Заставляет применить знание в ситуации."],
   ["5 · Решение","Агент делает выбор и объясняет основание."],
   ["6 · Обратная связь","Ошибка классифицируется и исправляется."],
   ["7 · Оценка","Навык измеряется на фиксированном наборе."],
   ["8 · Закрепление","Слабые места возвращаются в обучение."],
   ["9 · Доказательство компетенции","Навык считается подтверждённым только после PASS."]
  ].map(x=>'<div class="skill-step"><b>'+x[0]+'</b><p>'+x[1]+'</p></div>').join("")+'</div>';
 }else{
  stage.innerHTML='<div class="ab-grid">'+[
   ["A/B онтологии","Сравниваем две структуры знаний на одном наборе задач."],
   ["A/B слоёв","Проверяем, где знание эффективнее: common/profession/specialist."],
   ["A/B поиска","Chunking, embedding, top-k, reranking, context assembly."],
   ["Веса источников","Сравниваем веса первичных, корпоративных и OSINT-источников."],
   ["Метрики качества","Источник coverage · provenance · contradiction · stale · orphan · competency coverage."],
   ["Критический отказ","Нет источника у критичного знания; противоречие не разрешено; устаревшее правило используется как актуальное."]
  ].map(x=>'<div class="ab-card"><h4>'+x[0]+'</h4><p>'+x[1]+'</p></div>').join("")+'</div>';
 }
}

function selectNode(id){
 const n=layers[activeLayer].nodes.find(x=>x.id===id);selected=n;render();
 document.getElementById("nodeInspector").innerHTML=
  '<div class="node-field"><b>ID</b><code>'+n.id+'</code></div>'+
  '<div class="node-field"><b>Тип</b><code>'+n.type+'</code></div>'+
  '<div class="node-field"><b>Источник</b><code>'+n.source+'</code></div>'+
  '<div class="node-field"><b>Авторитетность</b><code>'+n.authority+'</code></div>'+
  '<div class="node-field"><b>Навыки</b><code>'+n.skills.join("\n")+'</code></div>';
 document.getElementById("skillBinding").innerHTML='<p><b>'+n.title+'</b></p><p>Knowledge → Пример → Процедура → Practice → Решение → Обратная связь → Оценка → Доказательство компетенции</p><button class="primary" onclick="toast(\'Предложение карты навыка создано\')">Сформировать карту навыка</button>';
}

document.querySelectorAll(".layer-btn").forEach(b=>b.onclick=()=>{activeLayer=b.dataset.layer;selected=null;document.querySelectorAll(".layer-btn").forEach(x=>x.classList.toggle("active",x===b));render();document.getElementById("nodeInspector").innerHTML='<p>Выберите узел знания.</p>';document.getElementById("skillBinding").innerHTML='<p>Выберите узел знания.</p>'});
document.querySelectorAll(".studio-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;document.querySelectorAll(".studio-tab").forEach(x=>x.classList.toggle("active",x===b));render()});
document.getElementById("analyzeKnowledge").onclick=()=>{document.getElementById("knowledgeGate").textContent="ПРОАНАЛИЗИРОВАНО";toast("Проверены слои, provenance, gaps, skills и quality metrics")};
document.getElementById("buildGraph").onclick=()=>{view="graph";document.querySelectorAll(".studio-tab").forEach(x=>x.classList.toggle("active",x.dataset.view==="graph"));render();toast("Граф знаний перестроен в черновик")};
document.getElementById("saveKbProposal").onclick=()=>{document.getElementById("knowledgeGate").textContent="ПРЕДЛОЖЕНИЕ";toast("Knowledge Architecture сохранена как ПРЕДЛОЖЕНИЕ")};
document.querySelectorAll("[data-source]").forEach(b=>b.onclick=()=>toast("Источник добавлен в ingestion plan: "+b.textContent));
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.remove("show"),2200)}
render();
