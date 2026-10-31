const state=document.getElementById("tournamentState");
const rows=document.getElementById("leaderboardRows");
const runBtn=document.getElementById("runTournament");
const resetBtn=document.getElementById("resetTournament");
const activeModelName=document.getElementById("activeModelName");
const activeModelMeta=document.getElementById("activeModelMeta");
const chips=[...document.querySelectorAll(".model-chip")];

const DEMO=[
 {model_id:"MODEL-A",status:"PASS",score:86,latency_ms:4200,hard_fails:[],role:"FALLBACK"},
 {model_id:"MODEL-B",status:"PASS",score:92,latency_ms:6100,hard_fails:[],role:"PRIMARY"},
 {model_id:"MODEL-C",status:"FAIL",score:97,latency_ms:2500,hard_fails:["canon_break"],role:"REJECTED"}
];

function trace(action,status,details={}){
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("STATE_CHANGE",action,status,details);
}
function wait(ms){return new Promise(r=>setTimeout(r,ms))}
function setChip(model,status){
 const chip=chips.find(x=>x.dataset.model===model);
 if(!chip)return;
 chip.className="model-chip "+status.toLowerCase();
 chip.querySelector("span").textContent=status;
}
function setActive(model,meta){
 chips.forEach(x=>x.classList.toggle("active",x.dataset.model===model));
 activeModelName.textContent=model;
 activeModelMeta.textContent=meta;
}
function renderLeaderboard(data){
 rows.innerHTML=data.slice().sort((a,b)=>{
   if(a.status!==b.status)return a.status==="PASS"?-1:1;
   if(a.score!==b.score)return b.score-a.score;
   return a.latency_ms-b.latency_ms;
 }).map((r,i)=>'<div class="leader-row '+(i===0&&r.status==="PASS"?"winner":"")+'">'+
   '<span><b>'+r.model_id+'</b></span>'+
   '<span><b class="'+(r.status==="PASS"?"pass":"fail")+'">'+r.status+'</b></span>'+
   '<span>'+r.score+'</span>'+
   '<span>'+r.latency_ms+' ms</span>'+
   '<span>'+(r.hard_fails.length?r.hard_fails.join(", "):"—")+'</span>'+
   '<span>'+r.role+'</span>'+
 '</div>').join("");
}
function reset(){
 state.textContent="READY";state.className="hold";
 rows.innerHTML="";
 chips.forEach(x=>{x.className="model-chip";x.querySelector("span").textContent="WAITING"});
 chips[0].classList.add("active");
 setActive("MODEL-A","готов к тесту");
 ["gateContract","gateCanon","gateSecurity","gateRuntime"].forEach(id=>{
  const e=document.getElementById(id);e.textContent="PENDING";e.className="";
 });
 document.getElementById("winnerOrb").textContent="?";
 document.getElementById("winnerName").textContent="Победитель ещё не выбран";
 document.getElementById("winnerReason").textContent="Запустите турнир. Победит лучшая модель, прошедшая все hard gates.";
 document.getElementById("primaryModel").textContent="—";
 document.getElementById("fallbackModel").textContent="—";
 document.getElementById("fastModel").textContent="—";
}
async function run(){
 reset();
 runBtn.disabled=true;
 state.textContent="RUNNING";state.className="running";
 trace("agent_model_tournament","STARTED",{agent_id:"AG-STORY-001"});
 const completed=[];
 for(const r of DEMO){
   setActive(r.model_id,"выполняет одинаковую задачу");
   setChip(r.model_id,"RUNNING");
   await wait(650);
   setChip(r.model_id,r.status);
   completed.push(r);
   renderLeaderboard(completed);
   trace("model_candidate_complete",r.status,{model_id:r.model_id,score:r.score,hard_fails:r.hard_fails});
 }
 const winner=DEMO.filter(x=>x.status==="PASS").sort((a,b)=>b.score-a.score)[0];
 document.getElementById("gateContract").textContent="PASS";document.getElementById("gateContract").className="pass";
 document.getElementById("gateCanon").textContent="PASS";document.getElementById("gateCanon").className="pass";
 document.getElementById("gateSecurity").textContent="PASS";document.getElementById("gateSecurity").className="pass";
 document.getElementById("gateRuntime").textContent="PASS";document.getElementById("gateRuntime").className="pass";
 document.getElementById("winnerOrb").textContent="✓";
 document.getElementById("winnerName").textContent=winner.model_id+" выбран PRIMARY";
 document.getElementById("winnerReason").textContent="Score "+winner.score+" · hard fails отсутствуют · одинаковый замороженный Agent Construct.";
 document.getElementById("primaryModel").textContent=winner.model_id;
 document.getElementById("fallbackModel").textContent="MODEL-A";
 document.getElementById("fastModel").textContent="MODEL-C*";
 state.textContent="DEMO PASS";state.className="pass";
 setActive(winner.model_id,"выбран PRIMARY");
 trace("agent_model_tournament","DEMO_PASS",{winner:winner.model_id});
 runBtn.disabled=false;
}
runBtn.onclick=run;
resetBtn.onclick=reset;
reset();