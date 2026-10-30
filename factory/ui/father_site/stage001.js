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
document.getElementById("stageState").textContent=prereqApproved?"READY":"LOCKED";
if(!prereqApproved) document.getElementById("stageState").classList.add("fail");

function render(){
 if(view==="proposal"){
  content.innerHTML='<div class="proposal-form">'+
   field("Project ID","project_id")+field("Public name","public_name")+field("Code name","code_name")+
   field("Local directory","local_directory","span2")+field("GitHub owner","github_owner")+field("GitHub repository","github_repository")+
   field("Visibility","visibility")+field("Default branch","default_branch")+field("License","license")+
   '</div><div class="notice" style="margin-top:12px">На этой статической странице APPROVE формирует только разрешённый execution plan. Реальное создание каталога и GitHub-репозитория должен выполнить backend/runtime фабрики.</div>';
  Object.keys(proposal).forEach(k=>{const e=document.getElementById(k);if(e){e.value=proposal[k];e.oninput=ev=>{proposal[k]=ev.target.value;validated=false;disableGate()}}});
 }else if(view==="scaffold"){
  content.innerHTML='<div class="scaffold-grid">'+Array.from({length:101},(_,i)=>{const n=String(i).padStart(3,"0");return '<div class="stage-chip"><b>'+n+'</b>'+(i===0?"IDEA_INTAKE":i===1?"PROJECT_INITIALIZATION":i===100?"PRODUCTION_PROVEN":"LOCKED")+'</div>'}).join("")+'</div>';
 }else if(view==="execution"){
  content.innerHTML=
   '<div class="execution-layout">'+
    '<div class="stage-card"><div class="card-head">GitHub execution</div>'+
      optionRow("github_mode","CREATE_NEW","Создать новый GitHub repository","Фабрика создаёт новый репозиторий после APPROVE.")+
      optionRow("github_mode","BIND_EXISTING","Привязать существующий repository","Использовать уже существующий GitHub repository.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Local execution</div>'+
      optionRow("local_mode","CREATE_NEW","Создать новую папку","Создать "+proposal.local_directory)+
      optionRow("local_mode","USE_EXISTING","Использовать существующую папку","Проверить и принять существующий каталог.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Git binding</div>'+
      optionRow("git_mode","INIT_AND_BIND","git init + remote origin","Инициализировать локальный Git и связать с GitHub.")+
      optionRow("git_mode","CLONE","git clone","Клонировать существующий repository в local directory.")+
    '</div>'+
    '<div class="stage-card"><div class="card-head">Project chassis</div>'+
      optionRow("scaffold_mode","GENERATE_000_100","Создать stages/000…100","Сгенерировать 101 стандартный stage-файл.")+
      '<div class="execution-summary"><b>После APPROVE</b><span>GitHub + Local + Git binding + 000–100 + initial commit + evidence</span></div>'+
    '</div>'+
   '</div>';
  bindExecutionOptions();
 }else if(view==="tests"){
  content.innerHTML='<div class="stage-card"><div class="card-head">Stage 001 Tests</div>'+testRow("STAGE 000 approved",prereqApproved)+testRow("Project ID present",!!proposal.project_id)+testRow("Project name present",!!proposal.public_name)+testRow("Local path present",!!proposal.local_directory)+testRow("Repository name present",!!proposal.github_repository)+testRow("000–100 scaffold planned",true)+'</div>'+
  '<div class="stage-card" style="margin-top:10px"><div class="card-head">Execution Verification</div>'+verificationRows()+'</div>';
 }else if(view==="evidence"){
  content.innerHTML='<div class="evidence-json">'+esc(JSON.stringify(evidence(),null,2))+'</div>';
 }else{
  content.innerHTML='<div class="stage-card"><div class="card-head">Human Gate</div><p style="font-size:9px;color:#748a9b">Decision: <b>'+(decision||"PENDING")+'</b></p>'+(decision==="APPROVE"?'<p class="pass" style="font-size:9px">Execution plan approved. Creation is permitted.</p>':'')+'</div>'+
  '<div class="stage-card" style="margin-top:10px"><div class="card-head">Verification Gate</div><p style="font-size:9px;color:#748a9b">Result: <b class="'+(verificationPassed?"pass":"fail")+'">'+(verificationPassed?"PASS":"NOT PASSED")+'</b></p><p style="font-size:9px;color:#748a9b">STAGE 001 считается пройденным только после фактической проверки GitHub, local folder, git binding, scaffold и evidence.</p></div>';
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
function testRow(n,p){return '<div class="test-row"><span>'+n+'</span><b class="'+(p?"pass":"fail")+'">'+(p?"PASS":"HOLD")+'</b></div>'}
function validate(){
 if(!prereqApproved){toast("STAGE 000 не APPROVED");return}
 const ok=proposal.project_id&&proposal.public_name&&proposal.code_name&&proposal.local_directory&&proposal.github_owner&&proposal.github_repository&&proposal.default_branch;
 validated=!!ok;
 document.getElementById("inputTestPanel").innerHTML=testRow("stage_000_approved",prereqApproved)+testRow("identity_complete",validated);
 document.getElementById("artifactTestPanel").innerHTML=testRow("scaffold_000_100_planned",true)+testRow("creation_not_executed",true);
 if(validated){document.getElementById("stageState").textContent="READY_FOR_GATE";enableGate();toast("STAGE 001 proposal PASS")}
 else toast("Proposal incomplete");
}
function refreshVerificationPanels(){
 document.getElementById("executionVerifyPanel").innerHTML=verificationRows();
 document.getElementById("verificationState").textContent=verificationPassed?"PASS":"NOT PASSED";
 document.getElementById("verificationState").className=verificationPassed?"pass":"fail";
}
function markExecutionVerifiedDemo(){
 if(!executionApproved){toast("Сначала APPROVE execution plan");return}
 Object.keys(verification).forEach(k=>verification[k]=true);
 verificationPassed=true;
 document.getElementById("stageState").textContent="PASS";
 refreshVerificationPanels();
 const ev=evidence();sessionStorage.setItem("nexus_stage_001",JSON.stringify(ev));
 toast("STAGE 001 PASS: execution verified");
 view="gate";sync();render();
}
function enableGate(){["approveGate","holdGate","rejectGate","approveProject"].forEach(id=>document.getElementById(id).disabled=false)}
function disableGate(){["approveGate","holdGate","rejectGate","approveProject"].forEach(id=>document.getElementById(id).disabled=true)}
function decide(d){
 const reason=document.getElementById("gateReason").value.trim();
 if(!validated){toast("Сначала проверьте proposal");return}
 if((d==="HOLD"||d==="REJECT")&&!reason){toast("Для HOLD/REJECT нужна причина");return}
 decision=d;
 executionApproved=d==="APPROVE";
 document.getElementById("stageState").textContent=d==="APPROVE"?"EXECUTION_APPROVED":d==="HOLD"?"HOLD":"REJECTED";
 const ev=evidence();sessionStorage.setItem("nexus_stage_001",JSON.stringify(ev));
 view="gate";sync();render();toast("Human Gate: "+d);
}
function evidence(){return {stage_id:"STAGE-001",state:document.getElementById("stageState").textContent,prerequisite:{stage:"STAGE-000",approved:prereqApproved},proposal,input_test:{status:validated?"PASS":"NOT_RUN"},artifact_test:{status:validated?"PASS":"LOCKED",planned_stage_files:101},human_gate:{decision},execution:{approved:executionApproved,plan:executionPlan,verification,verification_passed:verificationPassed,requires_runtime:true}}}
function sync(){document.querySelectorAll(".stage-tab").forEach(x=>x.classList.toggle("active",x.dataset.view===view))}
function esc(v){return v.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}
document.querySelectorAll(".stage-tab").forEach(b=>b.onclick=()=>{view=b.dataset.view;sync();render()});
document.getElementById("validateProposal").onclick=validate;
document.getElementById("approveGate").onclick=()=>decide("APPROVE");
document.getElementById("holdGate").onclick=()=>decide("HOLD");
document.getElementById("rejectGate").onclick=()=>decide("REJECT");
document.getElementById("approveProject").onclick=()=>decide("APPROVE");
document.getElementById("executionVerifyPanel").ondblclick=markExecutionVerifiedDemo;
render();