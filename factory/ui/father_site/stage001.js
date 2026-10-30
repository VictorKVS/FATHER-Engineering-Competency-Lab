let view="proposal",validated=false,decision=null,executionApproved=false,verificationPassed=false;
const previous=JSON.parse(sessionStorage.getItem("nexus_stage_000")||"null");
const prereqApproved=previous&&previous.human_gate&&previous.human_gate.decision==="APPROVE";
const proposal={
 project_id:"PRJ-STORY-001",
 public_name:"NEXUS Story Engine",
 code_name:"STORY_ENGINE",
 local_directory:"G:\\1\\NEXUS-STORY-ENGINE",
 github_owner:"VictorKVS",
 github_repository:"NEXUS-STORY-ENGINE",
 visibility:"private",
 default_branch:"main",
 license:"UNDECIDED"
};
const executionPlan={
 github_mode:"CREATE_NEW",
 local_mode:"CREATE_NEW",
 git_mode:"INIT_AND_BIND",
 scaffold_mode:"GENERATE_000_100",
 initial_commit:true
};
const verification={
 github_repository_exists:false,
 local_directory_exists:false,
 git_repository_initialized:false,
 git_remote_matches:false,
 stage_files_101:false,
 project_yaml_exists:false,
 initial_commit_exists:false,
 evidence_written:false
};
const content=document.getElementById("stageContent");
document.getElementById("stage000State").textContent="STAGE-000 · "+(prereqApproved?"APPROVED":"NOT APPROVED");
document.getElementById("stageState").textContent=prereqApproved?"ГОТОВ":"ЗАКРЫТО";
if(!prereqApproved) document.getElementById("stageState").classList.add("fail");

