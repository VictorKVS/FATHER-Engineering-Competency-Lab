let view="proposal",validated=false,decision=null,executionApproved=false,verificationPassed=false;
let preflightResult=null,runtimeOnline=false,operationState="IDLE";
const RUNTIME="http://127.0.0.1:8091";

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
function traceState(action,status,details={}){
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("STATE_CHANGE",action,status,details);
}
function tracedProposal(){
 return {...proposal,session_id:(window.NEXUS_TRACE&&window.NEXUS_TRACE.sessionId)||"ui"};
}
document.getElementById("stage000State").textContent="STAGE-000 · "+(prereqApproved?"APPROVED":"NOT APPROVED");
document.getElementById("stageState").textContent=prereqApproved?"ГОТОВ":"ЗАКРЫТО";
if(!prereqApproved)document.getElementById("stageState").classList.add("fail");

async function api(path,payload){
 const r=await fetch(RUNTIME+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const data=await r.json();
 if(!r.ok)throw new Error(data.message||data.error||("HTTP "+r.status));
 return data;
}
async function checkRuntime(){
 try{
  const r=await fetch(RUNTIME+"/health");
  runtimeOnline=r.ok;
 }catch{runtimeOnline=false}
 render();
}

function field(label,key,cl=""){return '<label class="'+cl+'">'+label+'<input id="'+key+'"></label>'}
function optionRow(group,value,title,desc){
 const checked=executionPlan[group]===value?"checked":"";
 return '<label class="exec-option"><input type="radio" name="'+group+'" value="'+value+'" '+checked+'><span><b>'+title+'</b><small>'+desc+'</small></span></label>';
}
function testRow(n,p){return '<div class="test-row"><span>'+n+'</span><b class="'+(p?"pass":"fail")+'">'+(p?"ПРОЙДЕНО":"УДЕРЖАНО")+'</b></div>'}
function esc(v){return String(v).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2600)}
function sync(){document.querySelectorAll(".stage-tab").forEach(x=>x.classList.toggle("active",x.dataset.view===view))}
function verificationRows(){return Object.entries(verification).map(([k,v])=>testRow(k,v)).join("")}
function bindProposal(){
 Object.keys(proposal).forEach(k=>{
  const e=document.getElementById(k);
  if(e){e.value=proposal[k];e.oninput=ev=>{proposal[k]=ev.target.value;validated=false;preflightResult=null;disableGate()}}
 });
}
function bindExecutionOptions(){
 document.querySelectorAll(".exec-option input").forEach(input=>input.onchange=()=>{
  executionPlan[input.name]=input.value;
  preflightResult=null;
  render();
 });
}

function preflightHtml(){
 if(!preflightResult)return '<div class="runtime-preflight-empty">Preflight ещё не запускался.</div>';
 const p=preflightResult;
 const rows=[
  ["GitHub repository",p.github_exists,p.github_repository],
  ["Локальная папка",p.local_exists,p.local_directory],
  ["Локальный Git",p.local_is_git,p.local_origin||"—"],
  ["Origin совпадает",p.local_origin_matches,p.local_origin||"—"],
  ["Файлы этапов",p.scaffold_stage_files===101,String(p.scaffold_stage_files)+"/101"],
  ["project.yaml",p.project_yaml_exists,p.project_yaml_exists?"есть":"нет"]
 ];
 return '<div class="preflight-grid">'+rows.map(([n,ok,d])=>'<div class="preflight-row"><span>'+n+'</span><b class="'+(ok?"pass":"fail")+'">'+(ok?"ЕСТЬ":"НЕТ")+'</b><small>'+esc(d)+'</small></div>').join("")+'</div>'+
 (p.conflicts&&p.conflicts.length?'<div class="preflight-conflicts"><b>Обнаружены конфликты</b>'+p.conflicts.map(x=>'<span>'+esc(x)+'</span>').join("")+'</div>':'<div class="preflight-clear">✓ Конфликтов для выбранного сценария нет</div>')+
 (p.allowed_actions&&p.allowed_actions.length?'<div class="preflight-actions"><b>Допустимые варианты:</b> '+p.allowed_actions.map(esc).join(" · ")+'</div>':'');
}

