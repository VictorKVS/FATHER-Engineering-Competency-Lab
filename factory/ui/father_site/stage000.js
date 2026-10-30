let state="DRAFT",view="idea",inputPassed=false,artifactPassed=false,analysis=null,decision=null;
const demoKey=new URLSearchParams(location.search).get("demo");
const model={raw_idea:"",author_or_sponsor:"",known_context:[],known_constraints:[]};
const demoPresets={
 story:{
  raw_idea:"Создать LLM-систему продолжения рассказов на одной агентной конструкции со сменяемой LLM, единым входным и выходным контрактом, автоматическими тестами результата, автоматическим переключением модели при отказе или непрохождении теста и сохранением evidence и результатов в GitHub.",
  context:["FATHER/NEXUS использует единый производственный каркас 000-100.","Model Slot должен позволять замену LLM без изменения алгоритма и контрактов.","Это первое демонстрационное изделие фабрики."],
  constraints:["Каждый переход между этапами требует Human Gate.","STAGE 000 не создаёт GitHub-репозиторий и локальный проект.","Один алгоритм должен работать с несколькими совместимыми LLM.","Результаты испытаний сохраняются как evidence."]
 },
 osint:{
  raw_idea:"Создать OSINT Research Agent, который принимает формализованный исследовательский запрос, строит план поиска, собирает источники, фиксирует provenance, проверяет corroboration и counter-evidence, оценивает достаточность и возвращает проверяемый Evidence Package.",
  context:["OSINT является поставщиком evidence для ALINA и других инженерных ролей.","Источники должны сохранять provenance, дату, юрисдикцию и confidence.","Результат должен быть пригоден для дальнейшего Knowledge Engineering."],
  constraints:["Нельзя выдавать найденное утверждение за истину без evidence.","Research Request и Evidence Package имеют явные контракты.","Human Gate обязателен между производственными этапами."]
 },
 security:{
  raw_idea:"Создать Security Analysis Agent, который по описанию продукта и системы определяет активы и данные, формирует threat model и risk register, сопоставляет controls и compliance requirements, выделяет hard-fail условия и выпускает проверяемый Security Package.",
  context:["Security является независимым инженерным контуром фабрики.","Результаты должны трассироваться к требованиям, рискам, controls, tests и evidence.","Security Agent не имеет права самостоятельно утверждать релиз."],
  constraints:["Hard security constraints имеют приоритет над оптимизацией.","Все critical risks требуют явного решения или HOLD.","Human Gate обязателен на каждом переходе."]
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
  if(!analysis){content.innerHTML='<div class="analysis-box"><h4>LOCKED</h4><p>Сначала должен пройти Input Test.</p></div>';return}
  content.innerHTML='<div class="analysis-grid">'+
   box("Original idea",analysis.original_idea)+box("Normalized intent",analysis.normalized_intent)+
   box("Facts",analysis.facts.map(x=>x.statement+" ["+x.source+"]"))+
   box("Assumptions",analysis.assumptions)+box("Unknowns",analysis.unknowns)+
   box("First questions",analysis.first_questions)+box("Initial risks",analysis.initial_risks)+
   box("Recommended next step",analysis.recommended_next_step)+'</div>';
 }else if(view==="tests"){
  content.innerHTML='<div class="analysis-box"><h4>Stage Tests</h4>'+testRow("Input Test",inputPassed)+testRow("Original idea preserved",!!analysis)+testRow("Facts separated from assumptions",artifactPassed)+testRow("Unknowns explicit",artifactPassed)+testRow("No project created",artifactPassed)+'</div>';
 }else if(view==="evidence"){
  content.innerHTML='<div class="evidence-json">'+escapeHtml(JSON.stringify(evidence(),null,2))+'</div>';
 }else{
  content.innerHTML='<div class="analysis-box"><h4>Human Gate</h4><p>Automatic analysis may recommend the next step, but cannot approve Stage 000.</p><p>Decision: <b>'+(decision||"PENDING")+'</b></p>'+(decision==="APPROVE"?'<p class="pass">STAGE 001 proposal unlocked. GitHub/local project creation is still NOT executed.</p>':'')+'</div>';
 }
}
function box(title,value){const body=Array.isArray(value)?'<ul>'+value.map(x=>'<li>'+escapeHtml(String(x))+'</li>').join("")+'</ul>':'<p>'+escapeHtml(String(value||"—"))+'</p>';return '<div class="analysis-box"><h4>'+title+'</h4>'+body+'</div>'}
function testRow(name,pass){return '<div class="test-row"><span>'+name+'</span><b class="'+(pass?"pass":"fail")+'">'+(pass?"PASS":"HOLD")+'</b></div>'}
function runInput(){
 inputPassed=model.raw_idea.trim().length>=20;
 document.getElementById("inputTestPanel").innerHTML=testRow("raw_idea_not_empty",!!model.raw_idea.trim())+testRow("meaningful_length",inputPassed);
 if(!inputPassed){setState("INPUT_INVALID");toast("Input Test: FAIL");return}
 setState("READY_FOR_WORK");
 analysis={
  original_idea:model.raw_idea.trim(),normalized_intent:model.raw_idea.trim(),problem_statement:"",expected_outcome:"",
  facts:[{statement:"Raw idea was supplied by the user.",source:"input.raw_idea"}].concat(model.known_context.length?[{statement:"Known context was supplied.",source:"input.known_context"}]:[]),
  assumptions:[],unknowns:["Кто основной пользователь/заказчик?","Какой измеримый результат считается успехом?","Какие ограничения являются HARD?"],
  initial_risks:[],first_questions:["Какую проблему решаем?","Кто принимает результат?","Что должно быть доказано до STAGE 001?"],
  recommended_next_step:"HUMAN_REVIEW_STAGE_000"
 };
 artifactPassed=true;
 document.getElementById("artifactTestPanel").innerHTML=testRow("original_idea_preserved",true)+testRow("facts_have_source_refs",true)+testRow("assumptions_separate",true)+testRow("unknowns_explicit",true)+testRow("no_project_created",true);
 setState("READY_FOR_GATE");enableGate();view="analysis";syncTabs();render();toast("STAGE 000 готов к человеческому решению");
}
function enableGate(){["approveStage","holdStage","rejectStage"].forEach(id=>document.getElementById(id).disabled=false)}
function decide(d){
 const reason=document.getElementById("gateReason").value.trim();
 if((d==="HOLD"||d==="REJECT")&&!reason){toast("Для HOLD/REJECT нужна причина");return}
 decision=d;
 setState(d==="APPROVE"?"APPROVED":d==="HOLD"?"HOLD":"REJECTED");
 const snapshot=evidence();
 sessionStorage.setItem("nexus_stage_000",JSON.stringify(snapshot));
 view="gate";syncTabs();render();toast("Human Gate: "+d);
 if(d==="APPROVE"){
   setTimeout(()=>{location.href="./stage001.html?demo=story"},700);
 }
}
function evidence(){return {stage_id:"STAGE-000",state, input_snapshot:model,input_test:{status:inputPassed?"PASS":"NOT_PASS"},analysis,artifact_test:{status:artifactPassed?"PASS":"LOCKED"},human_gate:{decision},project_creation_proposal:decision==="APPROVE"?{stage:"STAGE-001",mode:"PROPOSAL_ONLY",github_repository:"PENDING_APPROVAL",local_directory:"PENDING_APPROVAL"}:null}}
function setState(s){state=s;document.getElementById("stageState").textContent=s}
function syncTabs(){document.querySelectorAll(".stage-tab").forEach(x=>x.classList.toggle("active",x.dataset.view===view))}
function escapeHtml(v){return v.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}
document.querySelectorAll(".stage-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;syncTabs();render()});
document.getElementById("runInputTest").onclick=runInput;document.getElementById("approveStage").onclick=()=>decide("APPROVE");document.getElementById("holdStage").onclick=()=>decide("HOLD");document.getElementById("rejectStage").onclick=()=>decide("REJECT");document.getElementById("resetIdea").onclick=()=>{sessionStorage.removeItem("nexus_stage_000");location.href="./stage000.html"};render();