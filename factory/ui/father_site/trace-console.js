(() => {
  function mount(){
    if(!window.NEXUS_TRACE||document.getElementById("traceConsoleButton"))return;
    const btn=document.createElement("button");btn.id="traceConsoleButton";btn.className="trace-console-button";btn.textContent="Трассировка";
    const box=document.createElement("section");box.id="traceConsole";box.className="trace-console";
    box.innerHTML='<header><b>Factory Event Trace · '+window.NEXUS_TRACE.sessionId+'</b><div><button id="traceExport">Скачать трассировку</button><button id="traceClose">×</button></div></header><div id="traceConsoleBody" class="trace-console-body"></div>';
    document.body.append(btn,box);
    const body=box.querySelector("#traceConsoleBody");
    const render=()=>{
      const evs=window.NEXUS_TRACE.events().slice(-150).reverse();
      body.innerHTML=evs.map(e=>'<div class="trace-event '+(e.status==="ERROR"?"err":"")+'"><span>'+e.timestamp.slice(11,19)+'</span><b>'+e.event_type+'</b><span>'+String(e.action).replace(/[<>]/g,"")+'</span><i>'+e.status+'</i></div>').join("");
    };
    btn.onclick=()=>{box.classList.toggle("open");render()};
    box.querySelector("#traceClose").onclick=()=>box.classList.remove("open");
    box.querySelector("#traceExport").onclick=async()=>{
      const sessionId=window.NEXUS_TRACE.sessionId;
      const uiEvents=window.NEXUS_TRACE.events();
      let runtimeEvents=[];
      let runtimeStatus="OFFLINE_OR_UNAVAILABLE";
      try{
        const r=await fetch("http://127.0.0.1:8091/events/"+encodeURIComponent(sessionId));
        if(r.ok){
          const data=await r.json();
          runtimeEvents=data.events||[];
          runtimeStatus="ONLINE";
        }
      }catch{}
      const merged=[...uiEvents,...runtimeEvents].sort((a,b)=>String(a.timestamp).localeCompare(String(b.timestamp)));
      const payload={
        schema:"NEXUS_FACTORY_TRACE_EXPORT_V1",
        exported_at:new Date().toISOString(),
        session_id:sessionId,
        page:location.href,
        runtime_status:runtimeStatus,
        ui_event_count:uiEvents.length,
        runtime_event_count:runtimeEvents.length,
        total_event_count:merged.length,
        events:merged
      };
      const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
      const a=document.createElement("a");
      a.href=URL.createObjectURL(blob);
      a.download="NEXUS_TRACE_"+sessionId+".json";
      a.click();
      URL.revokeObjectURL(a.href);
    };
    window.NEXUS_TRACE.subscribe(()=>{if(box.classList.contains("open"))render()});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();