function render(){
 if(view==="proposal"){
  content.innerHTML='<div class="proposal-form">'+
   field("ID проекта","project_id")+field("Публичное имя","public_name")+field("Кодовое имя","code_name")+
   field("Локальная папка","local_directory","span2")+field("Владелец GitHub","github_owner")+field("Репозиторий GitHub","github_repository")+
   field("Видимость","visibility")+field("Ветка по умолчанию","default_branch")+field("Лицензия","license")+
   '</div><div class="notice" style="margin-top:12px">После APPROVE создание выполняет локальный runtime. Перед созданием он обязательно повторяет preflight GitHub, папки и Git.</div>';
  bindProposal();
 }else if(view==="scaffold"){
  content.innerHTML='<div class="scaffold-grid">'+Array.from({length:101},(_,i)=>{const n=String(i).padStart(3,"0");return '<div class="stage-chip"><b>'+n+'</b>'+(i===0?"IDEA_INTAKE":i===1?"PROJECT_INITIALIZATION":i===100?"PRODUCTION_PROVEN":"ЗАКРЫТО")+'</div>'}).join("")+'</div>';
 }else if(view==="execution"){
  const runtime='<div class="runtime-state '+(runtimeOnline?"ok":"bad")+'"><b>Локальный runtime</b><span>'+(runtimeOnline?"ONLINE · 127.0.0.1:8091":"OFFLINE · запустите father-factory site-runtime")+'</span></div>'+
  '<div class="runtime-operation"><b>Операция</b><span>'+operationState+'</span></div>';
  const auth=executionApproved
   ? '<div class="execution-approved-banner"><div><b>✓ ВЫПОЛНЕНИЕ РАЗРЕШЕНО</b><span>Перед созданием система повторно проверит GitHub, локальную папку и Git origin.</span></div></div>'
   : '<div class="execution-locked-banner"><b>ВЫПОЛНЕНИЕ ЕЩЁ НЕ РАЗРЕШЕНО</b><span>Сначала проверьте предложение и нажмите APPROVE.</span></div>';
  content.innerHTML=runtime+auth+
   '<div class="execution-controls">'+
    '<button id="runPreflight" class="ghost">1 · Перепроверить наличие</button>'+
    '<button id="executeProject" class="primary" '+(!executionApproved||!runtimeOnline?'disabled':'')+'>2 · Создать / привязать проект</button>'+
    '<button id="verifyProject" class="ghost" '+(!runtimeOnline?'disabled':'')+'>3 · Проверить результат</button>'+
   '</div>'+
   '<div class="execution-layout">'+
    '<div class="stage-card"><div class="card-head">GitHub</div>'+
      optionRow("github_mode","CREATE_NEW","Создать новый репозиторий GitHub","Разрешено только если имя свободно.")+
      optionRow("github_mode","BIND_EXISTING","Привязать существующий репозиторий","Разрешено только если репозиторий найден.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Локальная папка</div>'+
      optionRow("local_mode","CREATE_NEW","Создать новую папку","Разрешено только если путь свободен.")+
      optionRow("local_mode","USE_EXISTING","Использовать существующую папку","Только после проверки её содержимого.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Git</div>'+
      optionRow("git_mode","INIT_AND_BIND","git init + origin","Создать Git и связать с GitHub.")+
      optionRow("git_mode","CLONE","git clone","Клонировать существующий репозиторий.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Каркас</div>'+
      optionRow("scaffold_mode","GENERATE_000_100","Создать stages/000…100","Сгенерировать 101 стандартный stage-файл.")+
    '</div>'+
   '</div>'+
   '<div class="stage-card"><div class="card-head">Preflight</div>'+preflightHtml()+'</div>'+
   '<div class="project-links">'+
    '<button id="openGithub" '+(!(preflightResult&&preflightResult.github_exists)?'disabled':'')+'>Открыть GitHub</button>'+
    '<button id="openLocal" '+(!(preflightResult&&preflightResult.local_exists)?'disabled':'')+'>Открыть папку</button>'+
    '<button id="openEvidence" '+(!(verification.evidence_written)?'disabled':'')+'>Открыть evidence</button>'+
   '</div>';
  bindExecutionOptions();
  document.getElementById("runPreflight").onclick=runPreflight;
  document.getElementById("executeProject").onclick=executeProject;
  document.getElementById("verifyProject").onclick=verifyProject;
  const og=document.getElementById("openGithub"); if(og&&!og.disabled)og.onclick=openGithub;
  const ol=document.getElementById("openLocal"); if(ol&&!ol.disabled)ol.onclick=()=>openLocal(proposal.local_directory);
  const oe=document.getElementById("openEvidence"); if(oe&&!oe.disabled)oe.onclick=()=>openLocal(proposal.local_directory+"\\evidence\\stage_001");
 }else if(view==="tests"){
  content.innerHTML='<div class="stage-card"><div class="card-head">Тесты этапа 001</div>'+
   testRow("Этап 000 одобрен",prereqApproved)+
   testRow("ID проекта указан",!!proposal.project_id)+
   testRow("Имя проекта указано",!!proposal.public_name)+
   testRow("Локальный путь указан",!!proposal.local_directory)+
   testRow("Имя репозитория указано",!!proposal.github_repository)+
   testRow("Каркас 000–100 запланирован",true)+'</div>'+
   '<div class="stage-card" style="margin-top:10px"><div class="card-head">Проверка выполнения</div>'+verificationRows()+'</div>';
 }else if(view==="evidence"){
  content.innerHTML='<div class="evidence-json">'+esc(JSON.stringify(evidence(),null,2))+'</div>';
 }else{
  content.innerHTML='<div class="stage-card"><div class="card-head">Человеческий шлюз</div><p>Решение: <b>'+(decision||"PENDING")+'</b></p></div>'+
   '<div class="stage-card" style="margin-top:10px"><div class="card-head">Шлюз проверки</div><p>Результат: <b class="'+(verificationPassed?"pass":"fail")+'">'+(verificationPassed?"ПРОЙДЕНО":"НЕ ПРОЙДЕНО")+'</b></p></div>';
 }
}

function validate(){
 if(!prereqApproved){toast("STAGE 000 не APPROVED");return}
 validated=!!(proposal.project_id&&proposal.public_name&&proposal.code_name&&proposal.local_directory&&proposal.github_owner&&proposal.github_repository&&proposal.default_branch);
 document.getElementById("inputTestPanel").innerHTML=testRow("stage_000_approved",prereqApproved)+testRow("identity_complete",validated);
 document.getElementById("artifactTestPanel").innerHTML=testRow("scaffold_000_100_planned",true)+testRow("creation_not_executed",true);
 if(validated){document.getElementById("stageState").textContent="ГОТОВ К ШЛЮЗУ";enableGate();toast("Предложение этапа 001 прошло проверку")}
 else toast("Предложение заполнено не полностью");
}
function enableGate(){
 document.getElementById("approveGate").disabled=false;
 document.getElementById("approveProject").disabled=false;
 ["holdGate","rejectGate"].forEach(id=>document.getElementById(id).disabled=false);
}
function disableGate(){
 document.getElementById("approveGate").disabled=false;
 document.getElementById("approveProject").disabled=false;
 ["holdGate","rejectGate"].forEach(id=>document.getElementById(id).disabled=true);
}

function decide(d){
 const reason=document.getElementById("gateReason").value.trim();
 if(!validated){toast("Сначала проверьте предложение");return}
 if((d==="HOLD"||d==="REJECT")&&!reason){toast("Для HOLD/REJECT нужна причина");return}
 decision=d;executionApproved=d==="APPROVE";
 document.getElementById("stageState").textContent=d==="APPROVE"?"ВЫПОЛНЕНИЕ ОДОБРЕНО":d==="HOLD"?"УДЕРЖАНО":"ОТКЛОНЕНО";
 sessionStorage.setItem("nexus_stage_001",JSON.stringify(evidence()));
 view=d==="APPROVE"?"execution":"gate";sync();render();
}

async function approveAndExecute(){
 if(!prereqApproved){
  toast("Этап 000 не одобрен");
  return;
 }
 if(!validated){
  validate();
  if(!validated)return;
 }
 operationState="CHECK_RUNTIME";
 document.getElementById("stageState").textContent="ПРОВЕРКА RUNTIME";
 try{
  const health=await fetch(RUNTIME+"/health");
  runtimeOnline=health.ok;
 }catch{
  runtimeOnline=false;
 }
 if(!runtimeOnline){
  operationState="RUNTIME_OFFLINE";
  document.getElementById("stageState").textContent="RUNTIME OFFLINE";
  view="execution";sync();render();
  showRuntimeOffline();
  return;
 }

 decision="APPROVE";
 executionApproved=true;
 traceState("human_gate_approved","APPROVED",{project_id:proposal.project_id});
 document.getElementById("stageState").textContent="PREFLIGHT";
 sessionStorage.setItem("nexus_stage_001",JSON.stringify(evidence()));
 view="execution";sync();render();

 try{
  operationState="PREFLIGHT";
  traceState("preflight_start","STARTED",{repository:proposal.github_owner+"/"+proposal.github_repository,local_directory:proposal.local_directory});
  preflightResult=await api("/stage001/preflight",{proposal:tracedProposal(),execution_plan:executionPlan});
  traceState("preflight_result",preflightResult.conflicts&&preflightResult.conflicts.length?"HOLD":"PASS",{conflicts:preflightResult.conflicts||[]});
  render();

  if(preflightResult.conflicts&&preflightResult.conflicts.length){
   operationState="BLOCKED";
   document.getElementById("stageState").textContent="HOLD · PREFLIGHT";
   sessionStorage.setItem("nexus_stage_001",JSON.stringify(evidence()));
   toast("Создание заблокировано: найден конфликт");
   return;
  }

  operationState="EXECUTING";
  document.getElementById("stageState").textContent="СОЗДАНИЕ ПРОЕКТА";
  render();

  traceState("execution_start","STARTED",{project_id:proposal.project_id});
  const result=await api("/stage001/execute",{proposal:tracedProposal(),execution_plan:executionPlan,approved:true});
  traceState("execution_result",result.status||"UNKNOWN",{steps:result.steps||[]});

  if(result.status==="BLOCKED"){
   operationState="BLOCKED";
   preflightResult=result.preflight||preflightResult;
   document.getElementById("stageState").textContent="HOLD · PREFLIGHT";
   render();
   toast("Создание остановлено повторной проверкой");
   return;
  }

  operationState="VERIFYING";
  document.getElementById("stageState").textContent="ПРОВЕРКА РЕЗУЛЬТАТА";
  await verifyProject();
 }catch(e){
  operationState="ERROR";
  document.getElementById("stageState").textContent="ОШИБКА";
  view="execution";sync();render();
  showExecutionError(e.message);
 }
}

function showRuntimeOffline(){
 const box=document.createElement("div");
 box.className="runtime-blocking-message";
 box.innerHTML='<b>Локальный runtime не запущен</b>'+
  '<span>Сайт не может создавать папки на диске или GitHub-репозитории без локального runtime.</span>'+
  '<code>Set-Location \'G:\\1\\FATHER-Engineering-Competency-Lab-git\'<br>father-factory site-runtime</code>';
 content.prepend(box);
}

function showExecutionError(message){
 const box=document.createElement("div");
 box.className="runtime-blocking-message";
 box.innerHTML='<b>Ошибка выполнения STAGE 001</b><span>'+esc(message)+'</span>';
 content.prepend(box);
}

async function runPreflight(){
 if(!runtimeOnline){toast("Локальный runtime не запущен");return}
 try{
  toast("Проверяю GitHub, папку и Git...");
  preflightResult=await api("/stage001/preflight",{proposal,execution_plan:executionPlan});
  render();
  toast(preflightResult.conflicts.length?"Обнаружены конфликты":"Preflight: конфликтов нет");
 }catch(e){traceState("preflight_error","ERROR",{message:e.message});toast("Preflight error: "+e.message)}
}

async function executeProject(){
 if(!executionApproved){toast("Нет APPROVE");return}
 if(!runtimeOnline){toast("Локальный runtime не запущен");return}
 try{
  const fresh=await api("/stage001/preflight",{proposal,execution_plan:executionPlan});
  preflightResult=fresh;render();
  if(fresh.conflicts&&fresh.conflicts.length){toast("Создание заблокировано: сначала устраните конфликт");return}
  if(!confirm("Preflight чистый. Создать/привязать проект сейчас?"))return;
  const result=await api("/stage001/execute",{proposal,execution_plan:executionPlan,approved:true});
  if(result.status==="BLOCKED"){preflightResult=result.preflight;render();toast("Создание заблокировано новым preflight");return}
  toast("Выполнение завершено: "+result.status);
  await verifyProject();
 }catch(e){traceState("execution_error","ERROR",{message:e.message});toast("Execution error: "+e.message)}
}

async function verifyProject(){
 if(!runtimeOnline)return;
 try{
  traceState("verification_start","STARTED",{project_id:proposal.project_id});
  const v=await api("/stage001/verify",{proposal:tracedProposal()});
  Object.keys(verification).forEach(k=>verification[k]=!!v[k]);
  verificationPassed=Object.values(verification).every(Boolean);
  operationState=verificationPassed?"PASS":"HOLD";
  document.getElementById("verificationState").textContent=verificationPassed?"ПРОЙДЕНО":"НЕ ПРОЙДЕНО";
  document.getElementById("verificationState").className=verificationPassed?"pass":"fail";
  document.getElementById("stageState").textContent=verificationPassed?"ПРОЙДЕНО":"ВЫПОЛНЕНО, НО НЕ ПРОВЕРЕНО";
  document.getElementById("executionVerifyPanel").innerHTML=verificationRows();
  preflightResult=await api("/stage001/preflight",{proposal,execution_plan:executionPlan});
  sessionStorage.setItem("nexus_stage_001",JSON.stringify(evidence()));
  render();
  traceState("verification_result",verificationPassed?"PASS":"HOLD",{verification:{...verification}});
  toast(verificationPassed?"STAGE 001 PASS":"Проверка не пройдена полностью");
 }catch(e){traceState("verification_error","ERROR",{message:e.message});toast("Verification error: "+e.message)}
}

async function openGithub(){
 const url=(preflightResult&&preflightResult.github_url)||("https://github.com/"+proposal.github_owner+"/"+proposal.github_repository);
 window.open(url,"_blank","noopener");
}
async function openLocal(path){
 try{await api("/open/local",{path});}catch(e){toast("Не удалось открыть папку: "+e.message)}
}

function evidence(){
 return {
  stage_id:"STAGE-001",
  prerequisite:{stage:"STAGE-000",approved:prereqApproved},
  proposal,
  input_test:{status:validated?"PASS":"NOT_RUN"},
  artifact_test:{status:validated?"PASS":"LOCKED",planned_stage_files:101},
  human_gate:{decision},
  execution:{approved:executionApproved,plan:executionPlan,preflight:preflightResult,verification,verification_passed:verificationPassed}
 };
}

document.querySelectorAll(".stage-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;sync();render()});
document.getElementById("validateProposal").onclick=validate;
document.getElementById("approveGate").onclick=approveAndExecute;
document.getElementById("holdGate").onclick=()=>decide("HOLD");
document.getElementById("rejectGate").onclick=()=>decide("REJECT");
document.getElementById("approveProject").onclick=approveAndExecute;
render();
checkRuntime();
