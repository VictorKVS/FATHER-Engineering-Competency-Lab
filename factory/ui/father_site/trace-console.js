(() => {
  function esc(v){return String(v==null?"":v).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
  function dateFromFilename(name){
    const m=String(name||"").match(/NEXUS_TRACE_(\d{4}-\d{2}-\d{2})_(\d+)\.json/);
    return m?m[1]:new Date().toISOString().slice(0,10);
  }
  function mount(){
    if(!window.NEXUS_TRACE||document.getElementById("traceConsoleButton"))return;

    const badge=document.createElement("div");
    badge.id="traceBadge";
    badge.className="trace-badge";
    badge.innerHTML='<b>TRACE</b><span>НЕ ЗАПУЩЕНА</span>';
    document.body.appendChild(badge);

    const start=document.createElement("button");
    start.id="traceStartButton";
    start.className="trace-start-button";
    start.textContent="НАЧАТЬ ТРАССИРОВКУ";
    document.body.appendChild(start);

    const btn=document.createElement("button");
    btn.id="traceConsoleButton";
    btn.className="trace-console-button";
    btn.textContent="Трассировка";

    const box=document.createElement("section");
    box.id="traceConsole";
    box.className="trace-console";
    box.innerHTML='<header><b>Factory Event Trace</b><div><button id="traceExport">Сохранить трассировку</button><button id="traceClose">×</button></div></header><div id="traceConsoleBody" class="trace-console-body"></div>';
    document.body.append(btn,box);

    const body=box.querySelector("#traceConsoleBody");

    function refreshMeta(){
      const meta=window.NEXUS_TRACE.meta;
      if(meta){
        const d=dateFromFilename(meta.filename);
        badge.innerHTML='<b>TRACE '+esc(d)+' / #'+String(meta.trace_number).padStart(3,"0")+'</b><span>'+esc(meta.filename)+'</span>';
        badge.classList.add("active");
        start.textContent="НОВАЯ ТРАССИРОВКА";
      }else{
        badge.innerHTML='<b>TRACE</b><span>НЕ ЗАПУЩЕНА</span>';
        badge.classList.remove("active");
        start.textContent="НАЧАТЬ ТРАССИРОВКУ";
      }
    }

    const render=()=>{
      const evs=window.NEXUS_TRACE.events().slice(-200).reverse();
      body.innerHTML=evs.map(e=>'<div class="trace-event '+(e.status==="ERROR"?"err":"")+'"><span>'+esc(String(e.timestamp).slice(11,19))+'</span><b>'+esc(e.event_type)+'</b><span>'+esc(e.action)+'</span><i>'+esc(e.status)+'</i></div>').join("");
      refreshMeta();
    };

    start.onclick=async()=>{
      start.disabled=true;
      start.textContent="ЗАПУСК...";
      try{
        await window.NEXUS_TRACE.start(!!window.NEXUS_TRACE.meta);
        refreshMeta();
        alert("Трассировка запущена:\n"+window.NEXUS_TRACE.meta.trace_path);
      }catch(err){
        alert("Не удалось запустить трассировку. Проверьте runtime на 8091.\n"+err.message);
      }finally{
        start.disabled=false;
        refreshMeta();
      }
    };

    btn.onclick=()=>{box.classList.toggle("open");render()};
    box.querySelector("#traceClose").onclick=()=>box.classList.remove("open");
    box.querySelector("#traceExport").onclick=async()=>{
      try{
        await window.NEXUS_TRACE.snapshot("MANUAL_SAVE");
        const meta=window.NEXUS_TRACE.meta;
        alert(meta?"Трассировка сохранена:\n"+meta.trace_path:"Сначала запустите трассировку.");
      }catch(err){
        alert("Не удалось сохранить трассировку.\n"+err.message);
      }
    };

    window.NEXUS_TRACE.subscribe(()=>{if(box.classList.contains("open"))render();refreshMeta()});
    refreshMeta();

    // Auto-start only when runtime is available and this browser session has no active trace.
    if(!window.NEXUS_TRACE.meta){
      window.NEXUS_TRACE.start(false).then(refreshMeta).catch(()=>refreshMeta());
    }
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();