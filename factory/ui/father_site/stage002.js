const prev=JSON.parse(sessionStorage.getItem("nexus_stage_001")||"null");
const prereq=!!(prev&&prev.execution&&prev.execution.verification_passed);
let validated=false,decision=null;
const fields=["problem","user","value","success","scope"];
const $=id=>document.getElementById(id);
$("stage001State").textContent="STAGE-001 · "+(prereq?"PASS":"NOT PASS");
$("stageState").textContent=prereq?"ГОТОВ":"LOCKED";

function trace(action,status,details={}){
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("STATE_CHANGE",action,status,details);
}
function row(name,pass){return '<div class="test-row"><span>'+name+'</span><b class="'+(pass?"pass":"fail")+'">'+(pass?"ПРОЙДЕНО":"УДЕРЖАНО")+'</b></div>'}
function toast(msg){const t=$("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2200)}
function snapshot(){return {stage_id:"STAGE-002",prerequisite:{stage:"STAGE-001",pass:prereq},artifact:Object.fromEntries(fields.map(id=>[id,$(id).value.trim()])),input_test:{status:validated?"PASS":"NOT_RUN"},artifact_test:{status:validated?"PASS":"NOT_RUN"},human_gate:{decision}}}
function validate(){
 if(!prereq){toast("STAGE 001 ещё не PASS");return false}
 const vals=fields.map(id=>$(id).value.trim());
 validated=vals.every(v=>v.length>=12);
 $("inputTest").innerHTML=row("stage_001_pass",prereq)+row("required_fields",validated);
 $("artifactTest").innerHTML=row("problem_defined",$( "problem").value.trim().length>=12)+row("success_measurable",$( "success").value.trim().length>=12)+row("scope_explicit",$( "scope").value.trim().length>=12);
 $("stageState").textContent=validated?"ГОТОВ К ШЛЮЗУ":"HOLD";
 trace("stage_002_validation",validated?"PASS":"HOLD",{validated});
 return validated;
}
function approve(){
 if(!validated&&!validate())return;
 decision="APPROVE";
 sessionStorage.setItem("nexus_stage_002",JSON.stringify(snapshot()));
 $("stageState").textContent="APPROVED";
 $("resultPanel").innerHTML='<div class="stage-pass"><b>✓ STAGE 002 ОДОБРЕН</b><span>Артефакт PRODUCT_INTENT зафиксирован. STAGE 003 можно проектировать следующим.</span></div>';
 trace("stage_002_human_gate","APPROVED",{});
 toast("STAGE 002 APPROVED");
}
$("validateIntent").onclick=validate;
$("approveIntent").onclick=approve;
$("approveGate").onclick=approve;
$("holdGate").onclick=()=>{decision="HOLD";$("stageState").textContent="HOLD";trace("stage_002_human_gate","HOLD",{})};
$("rejectGate").onclick=()=>{decision="REJECT";$("stageState").textContent="REJECTED";trace("stage_002_human_gate","REJECTED",{})};
