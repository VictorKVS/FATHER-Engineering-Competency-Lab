(() => {
  const SESSION_KEY="nexus.trace.session";
  const META_KEY="nexus.trace.meta";
  const EVENTS_KEY="nexus.trace.events";
  const stageMatch=location.pathname.match(/stage(\d{3})\.html/i);
  const stageId=stageMatch?("STAGE-"+stageMatch[1]):"UI";

  let sessionId=sessionStorage.getItem(SESSION_KEY);
  if(!sessionId){
    sessionId=crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY,sessionId);
    sessionStorage.removeItem(META_KEY);
    sessionStorage.removeItem(EVENTS_KEY);
  }

  let traceMeta=null;
  try{traceMeta=JSON.parse(sessionStorage.getItem(META_KEY)||"null")}catch{}
  const listeners=[];

  function now(){return new Date().toISOString()}
  function redact(v){
    if(v==null)return v;
    if(typeof v==="string" && v.length>1000)return v.slice(0,1000)+"…";
    return v;
  }
  function saveLocalEvent(e){
    try{
      const hist=JSON.parse(sessionStorage.getItem(EVENTS_KEY)||"[]");
      hist.push(e);
      sessionStorage.setItem(EVENTS_KEY,JSON.stringify(hist.slice(-3000)));
    }catch{}
  }
  function event(eventType,action,status="INFO",details={}){
    const e={
      event_id:crypto.randomUUID(),
      timestamp:now(),
      session_id:sessionId,
      trace_number:traceMeta&&traceMeta.trace_number||null,
      stage_id:stageId,
      source:"UI",
      event_type:eventType,
      action,
      status,
      actor:"USER",
      target:location.pathname,
      details:Object.fromEntries(Object.entries(details||{}).map(([k,v])=>[k,redact(v)]))
    };
    saveLocalEvent(e);
    listeners.forEach(fn=>fn(e));
    fetch("http://127.0.0.1:8091/events",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(e)
    }).catch(()=>{});
    snapshot().catch(()=>{});
    return e;
  }

  async function startTrace(forceNew=false){
    if(traceMeta&&!forceNew)return traceMeta;
    if(forceNew){
      sessionId=crypto.randomUUID();
      sessionStorage.setItem(SESSION_KEY,sessionId);
      sessionStorage.setItem(EVENTS_KEY,"[]");
    }
    const r=await fetch("http://127.0.0.1:8091/trace/start",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({session_id:sessionId})
    });
    const data=await r.json();
    if(!r.ok)throw new Error(data.message||data.error||("HTTP "+r.status));
    traceMeta={
      trace_number:data.trace_number,
      trace_path:data.path,
      filename:data.filename,
      started_at:now()
    };
    sessionStorage.setItem(META_KEY,JSON.stringify(traceMeta));
    event("STATE_CHANGE","trace_started","ACTIVE",{trace_number:traceMeta.trace_number,trace_path:traceMeta.trace_path});
    return traceMeta;
  }

  async function snapshot(status="ACTIVE"){
    if(!traceMeta||!traceMeta.trace_path)return;
    const uiEvents=events();
    try{
      await fetch("http://127.0.0.1:8091/trace/snapshot",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          session_id:sessionId,
          trace_path:traceMeta.trace_path,
          ui_events:uiEvents,
          page:location.href,
          status
        })
      });
    }catch{}
  }

  function events(){
    try{return JSON.parse(sessionStorage.getItem(EVENTS_KEY)||"[]")}catch{return []}
  }

  document.addEventListener("click",ev=>{
    const el=ev.target.closest("button,a,[role=button]");
    if(!el)return;
    event("BUTTON_CLICK",el.id||el.dataset.view||el.dataset.phase||el.textContent.trim(),"CLICK",{
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
    snapshot("PAGE_LEAVE").catch(()=>{});
  });

  window.NEXUS_TRACE={
    get sessionId(){return sessionId},
    get meta(){return traceMeta},
    emit:event,
    start:startTrace,
    snapshot,
    subscribe(fn){listeners.push(fn)},
    events
  };

  event("NAVIGATION","page_loaded","OK",{url:location.href});
})();