const RUNTIME="http://127.0.0.1:8091";
const stageGrid=document.getElementById("stageGrid");
const runStatus=document.getElementById("runStatus");
const runProgress=document.getElementById("runProgress");
const runLog=document.getElementById("runLog");
const resultBox=document.getElementById("resultBox");
const runBtn=document.getElementById("runAutopilot");

function renderStages(done=0){
 stageGrid.innerHTML=Array.from({length:101},(_,i)=>{
   const sid=String(i).padStart(3,"0");
   const cls=i<done?"pass":i===done&&done<101?"active":"locked";
   return '<div class="demo-stage '+cls+'"><b>'+sid+'</b><span>'+cls.toUpperCase()+'</span></div>';
 }).join("");
}
function trace(action,status,details={}){
 if(window.NEXUS_TRACE)window.NEXUS_TRACE.emit("STATE_CHANGE",action,status,details);
}
function append(msg){
 const t=new Date().toLocaleTimeString();
 runLog.innerHTML='<div><b>'+t+'</b> '+msg+'</div>'+runLog.innerHTML;
}
async function api(path,payload){
 const r=await fetch(RUNTIME+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const data=await r.json();
 if(!r.ok)throw new Error(data.message||data.error||("HTTP "+r.status));
 return data;
}
async function run(){
 runBtn.disabled=true;
 runStatus.textContent="RUNNING";
 runProgress.textContent="0 / 101";
 renderStages(0);
 append("Запуск DEMO_AUTOPILOT 000→100");
 trace("demo_autopilot_start","STARTED",{project_id:"PRJ-STORY-001"});
 try{
   const health=await fetch(RUNTIME+"/health");
   if(!health.ok)throw new Error("Runtime 8091 недоступен");
   const result=await api("/demo/autopilot/run",{
     root:"G:\\1\\NEXUS-STORY-ENGINE",
     project_id:"PRJ-STORY-001",
     session_id:(window.NEXUS_TRACE&&window.NEXUS_TRACE.sessionId)||"demo",
     push:true
   });
   if(result.status!=="PASS")throw new Error("Autopilot status: "+result.status);
   renderStages(101);
   runStatus.textContent="PASS";
   runStatus.className="pass";
   runProgress.textContent="101 / 101";
   append("STAGE 100 PASS · полный минимальный цикл завершён");
   trace("demo_autopilot_complete","PASS",{run_id:result.run_id,completed_stages:result.completed_stages});
   const commit=result.git&&result.git.commit?result.git.commit.returncode:"—";
   const push=result.git&&result.git.push?result.git.push.returncode:"—";
   resultBox.innerHTML='<div class="final-pass"><b>✓ DEMO PRODUCTION PROVEN</b>'+
     '<span>run_id: '+result.run_id+'</span>'+
     '<span>stages: '+result.completed_stages+'/101</span>'+
     '<span>manifest: '+result.manifest+'</span>'+
     '<span>git commit rc: '+commit+'</span>'+
     '<span>git push rc: '+push+'</span>'+
     '<button id="openProject">Открыть папку проекта</button></div>';
   document.getElementById("openProject").onclick=()=>api("/open/local",{path:"G:\\1\\NEXUS-STORY-ENGINE"});
 }catch(err){
   runStatus.textContent="HOLD";
   runStatus.className="fail";
   append("ОШИБКА: "+err.message);
   trace("demo_autopilot_error","ERROR",{message:err.message});
   resultBox.innerHTML='<div class="final-fail"><b>DEMO HOLD</b><span>'+err.message+'</span></div>';
 }finally{
   runBtn.disabled=false;
 }
}
runBtn.onclick=run;
renderStages(0);