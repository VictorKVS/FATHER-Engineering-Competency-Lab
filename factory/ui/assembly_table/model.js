window.FATHER_MODEL = {
  id: "FATHER-FACTORY-L0",
  version: "0.1.0",
  layers: [
    {id:"business",name:"1. Бизнес-модель",active:true},
    {id:"bpmn",name:"2. Процессы BPMN"},
    {id:"api",name:"3. API слой"},
    {id:"data",name:"4. Данные"},
    {id:"llm",name:"5. Агенты / LLM"},
    {id:"infra",name:"6. Инфраструктура"},
    {id:"security",name:"7. Безопасность"},
    {id:"tests",name:"8. Тесты / Полигон"},
    {id:"monitoring",name:"9. Мониторинг"},
    {id:"release",name:"10. Релиз / Продажа"},
    {id:"engine",name:"11. FATHER Engine"}
  ],
  nodes: [
    {id:"CUSTOMER",step:"00",name:"Заказчик / Идея",kind:"customer",status:"READY",purpose:"Формирует потребность, бизнес-цель, ограничения и ожидаемую ценность.",output:"Customer Intent"},
    {id:"W00",step:"01",name:"Приём и формализация",kind:"workshop",status:"DRAFT",purpose:"Преобразует исходный запрос в формальный Customer Intent.",output:"Customer Intent Package"},
    {id:"W01",step:"02",name:"Бизнес-анализ",kind:"workshop",status:"DRAFT",purpose:"Строит бизнес-модель, BPMN, роли, потоки, правила и критерии приёмки.",output:"Business Design Package"},
    {id:"W02",step:"03",name:"Системный анализ",kind:"workshop",status:"NOT_DEFINED",purpose:"Преобразует бизнес-модель в системные требования и интерфейсы.",output:"System Design Package"},
    {id:"W03",step:"04",name:"Архитектура",kind:"workshop",status:"NOT_DEFINED",purpose:"Проектирует целевую архитектуру и распределение ответственности.",output:"Architecture Package"},
    {id:"W04",step:"05",name:"Данные и знания",kind:"workshop",status:"NOT_DEFINED",purpose:"Проектирует данные, RAG, knowledge graph, provenance и lifecycle знаний.",output:"Data & Knowledge Package"},
    {id:"W05",step:"06",name:"AI / LLM Design",kind:"workshop",status:"NOT_DEFINED",purpose:"Выбирает LLM-роли, routing, prompts, context, eval и fallback.",output:"AI Configuration Package"},
    {id:"W06",step:"07",name:"Безопасность",kind:"workshop",status:"NOT_DEFINED",purpose:"Проектирует trust boundaries, threat model, policies и security gates.",output:"Security Package"},
    {id:"W07",step:"08",name:"Разработка / сборка",kind:"workshop",status:"NOT_DEFINED",purpose:"Собирает компоненты, адаптеры, код и конфигурацию.",output:"Build Artifact"},
    {id:"W08",step:"09",name:"QA / Test",kind:"workshop",status:"NOT_DEFINED",purpose:"Проверяет функциональность, интеграции, регрессии и качество AI.",output:"Test Evidence"},
    {id:"W10",step:"10",name:"Оптимизация / A-B",kind:"workshop",status:"NOT_DEFINED",purpose:"Сравнивает конфигурации и выбирает Best Known Configuration.",output:"Best Known Configuration"},
    {id:"W12",step:"11",name:"Полигон",kind:"polygon",status:"NOT_DEFINED",purpose:"Испытывает фиксированный RC adversarial/failure/load/recovery сценариями.",output:"Polygon Report"},
    {id:"W14",step:"12",name:"Релиз / Продажа",kind:"release",status:"NOT_DEFINED",purpose:"Формирует release package, развертывание и коммерческую поставку.",output:"Release Package"}
  ],
  flows: [
    {id:"F001",name:"Customer Intent",producer:"CUSTOMER",consumer:"W00",payload:"customer_intent.yaml",quality:"UNKNOWN → normalized",protocol:"human/chat/form"},
    {id:"F002",name:"Formalized Intent",producer:"W00",consumer:"W01",payload:"customer_intent_package",quality:"G0 INTENT READY",protocol:"GitHub artifact handoff"},
    {id:"F003",name:"Business Design Package",producer:"W01",consumer:"W02",payload:"BA-OUTPUT-v0.1",quality:"G1 BUSINESS READY",protocol:"GitHub artifact handoff"},
    {id:"F004",name:"System Design Package",producer:"W02",consumer:"W03",payload:"system_design_package",quality:"validated",protocol:"GitHub artifact handoff"},
    {id:"F005",name:"Architecture Package",producer:"W03",consumer:"W04",payload:"architecture_package",quality:"G2 ARCHITECTURE READY",protocol:"GitHub artifact handoff"},
    {id:"F006",name:"Data & Knowledge Package",producer:"W04",consumer:"W05",payload:"data_knowledge_package",quality:"validated",protocol:"GitHub artifact handoff"},
    {id:"F007",name:"AI Configuration Package",producer:"W05",consumer:"W06",payload:"ai_configuration_package",quality:"validated",protocol:"GitHub artifact handoff"},
    {id:"F008",name:"Security Package",producer:"W06",consumer:"W07",payload:"security_package",quality:"security gate",protocol:"GitHub artifact handoff"},
    {id:"F009",name:"Build Artifact",producer:"W07",consumer:"W08",payload:"build_manifest",quality:"G3 BUILD READY",protocol:"artifact registry"},
    {id:"F010",name:"Test Evidence",producer:"W08",consumer:"W10",payload:"test_evidence",quality:"G4 FACTORY VERIFIED",protocol:"evidence registry"},
    {id:"F011",name:"Best Known Configuration",producer:"W10",consumer:"W12",payload:"BKC + frozen RC",quality:"RC FROZEN",protocol:"immutable RC package"},
    {id:"F012",name:"Polygon PASS / FAIL",producer:"W12",consumer:"W14",payload:"polygon_report",quality:"G5 POLYGON VERIFIED",protocol:"signed evidence package"}
  ]
};
