const books=[
{id:"BOOK-01",title:"FATHER Agent Engineering",subtitle:"От вызова LLM до production-proven агента",status:"IN_PROGRESS",target:"AGENT_V1",chapters:[
["CH00","Модель — не агент","ACTIVE"],["CH01","API модели и Provider Adapter","PLANNED"],["CH02","Agent Loop и инструменты","PLANNED"],["CH03","Контекстная инженерия","PLANNED"],["CH04","Состояние и память","PLANNED"],["CH05","Prompt, RAG и Knowledge Package","PLANNED"],["CH06","Субагенты и Agent Zoo","PLANNED"],["CH07","Безопасность и Human Gates","PLANNED"],["CH08","Evals, метрики и наблюдаемость","PLANNED"],["CH09","Выбор моделей и турниры","PLANNED"],["CH10","Release, Load, Red Team и Polygon","PLANNED"]]},
{id:"BOOK-02",title:"ALINA Scientific Prompt, RAG & Knowledge Engineering",subtitle:"Инженерия интеллекта агента",status:"PLANNED",target:"INTELLIGENCE_PACKAGE",chapters:[]},
{id:"BOOK-03",title:"FATHER Model Engineering & Selection Lab",subtitle:"Model Zoo, турниры, router, cascade, ensemble",status:"PLANNED",target:"MODEL_FABRIC",chapters:[]}
];
const metrics=[
{id:"M-Q01",name:"Task Success Rate",unit:"%",layer:"QUALITY",state:"TO_MEASURE",desc:"Доля задач, прошедших контракт и критерии качества."},
{id:"M-Q02",name:"Contract Validity",unit:"%",layer:"QUALITY",state:"TO_MEASURE",desc:"Доля структурно корректных выходов."},
{id:"M-Q03",name:"Groundedness / Faithfulness",unit:"score",layer:"QUALITY",state:"PLANNED",desc:"Соответствие ответа предоставленным доказательствам."},
{id:"M-A01",name:"Tool-use Correctness",unit:"%",layer:"AGENT",state:"TO_MEASURE",desc:"Правильный выбор инструмента и корректность аргументов."},
{id:"M-A02",name:"Recovery Rate",unit:"%",layer:"AGENT",state:"TO_MEASURE",desc:"Восстановление после контролируемой ошибки инструмента."},
{id:"M-A03",name:"Steps per Task",unit:"steps",layer:"AGENT",state:"TO_MEASURE",desc:"Число циклов agent loop на задачу."},
{id:"M-R01",name:"Recall@k",unit:"score",layer:"RAG",state:"PLANNED",desc:"Полнота найденного релевантного контекста."},
{id:"M-R02",name:"nDCG / MRR",unit:"score",layer:"RAG",state:"PLANNED",desc:"Качество ранжирования retrieved evidence."},
{id:"M-O01",name:"Latency p50/p95",unit:"ms",layer:"OPS",state:"TO_MEASURE",desc:"Медианная и хвостовая задержка полного запроса."},
{id:"M-O02",name:"Input / Output Tokens",unit:"tokens",layer:"OPS",state:"TO_MEASURE",desc:"Фактическое потребление токенов на задачу."},
{id:"M-O03",name:"VRAM / RAM Peak",unit:"MB",layer:"OPS",state:"PLANNED",desc:"Пиковое потребление ресурсов локального runtime."},
{id:"M-S01",name:"Security Hard-Fail Rate",unit:"count",layer:"SECURITY",state:"PLANNED",desc:"Нарушения политики, утечки, запрещённые tool calls."},
{id:"M-E01",name:"Evidence Completeness",unit:"%",layer:"EVIDENCE",state:"TO_MEASURE",desc:"Наличие trace, config, hashes, metrics и verdict для прогона."}
];
const sc=s=>s.toLowerCase().replaceAll("_","-");
function renderNav(){bookNav.innerHTML=books.map(b=>`<button class="book-nav-item" data-id="${b.id}"><b>${b.id}</b><span>${b.title}</span><i class="${sc(b.status)}">${b.status}</i></button>`).join("");document.querySelectorAll(".book-nav-item").forEach(x=>x.onclick=()=>selectBook(x.dataset.id));}
function renderCards(){bookCards.innerHTML=books.map(b=>`<article class="book-card" data-id="${b.id}"><div class="book-card-top"><b>${b.id}</b><span class="pill ${sc(b.status)}">${b.status}</span></div><h3>${b.title}</h3><p>${b.subtitle}</p><footer><span>ЦЕЛЬ</span><strong>${b.target}</strong></footer></article>`).join("");document.querySelectorAll(".book-card").forEach(x=>x.onclick=()=>selectBook(x.dataset.id));}
function selectBook(id){const b=books.find(x=>x.id===id)||books[0];activeBookTitle.textContent=b.title;bookGate.textContent=b.status.replaceAll("_"," ");bookGate.className="gate "+(b.status==="IN_PROGRESS"?"hold":"planned");document.querySelectorAll(".book-nav-item,.book-card").forEach(x=>x.classList.toggle("selected",x.dataset.id===id));chapters.innerHTML=b.chapters.length?b.chapters.map((c,i)=>`<div class="chapter-row"><div class="chapter-no">${String(i).padStart(2,"0")}</div><div class="chapter-title"><b>${c[0]}</b><strong>${c[1]}</strong></div><div class="chapter-artifacts"><span>ТЕКСТ RU</span><span>ALGORITHM</span><span>CODE</span><span>TEST</span><span>METRICS</span><span>EVIDENCE</span></div><div class="chapter-status ${sc(c[2])}">${c[2]}</div></div>`).join(""):'<div class="chapter-empty">Структура глав будет добавлена после загрузки исходной книги и научного разбора.</div>';}
function renderMetrics(){metricGrid.innerHTML=metrics.map(m=>`<article class="metric-card"><div><b>${m.id}</b><span>${m.layer}</span></div><h3>${m.name}</h3><p>${m.desc}</p><footer><strong>— ${m.unit}</strong><i class="${sc(m.state)}">${m.state.replaceAll("_"," ")}</i></footer></article>`).join("");}
function renderKpis(){const totalCh=books.reduce((a,b)=>a+b.chapters.length,0);const active=books.filter(b=>b.status==="IN_PROGRESS").length;catalogKpis.innerHTML=`<div><span>КНИГ</span><b>${books.length}</b></div><div><span>ГЛАВ</span><b>${totalCh}</b></div><div><span>АКТИВНО</span><b>${active}</b></div><div><span>МЕТРИК</span><b>${metrics.length}</b></div>`;}
renderNav();renderCards();renderMetrics();renderKpis();selectBook("BOOK-01");