function render(){
 if(view==="proposal"){
  content.innerHTML='<div class="proposal-form">'+
   field("ID проекта","project_id")+field("Публичное имя","public_name")+field("Кодовое имя","code_name")+
   field("Локальная папка","local_directory","span2")+field("Владелец GitHub","github_owner")+field("Репозиторий GitHub","github_repository")+
   field("Видимость","visibility")+field("Ветка по умолчанию","default_branch")+field("Лицензия","license")+
   '</div><div class="notice" style="margin-top:12px">На этой статической странице APPROVE формирует только разрешённый execution plan. Реальное создание каталога и GitHub-репозитория должен выполнить backend/runtime фабрики.</div>';
  Object.keys(proposal).forEach(k=>{const e=document.getElementById(k);if(e){e.value=proposal[k];e.oninput=ev=>{proposal[k]=ev.target.value;validated=false;disableGate()}}});
 }else if(view==="scaffold"){
  content.innerHTML='<div class="scaffold-grid">'+Array.from({length:101},(_,i)=>{const n=String(i).padStart(3,"0");return '<div class="stage-chip"><b>'+n+'</b>'+(i===0?"IDEA_INTAKE":i===1?"PROJECT_INITIALIZATION":i===100?"PRODUCTION_PROVEN":"ЗАКРЫТО")+'</div>'}).join("")+'</div>';
 }else if(view==="execution"){
  const authBanner=executionApproved
   ? '<div class="execution-approved-banner"><div><b>✓ ВЫПОЛНЕНИЕ РАЗРЕШЕНО</b><span>Human Gate = APPROVE. Теперь разрешено создать GitHub, локальную папку, Git-связку и каркас 000–100.</span></div><div class="execution-approved-actions"><button id="downloadExecutionPlan" class="primary">Скачать план выполнения</button><button id="openVerification" class="ghost">Перейти к проверке</button></div></div>'
   : '<div class="execution-locked-banner"><b>ВЫПОЛНЕНИЕ ЕЩЁ НЕ РАЗРЕШЕНО</b><span>Сначала проверьте предложение и нажмите APPROVE.</span></div>';
  content.innerHTML=authBanner+
   '<div class="execution-layout">'+
    '<div class="stage-card"><div class="card-head">Выполнение GitHub</div>'+
      optionRow("github_mode","CREATE_NEW","Создать новый Репозиторий GitHub","Фабрика создаёт новый репозиторий после APPROVE.")+
      optionRow("github_mode","BIND_EXISTING","Привязать существующий репозиторий","Использовать уже существующий Репозиторий GitHub.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Локальное выполнение</div>'+
      optionRow("local_mode","CREATE_NEW","Создать новую папку","Создать "+proposal.local_directory)+
      optionRow("local_mode","USE_EXISTING","Использовать существующую папку","Проверить и принять существующий каталог.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Связка Git</div>'+
      optionRow("git_mode","INIT_AND_BIND","git init + remote origin","Инициализировать локальный Git и связать с GitHub.")+
      optionRow("git_mode","CLONE","git clone","Клонировать существующий repository в local directory.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Каркас проекта</div>'+
      optionRow("scaffold_mode","GENERATE_000_100","Создать stages/000…100","Сгенерировать 101 стандартный stage-файл.")+
      '<div class="execution-summary"><b>После одобрения</b><span>GitHub + Local + Связка Git + 000–100 + initial commit + evidence</span></div>'+
    '</div>'+
   '</div>';
  bindExecutionOptions();
  if(executionApproved){
    const dl=document.getElementById("downloadExecutionPlan");
    if(dl)dl.onclick=downloadExecutionPlan;
    const ov=document.getElementById("openVerification");
    if(ov)ov.onclick=()=>{view="tests";sync();render();};
  }
 }else if(view==="tests"){
  content.innerHTML='<div class="stage-card"><div class="card-head">Тесты этапа 001</div>'+testRow("Этап 000 одобрен",prereqApproved)+testRow("ID проекта present",!!proposal.project_id)+testRow("Имя проекта указано",!!proposal.public_name)+testRow("Локальный путь указан",!!proposal.local_directory)+testRow("Имя репозитория указано",!!proposal.github_repository)+testRow("Каркас 000–100 запланирован",true)+'</div>'+
  '<div class="stage-card" style="margin-top:10px"><div class="card-head">Проверка выполнения</div>'+verificationRows()+'</div>';
 }else if(view==="evidence"){
  content.innerHTML='<div class="evidence-json">'+esc(JSON.stringify(evidence(),null,2))+'</div>';
 }else{
  content.innerHTML='<div class="stage-card"><div class="card-head">Человеческий шлюз</div><p style="font-size:9px;color:#748a9b">Decision: <b>'+(decision||"PENDING")+'</b></p>'+(decision==="APPROVE"?'<p class="pass" style="font-size:9px">План выполнения одобрен. Создание разрешено.</p>':'')+'</div>'+
  '<div class="stage-card" style="margin-top:10px"><div class="card-head">Шлюз проверки</div><p style="font-size:9px;color:#748a9b">Результат: <b class="'+(verificationPassed?"pass":"fail")+'">'+(verificationPassed?"ПРОЙДЕНО":"НЕ ПРОЙДЕНО")+'</b></p><p style="font-size:9px;color:#748a9b">Этап 001 считается пройденным только после фактической проверки GitHub, локальной папки, привязки Git, каркаса и доказательств.</p></div>';
 }
}
function field(label,key,cl=""){return '<label class="'+cl+'">'+label+'<input id="'+key+'"></label>'}
function optionRow(group,value,title,desc){
 const checked=executionPlan[group]===value?"checked":"";
 return '<label class="exec-option"><input type="radio" name="'+group+'" value="'+value+'" '+checked+'><span><b>'+title+'</b><small>'+desc+'</small></span></label>';
}
function bindExecutionOptions(){
 document.querySelectorAll(".exec-option input").forEach(input=>input.onchange=()=>{executionPlan[input.name]=input.value;});
}
function verificationRows(){
 return Object.entries(verification).map(([k,v])=>testRow(k,v)).join("");
}
function testRow(n,p){return '<div class="test-row"><span>'+n+'</span><b class="'+(p?"pass":"fail")+'">'+(p?"ПРОЙДЕНО":"УДЕРЖАНО")+'</b></div>'}
function validate(){
 if(!prereqApproved){toast("STAGE 000 не APPROVED");return}
 const ok=proposal.project_id&&proposal.public_name&&proposal.code_name&&proposal.local_directory&&proposal.github_owner&&proposal.github_repository&&proposal.default_branch;
 validated=!!ok;
 document.getElementById("inputTestPanel").innerHTML=testRow("stage_000_approved",prereqApproved)+testRow("identity_complete",validated);
 document.getElementById("artifactTestPanel").innerHTML=testRow("scaffold_000_100_planned",true)+testRow("creation_not_executed",true);
 if(validated){document.getElementById("stageState").textContent="ГОТОВ К ШЛЮЗУ";enableGate();toast("Предложение этапа 001 прошло проверку")}
 else toast("Предложение заполнено не полностью");
}
function downloadExecutionPlan(){
 const payload={
  stage_id:"STAGE-001",
  action:"PROJECT_INITIALIZATION",
  approved:true,
  proposal,
  execution_plan:executionPlan,
  expected_results:{
   github_repository:proposal.github_owner+"/"+proposal.github_repository,
   local_directory:proposal.local_directory,
   stage_files:101,
   required_paths:["project.yaml","stages/000.yaml","stages/100.yaml","artifacts/","agents/","algorithms/","knowledge/","tests/","evidence/"]
  }
 };
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
 const a=document.createElement("a");
 a.href=URL.createObjectURL(blob);
 a.download="stage-001-execution-plan.json";
 a.click();
 URL.revokeObjectURL(a.href);
 toast("План выполнения сохранён");
}
function refreshVerificationPanels(){
 document.getElementById("executionVerifyPanel").innerHTML=verificationRows();
 document.getElementById("verificationState").textContent=verificationPassed?"ПРОЙДЕНО":"НЕ ПРОЙДЕНО";
 document.getElementById("verificationState").className=verificationPassed?"pass":"fail";
}
function markExecutionVerifiedDemo(){
 if(!executionApproved){toast("Сначала одобрите план выполнения");return}
 Object.keys(verification).forEach(k=>verification[k]=true);
 verificationPassed=true;
 document.getElementById("stageState").textContent="ПРОЙДЕНО";
 refreshVerificationPanels();
 const ev=evidence();sessionStorage.setItem("nexus_stage_001",JSON.stringify(ev));
 toast("Этап 001 ПРОЙДЕН: выполнение подтверждено");
 view="gate";sync();render();
}
function enableGate(){["approveGate","holdGate","rejectGate","approveProject"].forEach(id=>document.getElementById(id).disabled=false)}
function disableGate(){["approveGate","holdGate","rejectGate","approveProject"].forEach(id=>document.getElementById(id).disabled=true)}
function decide(d){
 const reason=document.getElementById("gateReason").value.trim();
 if(!validated){toast("Сначала проверьте proposal");return}
 if((d==="УДЕРЖАНО"||d==="REJECT")&&!reason){toast("Для УДЕРЖАНО/REJECT нужна причина");return}
 decision=d;
 executionApproved=d==="APPROVE";
 document.getElementById("stageState").textContent=d==="APPROVE"?"ВЫПОЛНЕНИЕ ОДОБРЕНО":d==="УДЕРЖАНО"?"УДЕРЖАНО":"ОТКЛОНЕНО";
 const ev=evidence();sessionStorage.setItem("nexus_stage_001",JSON.stringify(ev));
 view=d==="APPROVE"?"execution":"gate";
 sync();render();
 toast(d==="APPROVE"?"Выполнение разрешено — открыт план выполнения":"Человеческий шлюз: "+d);
}
function evidence(){return {stage_id:"STAGE-001",state:document.getElementById("stageState").textContent,prerequisite:{stage:"STAGE-000",approved:prereqApproved},proposal,input_test:{status:validated?"ПРОЙДЕНО":"NOT_RUN"},artifact_test:{status:validated?"ПРОЙДЕНО":"ЗАКРЫТО",planned_stage_files:101},human_gate:{decision},execution:{approved:executionApproved,plan:executionPlan,verification,verification_passed:verificationPassed,requires_runtime:true}}}
function sync(){document.querySelectorAll(".stage-tab").forEach(x=>x.classList.toggle("active",x.dataset.view===view))}
function esc(v){return v.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}
document.querySelectorAll(".stage-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;sync();render()});
document.getElementById("validateProposal").onclick=validate;
document.getElementById("approveGate").onclick=()=>decide("APPROVE");
document.getElementById("holdGate").onclick=()=>decide("УДЕРЖАНО");
document.getElementById("rejectGate").onclick=()=>decide("REJECT");
document.getElementById("approveProject").onclick=()=>decide("APPROVE");
render();