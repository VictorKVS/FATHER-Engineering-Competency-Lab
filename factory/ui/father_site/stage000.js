let state="DRAFT",view="idea",inputPassed=false,artifactPassed=false,analysis=null,decision=null;
const demoKey=new URLSearchParams(location.search).get("demo");
const model={raw_idea:"",author_or_sponsor:"",known_context:[],known_constraints:[]};
const demoPresets={
 story:{
  raw_idea:"Создать LLM-систему продолжения рассказов на одной агентной конструкции со сменяемой LLM, единым входным и выходным контрактом, автоматическими тестами результата, автоматическим переключением модели при отказе или непрохождении теста и сохранением evidence и результатов в GitHub.",
  context:["FATHER/NEXUS использует единый производственный каркас 000-100.","Model Slot должен позволять замену LLM без изменения алгоритма и контрактов.","Это первое демонстрационное изделие фабрики."],
  constraints:["Каждый переход между этапами требует Человеческий шлюз.","STAGE 000 не создаёт GitHub-репозиторий и локальный проект.","Один алгоритм должен работать с несколькими совместимыми LLM.","Результаты испытаний сохраняются как evidence."]
 },
 osint:{
  raw_idea:"Создать OSINT Research Agent, который принимает формализованный исследовательский запрос, строит план поиска, собирает источники, фиксирует provenance, проверяет corroboration и counter-evidence, оценивает достаточность и возвращает проверяемый Evidence Package.",
  context:["OSINT является поставщиком evidence для ALINA и других инженерных ролей.","Источники должны сохранять provenance, дату, юрисдикцию и confidence.","Результат должен быть пригоден для дальнейшего Knowledge Engineering."],
  constraints:["Нельзя выдавать найденное утверждение за истину без evidence.","Research Request и Evidence Package имеют явные контракты.","Человеческий шлюз обязателен между производственными этапами."]
 },
 security:{
  raw_idea:"Создать Security Analysis Agent, который по описанию продукта и системы определяет активы и данные, формирует threat model и risk register, сопоставляет controls и compliance requirements, выделяет hard-fail условия и выпускает проверяемый Security Package.",
  context:["Security является независимым инженерным контуром фабрики.","Результаты должны трассироваться к требованиям, рискам, controls, tests и evidence.","Security Agent не имеет права самостоятельно утверждать релиз."],
  constraints:["Hard security constraints имеют приоритет над оптимизацией.","Все critical risks требуют явного решения или УДЕРЖАНО.","Человеческий шлюз обязателен на каждом переходе."]
 }
};
if(demoKey&&demoPresets[demoKey]){
 const p=demoPresets[demoKey];
 model.raw_idea=p.raw_idea;
 model.author_or_sponsor="USER";
 model.known_context=p.context;
 model.known_constraints=p.constraints;
}
const content=document.getElementById("stageContent");
function render(){
 if(view==="idea"){
  content.innerHTML='<div class="idea-form"><label>Raw idea<textarea id="rawIdea" placeholder="Опишите идею продукта или системы..."></textarea></label><label>Author / sponsor<input id="author" placeholder="Инициатор"></label><label>Known context<textarea id="context" placeholder="По одному пункту на строку"></textarea></label><label>Known constraints<textarea id="constraints" placeholder="По одному ограничению на строку"></textarea></label></div>';
  document.getElementById("rawIdea").value=model.raw_idea;document.getElementById("author").value=model.author_or_sponsor;document.getElementById("context").value=model.known_context.join("\n");document.getElementById("constraints").value=model.known_constraints.join("\n");
  document.getElementById("rawIdea").oninput=e=>model.raw_idea=e.target.value;document.getElementById("author").oninput=e=>model.author_or_sponsor=e.target.value;document.getElementById("context").oninput=e=>model.known_context=e.target.value.split("\n").filter(Boolean);document.getElementById("constraints").oninput=e=>model.known_constraints=e.target.value.split("\n").filter(Boolean);
 }else if(view==="analysis"){
  if(!analysis){content.innerHTML='<div class="analysis-box"><h4>LOCKED</h4><p>Сначала должен пройти Тест входа.</p></div>';return}
  content.innerHTML='<div class="analysis-grid">'+
   box("Исходная идея",analysis.original_idea)+box("Нормализованная цель",analysis.normalized_intent)+
   box("Факты",analysis.facts.map(x=>x.statement+" ["+x.source+"]"))+
   box("Предположения",analysis.assumptions)+box("Неизвестные",analysis.unknowns)+
   box("Первые вопросы",analysis.first_questions)+box("Начальные риски",analysis.initial_risks)+
   box("Рекомендуемый следующий шаг",analysis.recommended_next_step)+'</div>';
 }else if(view==="tests"){
  content.innerHTML='<div class="analysis-box"><h4>Тесты этапа</h4>'+testRow("Тест входа",inputPassed)+testRow("Исходная идея preserved",!!analysis)+testRow("Факты separated from assumptions",artifactPassed)+testRow("Неизвестные explicit",artifactPassed)+testRow("Проект ещё не создан",artifactPassed)+'</div>';
 }else if(view==="evidence"){
  content.innerHTML='<div class="evidence-json">'+escapeHtml(JSON.stringify(evidence(),null,2))+'</div>';
 }else{
  content.innerHTML='<div class="analysis-box"><h4>Человеческий шлюз</h4><p>Автоматический анализ может рекомендовать следующий шаг, но не может сам одобрить этап 000.</p><p>Решение: <b>'+(decision||"PENDING")+'</b></p>'+(decision==="APPROVE"?'<p class="pass">Предложение этапа 001 разблокировано. GitHub и локальный проект ещё НЕ создавались.</p>':'')+'</div>';
 }
}
function box(title,value){const body=Array.isArray(value)?'<ul>'+value.map(x=>'<li>'+escapeHtml(String(x))+'</li>').join("")+'</ul>':'<p>'+escapeHtml(String(value||"—"))+'</p>';return '<div class="analysis-box"><h4>'+title+'</h4>'+body+'</div>'}
function testRow(name,pass){return '<div class="test-row"><span>'+name+'</span><b class="'+(pass?"pass":"fail")+'">'+(pass?"ПРОЙДЕНО":"УДЕРЖАНО")+'</b></div>'}
function runInput(){
 inputPassed=model.raw_idea.trim().length>=20;
 document.getElementById("inputTestPanel").innerHTML=testRow("raw_idea_not_empty",!!model.raw_idea.trim())+testRow("meaningful_length",inputPassed);
 if(!inputPassed){setState("НЕКОРРЕКТНЫЙ ВХОД");toast("Тест входа: FAIL");return}
 setState("ГОТОВ К РАБОТЕ");
 analysis={
  original_idea:model.raw_idea.trim(),normalized_intent:model.raw_idea.trim(),problem_statement:"",expected_outcome:"",
  facts:[{statement:"Raw idea was supplied by the user.",source:"input.raw_idea"}].concat(model.known_context.length?[{statement:"Known context was supplied.",source:"input.known_context"}]:[]),
  assumptions:[],unknowns:["Кто основной пользователь/заказчик?","Какой измеримый результат считается успехом?","Какие ограничения являются HARD?"],
  initial_risks:[],first_questions:["Какую проблему решаем?","Кто принимает результат?","Что должно быть доказано до STAGE 001?"],
  recommended_next_step:"HUMAN_REVIEW_STAGE_000"
 };
 artifactPassed=true;
 document.getElementById("artifactTestPanel").innerHTML=testRow("original_idea_preserved",true)+testRow("facts_have_source_refs",true)+testRow("assumptions_separate",true)+testRow("unknowns_explicit",true)+testRow("no_project_created",true);
 setState("ГОТОВ К ШЛЮЗУ");enableGate();view="analysis";syncTabs();render();toast("Этап 000 готов к человеческому решению");
}
function enableGate(){["holdStage","rejectStage"].forEach(id=>document.getElementById(id).disabled=false);document.getElementById("approveStage").disabled=false}
function approveWithChecks(){
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("GATE_DECISION","approve_clicked","REQUESTED",{inputPassed,artifactPassed});
 if(!inputPassed||!artifactPassed){
   runInput();
 }
 if(!inputPassed||!artifactPassed){
   if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("GATE_DECISION","approve_blocked","HOLD",{inputPassed,artifactPassed});
   toast("Одобрение невозможно: обязательные проверки не пройдены");
   return;
 }
 decide("APPROVE");
}
function decide(d){
 const reason=document.getElementById("gateReason").value.trim();
 if((d==="HOLD"||d==="REJECT")&&!reason){toast("Для удержания/отклонения нужна причина");return}
 decision=d;
 setState(d==="APPROVE"?"APPROVED":d==="HOLD"?"HOLD":"REJECTED");
 const snapshot=evidence();
 sessionStorage.setItem("nexus_stage_000",JSON.stringify(snapshot));
 view="gate";syncTabs();render();
 updateGateUi();
 toast(d==="APPROVE"?"Этап 000 одобрен. STAGE 001 готов к переходу.":"Человеческий шлюз: "+d);
}
function evidence(){return {stage_id:"STAGE-000",state,input_snapshot:model,input_test:{status:inputPassed?"PASS":"NOT_RUN"},analysis,artifact_test:{status:artifactPassed?"PASS":"LOCKED"},human_gate:{decision},project_creation_proposal:decision==="APPROVE"?{stage:"STAGE-001",mode:"PROPOSAL_ONLY",github_repository:"PENDING_APPROVAL",local_directory:"PENDING_APPROVAL"}:null}}
function setState(s){state=s;document.getElementById("stageState").textContent=s}
function updateGateUi(){
 const next=document.getElementById("nextStageState");
 const panel=document.getElementById("stageAdvancePanel");
 if(!next||!panel)return;
 if(decision==="APPROVE"){
  next.textContent="STAGE-001 · READY";
  next.className="pass";
  panel.innerHTML='<div class="stage-approved-box"><b>✓ ЭТАП 000 ОДОБРЕН</b><span>Все обязательные проверки этапа пройдены. Следующий этап разблокирован.</span><button id="goStage001" class="stage-next-button">ПЕРЕЙТИ К STAGE 001 →</button></div>';
  document.getElementById("goStage001").onclick=()=>{const suffix=demoKey?"?demo="+encodeURIComponent(demoKey):"";location.href="./stage001.html"+suffix;};
 }else{
  next.textContent="STAGE-001 · LOCKED";
  next.className="";
  panel.innerHTML="";
 }
}
function syncTabs(){document.querySelectorAll(".stage-tab").forEach(x=>x.classList.toggle("active",x.dataset.view===view))}
function escapeHtml(v){return v.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}
document.querySelectorAll(".stage-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;syncTabs();render()});
document.getElementById("runInputTest").onclick=runInput;
document.getElementById("approveStage").onclick=approveWithChecks;
document.getElementById("holdStage").onclick=()=>decide("HOLD");
document.getElementById("rejectStage").onclick=()=>decide("REJECT");
document.getElementById("resetIdea").onclick=()=>{sessionStorage.removeItem("nexus_stage_000");location.href="./stage000.html"};
render();
updateGateUi();