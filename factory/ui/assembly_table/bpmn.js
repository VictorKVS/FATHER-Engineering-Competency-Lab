function renderBpmn(){
  const model=window.FATHER_BPMN;
  const c=document.getElementById("factoryCanvas");
  c.className="bpmn-board";
  c.innerHTML="";
  model.lanes.forEach(l=>{
    const lane=document.createElement("section");
    lane.className="lane";
    lane.innerHTML=`<div class="lane-title">${l.name}</div><div class="lane-steps">${l.steps.map(s=>`<div class="bpmn-step">${s}</div>`).join("")}</div>`;
    c.appendChild(lane);
  });
  document.querySelector(".canvas-title h1").textContent="Слой 2. Процессы фабрики — BPMN L1";
  document.querySelector(".canvas-title p").textContent="Swimlane-представление общего процесса. Следующий drill-down — BPMN L2 конкретного цеха.";
  document.getElementById("inspector").innerHTML="<h2>BPMN L1</h2><p>Выберите Business Model, чтобы вернуться на L0. Детализация отдельных цехов будет подключаться на следующем шаге.</p>";
}
