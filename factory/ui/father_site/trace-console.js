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
      const exportBtn=box.querySelector("#traceExport");
      const sessionId=window.NEXUS_TRACE.sessionId;
      const uiEvents=window.NEXUS_TRACE.events();
      exportBtn.disabled=true;
      exportBtn.textContent="Сохраняю...";
      try{
        const r=await fetch("http://127.0.0.1:8091/events/export",{
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body:JSON.stringify({
            session_id:sessionId,
            page:location.href,
            ui_events:uiEvents
          })
        });
        const data=await r.json();
        if(!r.ok)throw new Error(data.message||data.error||("HTTP "+r.status));
        exportBtn.textContent="Сохранено";
        alert("Трассировка сохранена:\n"+data.path);
      }catch(err){
        exportBtn.textContent="Ошибка";
        alert("Не удалось сохранить трассировку. Проверьте runtime на 8091.\n"+err.message);
      }finally{
        setTimeout(()=>{exportBtn.disabled=false;exportBtn.textContent="Скачать трассировку"},1800);
      }
    };
    window.NEXUS_TRACE.subscribe(()=>{if(box.classList.contains("open"))render()});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();