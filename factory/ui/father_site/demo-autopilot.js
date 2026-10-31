const RUNTIME="http://127.0.0.1:8091";
const stageGrid=document.getElementById("stageGrid");
const runStatus=document.getElementById("runStatus");
const runProgress=document.getElementById("runProgress");
const runLog=document.getElementById("runLog");
const resultBox=document.getElementById("resultBox");
const runBtn=document.getElementById("runAutopilot");
let pollTimer=null,lastStage=null;

function renderStages(done=0,current=null,status="RUNNING"){
 stageGrid.innerHTML=Array.from({length:101},(_,i)=>{
   const sid=String(i).padStart(3,"0");
   let cls="locked";
   if(i<done)cls="pass";
   else if(current===("STAGE-"+sid) && status==="RUNNING")cls="active";
   else if(current===("STAGE-"+sid) && (status==="ERROR"||status==="HOLD"))cls="fail";
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
 const options=payload?{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}:{};
 const r=await fetch(RUNTIME+path,options);
 const data=await r.json();
 if(!r.ok)throw new Error(data.message||data.error||("HTTP "+r.status));
 return data;
}
function showChecks(checks={}){
 return Object.entries(checks).filter(([k])=>k!=="pass").map(([k,v])=>
   '<div class="final-check"><span>'+k+'</span><b class="'+(v?"pass":"fail")+'">'+(v?"PASS":"HOLD")+'</b></div>'
 ).join("");
}
async function poll(){
 try{
   const s=await api("/demo/autopilot/status");
   runStatus.textContent=s.status;
   runStatus.className=(s.status==="PASS"?"pass":(s.status==="HOLD"||s.status==="ERROR"?"fail":""));
   runProgress.textContent=(s.completed_stages||0)+" / 101";
   renderStages(s.completed_stages||0,s.current_stage,s.status);
   if(s.current_stage&&s.current_stage!==lastStage){
     lastStage=s.current_stage;
     append(s.current_stage+" · "+s.status);
   }
   if(s.status==="PASS"||s.status==="HOLD"||s.status==="ERROR"){
     clearInterval(pollTimer);pollTimer=null;
   }
 }catch{}
}
async function run(){
 runBtn.disabled=true;
 runStatus.textContent="RUNNING";
 runProgress.textContent="0 / 101";
 renderStages(0,"STAGE-000","RUNNING");
 resultBox.textContent="Идёт сквозной прогон...";
 append("Запуск DEMO_AUTOPILOT 000→100");
 trace("demo_autopilot_start","STARTED",{project_id:"PRJ-STORY-001"});
 lastStage=null;
 if(pollTimer)clearInterval(pollTimer);
 pollTimer=setInterval(poll,350);

 try{
   const health=await fetch(RUNTIME+"/health");
   if(!health.ok)throw new Error("Runtime 8091 недоступен");
   const result=await api("/demo/autopilot/run",{
     root:"G:\\1\\NEXUS-STORY-ENGINE",
     project_id:"PRJ-STORY-001",
     session_id:(window.NEXUS_TRACE&&window.NEXUS_TRACE.sessionId)||"demo",
     push:true
   });
   await poll();
   const checks=result.final_checks||{};
   if(result.status!=="PASS"){
     runStatus.textContent="HOLD";
     runStatus.className="fail";
     trace("demo_autopilot_complete","HOLD",{run_id:result.run_id,checks});
     resultBox.innerHTML='<div class="final-fail"><b>DEMO HOLD</b><span>Финальная проверка не пройдена.</span>'+showChecks(checks)+'</div>';
     append("HOLD · финальная проверка не пройдена");
     return;
   }

   renderStages(101,"STAGE-100","PASS");
   runStatus.textContent="PASS";
   runStatus.className="pass";
   runProgress.textContent="101 / 101";
   append("STAGE 100 PASS · полный минимальный цикл завершён");
   trace("demo_autopilot_complete","PASS",{run_id:result.run_id,completed_stages:result.completed_stages,checks});

   const commit=result.git&&result.git.commit?result.git.commit.returncode:"—";
   const push=result.git&&result.git.push?result.git.push.returncode:"—";
   resultBox.innerHTML='<div class="final-pass"><b>✓ DEMO PRODUCTION PROVEN</b>'+
     '<span>run_id: '+result.run_id+'</span>'+
     '<span>stages: '+result.completed_stages+'/101</span>'+
     '<span>manifest: '+result.manifest+'</span>'+
     '<span>git commit rc: '+commit+'</span>'+
     '<span>git push rc: '+push+'</span>'+
     showChecks(checks)+
     '<button id="openProject">Открыть папку проекта</button></div>';
   document.getElementById("openProject").onclick=()=>api("/open/local",{path:"G:\\1\\NEXUS-STORY-ENGINE"});
 }catch(err){
   if(pollTimer){clearInterval(pollTimer);pollTimer=null}
   runStatus.textContent="ERROR";
   runStatus.className="fail";
   append("ОШИБКА: "+err.message);
   trace("demo_autopilot_error","ERROR",{message:err.message});
   resultBox.innerHTML='<div class="final-fail"><b>DEMO ERROR</b><span>'+err.message+'</span></div>';
 }finally{
   runBtn.disabled=false;
 }
}
runBtn.onclick=run;
renderStages(0,null,"READY");
poll();