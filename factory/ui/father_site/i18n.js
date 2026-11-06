(() => {
  const STORAGE_KEY = "nexus.language";
  const SUPPORTED = [
    ["ru","Русский"],
    ["en","English"],
    ["de","Deutsch"],
    ["fr","Français"],
    ["es","Español"],
    ["zh-CN","中文"]
  ];

  const T = {
    en: {
      "Настройки":"Settings","Язык интерфейса":"Interface language","Закрыть":"Close",
      "Инженерная фабрика ИИ":"AI Engineering Factory","ИНЖЕНЕРИЯ ИИ-СИСТЕМ":"AI SYSTEMS ENGINEERING",
      "РАБОЧИЕ ОБЛАСТИ":"WORKSPACES","Конструктор агентов":"Agent Designer","Процессы":"Workflow",
      "Лаборатория моделей":"Model Lab","RAG / Знания":"RAG / Knowledge","Полигон":"Polygon",
      "АКТИВНО":"LIVE","ЗАКРЫТО":"LOCKED","ИНЖЕНЕРНАЯ СИСТЕМА РАБОТАЕТ":"ENGINEERING SYSTEM ONLINE",
      "ПОЛЕ 01 · ПРОЕКТИРОВАНИЕ АГЕНТА":"FIELD 01 · AGENT ENGINEERING","Проектирование агента":"Agent Design",
      "Новая идея · STAGE 000":"New idea · STAGE 000","Демо: идея → проект":"Demo: idea → project",
      "Специалисты":"Specialists","Трассируемость":"Traceability","Создать агента из шаблона":"Create agent from template",
      "Загрузить demo агента":"Load demo agent","Проверить конструкцию":"Validate design","Экспорт JSON":"Export JSON",
      "Агент":"Agent","Профиль":"Profile","Слот модели":"Model slot","Шлюз":"Gate",
      "КАТАЛОГ БЛОКОВ":"BLOCK CATALOG","ИНЖЕНЕРНЫЙ КАНОН":"ENGINEERING CANON",
      "ПОЛЕ СБОРКИ АГЕНТА":"AGENT ASSEMBLY CANVAS","ИНСПЕКТОР":"INSPECTOR","БЛОК":"BLOCK",
      "ГОТОВНОСТЬ":"READINESS","ЛОКАЛЬНЫЙ ЗООПАРК МОДЕЛЕЙ":"LOCAL MODEL ZOO",
      "ДЕМО":"DEMO","ДЕМО ИНЖЕНЕРИИ ЗНАНИЙ":"KNOWLEDGE ENGINEERING DEMO","Подготовить демо-прогон":"Prepare demo run",
      "Входной контракт":"Input Contract","Роль":"Role","Промпт":"Prompt","База знаний":"Knowledge Base",
      "Выходной контракт":"Output Contract","Оценки":"Evals","Доказательства":"Evidence",
      "Описание":"Description","Где находится":"Location","Редактирование":"Editing","ЛОКАЛЬНЫЙ ЧЕРНОВИК":"LOCAL DRAFT",
      "Экспорт блока":"Export block","Редактировать":"Edit","ДЕМО-ПРОДУКТЫ":"DEMO PRODUCTS",
      "ПРЕСЕТЫ ФАБРИКИ":"FACTORY PRESETS","Рассказ / Смена модели":"Story / Model Swap",
      "OSINT-исследование":"OSINT Research","Анализ безопасности":"Security Analysis","СТАРТ 000 →":"START 000 →",
      "ФАБРИКА АГЕНТОВ":"AGENT FACTORY","Шаблон":"Template","Новый стабильный ID":"New stable ID",
      "Публичное имя":"Public name","Кодовое имя":"Code name","Назначение":"Purpose","Предметная область":"Domain",
      "Начальное состояние":"Initial state","НАСЛЕДУЕТСЯ":"INHERIT","ПЕРЕСОБИРАЕТСЯ":"REBUILD","Отмена":"Cancel",
      "Регистрация идеи":"Idea Intake","ВХОДНОЙ ШЛЮЗ ФАБРИКИ":"FACTORY ENTRY GATE","ФАЗЫ":"PHASES",
      "01 · ВХОД":"01 · INPUT","02 · ТЕСТ ВХОДА":"02 · INPUT TEST","03 · РАБОТА СПЕЦИАЛИСТА":"03 · SPECIALIST WORK",
      "04 · ТЕСТ АРТЕФАКТА":"04 · ARTIFACT TEST","05 · ДОКАЗАТЕЛЬСТВА":"05 · EVIDENCE","06 · ЧЕЛОВЕЧЕСКИЙ ШЛЮЗ":"06 · HUMAN GATE",
      "ЭТАП 000 РАБОТАЕТ":"STAGE 000 ONLINE","Следующий этап закрыт до одобрения":"Next stage locked until approval",
      "ФАБРИКА · ЭТАП 000":"FACTORY · STAGE 000","Новая идея":"New idea","Запустить тест входа":"Run input test",
      "Этап":"Stage","Ответственный":"Owner","Состояние":"State","Следующий":"Next","Правила фабрики":"Factory rules",
      "Тест входа":"Input test","Тест артефакта":"Artifact test","Человеческий шлюз":"Human gate",
      "Запреты этапа 000":"Stage 000 prohibitions","Идея":"Idea","Анализ":"Analysis","Тесты":"Tests",
      "Инициализация проекта":"Project Initialization","КАРКАС ПРОЕКТА":"PROJECT CHASSIS","ЭТАП 001 РАБОТАЕТ":"STAGE 001 ONLINE",
      "Создание закрыто до одобрения":"Creation locked until approval","ФАБРИКА · ЭТАП 001":"FACTORY · STAGE 001",
      "Проверить предложение":"Validate proposal","ОДОБРИТЬ И ПОДГОТОВИТЬ СОЗДАНИЕ":"APPROVE & PREPARE CREATION",
      "Предусловие":"Prerequisite","Каркас":"Scaffold","Проверка":"Verification","Канонический каркас":"Canonical scaffold",
      "Правило":"Rule","Предложение":"Proposal","Выполнение":"Execution","Проверка выполнения":"Execution verification",
      "Инженерные роли":"Engineering Roles","ЦЕПОЧКА РОЛЕЙ":"ROLE PIPELINE","ЦЕПОЧКА":"PIPELINE",
      "СИСТЕМА РОЛЕЙ РАБОТАЕТ":"ROLE FABRIC ONLINE","ИНЖЕНЕРИЯ ИИ-СИСТЕМ":"AI SYSTEMS ENGINEERING",
      "Рабочее место специалиста":"Specialist Studio","РАБОЧАЯ ОБЛАСТЬ":"WORKSPACE","Входной пакет":"Input Package",
      "Основной редактор":"Main Editor","Профессиональная логика":"Professional Logic","Метрики":"Metrics","A/B-тестирование":"A/B Testing",
      "Передача":"Handoff","СПЕЦИАЛИСТ РАБОТАЕТ":"SPECIALIST ONLINE","Основное действие":"Primary Action","Качество":"Quality",
      "Студия трассируемости":"Traceability Studio","КАНОНИЧЕСКАЯ ИНЖЕНЕРНАЯ МОДЕЛЬ":"CANONICAL ENGINEERING MODEL",
      "ПРЕДСТАВЛЕНИЯ":"VIEWS","Цепочка требований":"Requirement Chain","Разрывы трассируемости":"Traceability Gaps",
      "Пути доказательств":"Evidence Paths","Ответственность":"Ownership","Граф трассируемости":"Traceability Graph",
      "Граф":"Graph","Матрица":"Matrix","Проблемы":"Issues","Выбранный узел":"Selected Node",
      "Инженер знаний и рассуждений":"Knowledge & Reasoning Engineer","ИНЖЕНЕРИЯ ИНТЕЛЛЕКТА":"INTELLIGENCE ENGINEERING",
      "Анализ ситуации":"Situation Analysis","Карта требований":"Requirements Map","Исследовательские вопросы":"Research Questions",
      "Заказы OSINT":"OSINT Orders","Модель компетенций":"Competency Model","Граф знаний":"Knowledge Graph",
      "Инженерия промптов":"Prompt Engineering","Инженерия RAG":"RAG Engineering","Инженерия знаний":"Knowledge Engineering",
      "Программа обучения":"Training Program","A/B и метрики":"A/B & Metrics","Приёмка":"Acceptance","Версионирование":"Versioning",
      "Студия архитектуры знаний":"Knowledge Architecture Studio","СЛОИ ЗНАНИЙ":"KNOWLEDGE LAYERS","Общая основа":"Common Foundation",
      "Корпоративная база":"Corporate Common","Ядро профессии":"Profession Core","Специализированная область":"Specialist Domain",
      "Получено через OSINT":"OSINT Acquired","Динамические / RAG":"Dynamic / RAG","Каталог знаний":"Knowledge Catalog",
      "Формирование навыка":"Skill Formation","A/B и качество":"A/B & Quality","Студия инженерии интеллекта":"Intelligence Engineering Studio",
      "РАБОЧИЙ ПРОЦЕСС":"WORKFLOW","Редактор артефакта":"Artifact Editor","Инженерная логика":"Engineering Logic",
      "Панель качества":"Quality Panel","Зависимости":"Dependencies","Статус доказательств":"Evidence Status"
    },
    de: {
      "Настройки":"Einstellungen","Язык интерфейса":"Oberflächensprache","Закрыть":"Schließen",
      "Инженерная фабрика ИИ":"KI-Engineering-Fabrik","РАБОЧИЕ ОБЛАСТИ":"ARBEITSBEREICHE","Конструктор агентов":"Agenten-Designer",
      "Процессы":"Workflows","Лаборатория моделей":"Modelllabor","RAG / Знания":"RAG / Wissen","Полигон":"Prüffeld",
      "Новая идея · STAGE 000":"Neue Idee · STAGE 000","Демо: идея → проект":"Demo: Idee → Projekt","Специалисты":"Spezialisten",
      "Трассируемость":"Rückverfolgbarkeit","Создать агента из шаблона":"Agent aus Vorlage erstellen","Проверить конструкцию":"Konstruktion prüfen",
      "Регистрация идеи":"Ideenerfassung","ФАЗЫ":"PHASEN","01 · ВХОД":"01 · EINGABE","02 · ТЕСТ ВХОДА":"02 · EINGABETEST",
      "03 · РАБОТА СПЕЦИАЛИСТА":"03 · FACHARBEIT","04 · ТЕСТ АРТЕФАКТА":"04 · ARTEFAKTTEST","05 · ДОКАЗАТЕЛЬСТВА":"05 · NACHWEISE",
      "06 · ЧЕЛОВЕЧЕСКИЙ ШЛЮЗ":"06 · MENSCHLICHES GATE","Инициализация проекта":"Projektinitialisierung","Каркас":"Gerüst",
      "Предложение":"Vorschlag","Выполнение":"Ausführung","Тесты":"Tests","Доказательства":"Nachweise","Шлюз":"Gate",
      "Инженерные роли":"Engineering-Rollen","Рабочее место специалиста":"Spezialisten-Studio","Метрики":"Metriken",
      "Студия трассируемости":"Traceability-Studio","Граф трассируемости":"Traceability-Graph",
      "Инженер знаний и рассуждений":"Wissens- und Reasoning-Ingenieur","Студия архитектуры знаний":"Wissensarchitektur-Studio"
    },
    fr: {
      "Настройки":"Paramètres","Язык интерфейса":"Langue de l’interface","Закрыть":"Fermer",
      "Инженерная фабрика ИИ":"Fabrique d’ingénierie IA","РАБОЧИЕ ОБЛАСТИ":"ESPACES DE TRAVAIL","Конструктор агентов":"Concepteur d’agents",
      "Процессы":"Flux de travail","Лаборатория моделей":"Laboratoire de modèles","RAG / Знания":"RAG / Connaissances","Полигон":"Polygone de test",
      "Новая идея · STAGE 000":"Nouvelle idée · STAGE 000","Демо: идея → проект":"Démo : idée → projet","Специалисты":"Spécialistes",
      "Трассируемость":"Traçabilité","Создать агента из шаблона":"Créer un agent depuis un modèle","Проверить конструкцию":"Valider la conception",
      "Регистрация идеи":"Saisie de l’idée","ФАЗЫ":"PHASES","01 · ВХОД":"01 · ENTRÉE","02 · ТЕСТ ВХОДА":"02 · TEST D’ENTRÉE",
      "03 · РАБОТА СПЕЦИАЛИСТА":"03 · TRAVAIL DU SPÉCIALISTE","04 · ТЕСТ АРТЕФАКТА":"04 · TEST D’ARTEFACT","05 · ДОКАЗАТЕЛЬСТВА":"05 · PREUVES",
      "06 · ЧЕЛОВЕЧЕСКИЙ ШЛЮЗ":"06 · GATE HUMAIN","Инициализация проекта":"Initialisation du projet","Каркас":"Structure",
      "Предложение":"Proposition","Выполнение":"Exécution","Тесты":"Tests","Доказательства":"Preuves","Шлюз":"Gate",
      "Инженерные роли":"Rôles d’ingénierie","Рабочее место специалиста":"Studio du spécialiste","Метрики":"Métriques",
      "Студия трассируемости":"Studio de traçabilité","Граф трассируемости":"Graphe de traçabilité",
      "Инженер знаний и рассуждений":"Ingénieur connaissances et raisonnement","Студия архитектуры знаний":"Studio d’architecture des connaissances"
    },
    es: {
      "Настройки":"Configuración","Язык интерфейса":"Idioma de la interfaz","Закрыть":"Cerrar",
      "Инженерная фабрика ИИ":"Fábrica de ingeniería de IA","РАБОЧИЕ ОБЛАСТИ":"ESPACIOS DE TRABAJO","Конструктор агентов":"Diseñador de agentes",
      "Процессы":"Flujos de trabajo","Лаборатория моделей":"Laboratorio de modelos","RAG / Знания":"RAG / Conocimiento","Полигон":"Polígono de pruebas",
      "Новая идея · STAGE 000":"Nueva idea · STAGE 000","Демо: идея → проект":"Demo: idea → proyecto","Специалисты":"Especialistas",
      "Трассируемость":"Trazabilidad","Создать агента из шаблона":"Crear agente desde plantilla","Проверить конструкцию":"Validar diseño",
      "Регистрация идеи":"Registro de idea","ФАЗЫ":"FASES","01 · ВХОД":"01 · ENTRADA","02 · ТЕСТ ВХОДА":"02 · PRUEBA DE ENTRADA",
      "03 · РАБОТА СПЕЦИАЛИСТА":"03 · TRABAJO DEL ESPECIALISTA","04 · ТЕСТ АРТЕФАКТА":"04 · PRUEBA DEL ARTEFACTO","05 · ДОКАЗАТЕЛЬСТВА":"05 · EVIDENCIAS",
      "06 · ЧЕЛОВЕЧЕСКИЙ ШЛЮЗ":"06 · GATE HUMANO","Инициализация проекта":"Inicialización del proyecto","Каркас":"Estructura",
      "Предложение":"Propuesta","Выполнение":"Ejecución","Тесты":"Pruebas","Доказательства":"Evidencias","Шлюз":"Gate",
      "Инженерные роли":"Roles de ingeniería","Рабочее место специалиста":"Estudio del especialista","Метрики":"Métricas",
      "Студия трассируемости":"Estudio de trazabilidad","Граф трассируемости":"Grafo de trazabilidad",
      "Инженер знаний и рассуждений":"Ingeniero de conocimiento y razonamiento","Студия архитектуры знаний":"Estudio de arquitectura del conocimiento"
    },
    "zh-CN": {
      "Настройки":"设置","Язык интерфейса":"界面语言","Закрыть":"关闭",
      "Инженерная фабрика ИИ":"AI 工程工厂","РАБОЧИЕ ОБЛАСТИ":"工作区","Конструктор агентов":"智能体设计器",
      "Процессы":"工作流","Лаборатория моделей":"模型实验室","RAG / Знания":"RAG / 知识","Полигон":"测试场",
      "Новая идея · STAGE 000":"新想法 · STAGE 000","Демо: идея → проект":"演示：想法 → 项目","Специалисты":"专家",
      "Трассируемость":"可追溯性","Создать агента из шаблона":"从模板创建智能体","Проверить конструкцию":"验证设计",
      "Регистрация идеи":"想法登记","ФАЗЫ":"阶段","01 · ВХОД":"01 · 输入","02 · ТЕСТ ВХОДА":"02 · 输入测试",
      "03 · РАБОТА СПЕЦИАЛИСТА":"03 · 专家工作","04 · ТЕСТ АРТЕФАКТА":"04 · 工件测试","05 · ДОКАЗАТЕЛЬСТВА":"05 · 证据",
      "06 · ЧЕЛОВЕЧЕСКИЙ ШЛЮЗ":"06 · 人工关卡","Инициализация проекта":"项目初始化","Каркас":"框架",
      "Предложение":"方案","Выполнение":"执行","Тесты":"测试","Доказательства":"证据","Шлюз":"关卡",
      "Инженерные роли":"工程角色","Рабочее место специалиста":"专家工作台","Метрики":"指标",
      "Студия трассируемости":"可追溯性工作室","Граф трассируемости":"可追溯图",
      "Инженер знаний и рассуждений":"知识与推理工程师","Студия архитектуры знаний":"知识架构工作室"
    }
  };

  const originalText = new WeakMap();
  const originalAttrs = new WeakMap();

  function currentLanguage(){
    return localStorage.getItem(STORAGE_KEY) || "ru";
  }

  function translate(source, lang){
    if(lang==="ru") return source;
    return (T[lang] && T[lang][source]) || source;
  }

  function translateNode(node, lang){
    if(node.nodeType===Node.TEXT_NODE){
      const raw=node.nodeValue;
      if(!raw || !raw.trim()) return;
      if(!originalText.has(node)) originalText.set(node, raw);
      const source=originalText.get(node);
      const trimmed=source.trim();
      const translated=translate(trimmed,lang);
      if(translated!==trimmed){
        const leading=source.match(/^\s*/)?.[0]||"";
        const trailing=source.match(/\s*$/)?.[0]||"";
        node.nodeValue=leading+translated+trailing;
      } else {
        node.nodeValue=source;
      }
      return;
    }
    if(node.nodeType!==Node.ELEMENT_NODE) return;
    if(["SCRIPT","STYLE","CODE","PRE"].includes(node.tagName)) return;

    if(!originalAttrs.has(node)){
      const attrs={};
      for(const name of ["placeholder","title","aria-label"]){
        if(node.hasAttribute(name)) attrs[name]=node.getAttribute(name);
      }
      originalAttrs.set(node,attrs);
    }
    const attrs=originalAttrs.get(node);
    for(const [name,source] of Object.entries(attrs)){
      node.setAttribute(name,translate(source,lang));
    }
    Array.from(node.childNodes).forEach(child=>translateNode(child,lang));
  }

  function applyLanguage(lang){
    if(!SUPPORTED.some(([id])=>id===lang)) lang="ru";
    localStorage.setItem(STORAGE_KEY,lang);
    document.documentElement.lang=lang;
    translateNode(document.body,lang);
    const select=document.getElementById("nexusLanguageSelect");
    if(select) select.value=lang;
  }

  function injectSettings(){
    if(document.getElementById("nexusLanguageSettings")) return;
    const root=document.createElement("div");
    root.id="nexusLanguageSettings";
    root.className="nexus-lang";
    root.innerHTML=
      '<button class="nexus-lang-toggle" id="nexusLangToggle" aria-label="Настройки">⚙</button>'+
      '<section class="nexus-lang-panel" id="nexusLangPanel" aria-hidden="true">'+
        '<header><b>Настройки</b><button id="nexusLangClose" aria-label="Закрыть">×</button></header>'+
        '<label>Язык интерфейса<select id="nexusLanguageSelect">'+
        SUPPORTED.map(([id,label])=>'<option value="'+id+'">'+label+'</option>').join("")+
        '</select></label>'+
        '<p>STAGE / ROLE / ID / YAML / JSON / пути не переводятся.</p>'+
      '</section>';
    document.body.appendChild(root);

    const panel=root.querySelector("#nexusLangPanel");
    root.querySelector("#nexusLangToggle").onclick=()=>{panel.classList.add("open");panel.setAttribute("aria-hidden","false");};
    root.querySelector("#nexusLangClose").onclick=()=>{panel.classList.remove("open");panel.setAttribute("aria-hidden","true");};
    root.querySelector("#nexusLanguageSelect").onchange=e=>applyLanguage(e.target.value);
  }

  function boot(){
    injectSettings();
    applyLanguage(currentLanguage());
    const observer=new MutationObserver(records=>{
      const lang=currentLanguage();
      for(const record of records){
        record.addedNodes.forEach(node=>translateNode(node,lang));
      }
    });
    observer.observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",boot);
  else boot();

  window.NEXUS_I18N={applyLanguage,currentLanguage,supported:SUPPORTED};
})();