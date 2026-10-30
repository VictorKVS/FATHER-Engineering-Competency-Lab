(() => {
  const KEY="nexus.trace.session";
  const sessionId=sessionStorage.getItem(KEY)||crypto.randomUUID();
  sessionStorage.setItem(KEY,sessionId);
  const stageMatch=location.pathname.match(/stage(\d{3})\.html/i);
  const stageId=stageMatch?("STAGE-"+stageMatch[1]):"UI";
  const queue=[];
  const listeners=[];

  function now(){return new Date().toISOString()}
  function redact(v){
    if(v==null)return v;
    if(typeof v==="string" && v.length>500)return v.slice(0,500)+"…";
    return v;
  }
  function event(eventType,action,status="INFO",details={}){
    const e={
      event_id:crypto.randomUUID(),
      timestamp:now(),
      session_id:sessionId,
      stage_id:stageId,
      source:"UI",
      event_type:eventType,
      action,
      status,
      actor:"USER",
      target:location.pathname,
      details:Object.fromEntries(Object.entries(details||{}).map(([k,v])=>[k,redact(v)]))
    };
    queue.push(e);
    try{
      const hist=JSON.parse(sessionStorage.getItem("nexus.trace.events")||"[]");
      hist.push(e);
      sessionStorage.setItem("nexus.trace.events",JSON.stringify(hist.slice(-1000)));
    }catch{}
    listeners.forEach(fn=>fn(e));
    fetch("http://127.0.0.1:8091/events",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(e)
    }).catch(()=>{});
    return e;
  }

  document.addEventListener("click",ev=>{
    const el=ev.target.closest("button,a,[role=button]");
    if(!el)return;
    event("BUTTON_CLICK",el.id||el.dataset.view||el.dataset.phase||el.textContent.trim(), "CLICK", {
      text:el.textContent.trim(),
      href:el.getAttribute("href")||null
    });
  },true);

  document.addEventListener("change",ev=>{
    const el=ev.target;
    if(!el||!el.id)return;
    event("INPUT_CHANGE",el.id,"CHANGED",{type:el.type||el.tagName});
  },true);

  window.addEventListener("beforeunload",()=>{
    event("NAVIGATION","leave_page","INFO",{to:document.activeElement&&document.activeElement.href||null});
  });

  window.NEXUS_TRACE={
    sessionId,
    emit:event,
    subscribe(fn){listeners.push(fn)},
    events(){
      try{return JSON.parse(sessionStorage.getItem("nexus.trace.events")||"[]")}catch{return []}
    }
  };

  event("NAVIGATION","page_loaded","OK",{url:location.href});
})();