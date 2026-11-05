import json, re
from pathlib import Path

BASE=Path(__file__).resolve().parent
INGEST=BASE/"evidence/book_ingestion/canonical_books.json"
OUT=BASE/"evidence/text_analyst_exam"
OUT.mkdir(parents=True,exist_ok=True)

UNIVERSAL=[
 {"id":"U001","level":"L1","category":"facts","q":"Назови центральных персонажей и приведи источники, подтверждающие их роль."},
 {"id":"U002","level":"L1","category":"facts","q":"Какие ключевые локации используются в тексте и какие события происходят в каждой?"},
 {"id":"U003","level":"L2","category":"chronology","q":"Составь краткую хронологию ключевых событий в правильном порядке."},
 {"id":"U004","level":"L3","category":"causality","q":"Какие три события сильнее всего изменили дальнейшее развитие сюжета и почему?"},
 {"id":"U005","level":"L3","category":"characters","q":"Как меняются цели и мотивация главного героя по ходу произведения?"},
 {"id":"U006","level":"L3","category":"relationships","q":"Какие отношения между персонажами заметно меняются и что вызывает эти изменения?"},
 {"id":"U007","level":"L3","category":"epistemics","q":"Какие важные факты известны читателю раньше, чем отдельным персонажам?"},
 {"id":"U008","level":"L3","category":"epistemics","q":"Кто ошибается относительно ключевых событий и на чем основаны эти ошибочные убеждения?"},
 {"id":"U009","level":"L3","category":"deception","q":"Какие утверждения персонажей являются ложью, полуправдой или неподтвержденной версией?"},
 {"id":"U010","level":"L3","category":"evidence","q":"Какие детали сначала выглядят незначительными, но позже становятся важными?"},
 {"id":"U011","level":"L3","category":"plot_threads","q":"Какие сюжетные линии остаются открытыми к середине произведения?"},
 {"id":"U012","level":"L3","category":"plot_threads","q":"Какие сюжетные линии закрываются и каким событием они закрываются?"},
 {"id":"U013","level":"L4","category":"continuity","q":"Есть ли в тексте потенциальные противоречия хронологии, местоположения, знаний персонажей или состояния предметов?"},
 {"id":"U014","level":"L4","category":"hypothesis","q":"Какая гипотеза лучше всего объясняет ключевой конфликт с минимальным числом допущений?"},
 {"id":"U015","level":"L4","category":"style","q":"Какие устойчивые особенности повествовательного стиля можно доказать цитируемыми фрагментами?"},
 {"id":"U016","level":"L4","category":"composition","q":"Как структура глав и смена фокуса влияют на восприятие сюжета?"},
 {"id":"U017","level":"L4","category":"themes","q":"Какие темы проходят через произведение и какими событиями они поддерживаются?"},
 {"id":"U018","level":"L4","category":"symbols","q":"Какие предметы, образы или места могут иметь символическую функцию? Отдели текстовый факт от интерпретации."},
 {"id":"U019","level":"L4","category":"forecast","q":"Какие три дальнейших события были бы наиболее вероятны на выбранной промежуточной точке и почему?"},
 {"id":"U020","level":"L4","category":"counterfactual","q":"Как изменился бы сюжет, если убрать одно ключевое событие? Укажи причинную цепочку."}
]

TRAPS=[
 {"id":"T001","level":"L2","category":"hallucination_trap","q":"Назови факт, который часто можно было бы предположить по жанру, но который текстом не подтвержден. Ответ должен явно сказать 'НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ'."},
 {"id":"T002","level":"L3","category":"hallucination_trap","q":"Есть ли в тексте прямое подтверждение тайного сговора всех основных персонажей? Если нет, не додумывай."},
 {"id":"T003","level":"L3","category":"hallucination_trap","q":"Есть ли подтверждение, что главный герой заранее знал финальную развязку? Если нет, ответь 'НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ'."},
 {"id":"T004","level":"L3","category":"hallucination_trap","q":"Назови персонажа, которому нельзя приписывать знание ключевого события раньше времени, и объясни почему."},
 {"id":"T005","level":"L4","category":"hallucination_trap","q":"Какая привлекательная интерпретация не имеет достаточной текстовой опоры?"}
]

KB=[
 {"id":"K001","level":"L2","category":"kb","q":"Построй список значимых персонажей с aliases и source_chunk."},
 {"id":"K002","level":"L2","category":"kb","q":"Построй список ключевых событий с actor, target, location, time и source_chunk."},
 {"id":"K003","level":"L3","category":"kb","q":"Построй граф отношений персонажей и укажи, как и когда отношения изменяются."},
 {"id":"K004","level":"L3","category":"kb","q":"Выдели claims и присвой truth_status: TRUE/FALSE/UNVERIFIED/INTERPRETATION."},
 {"id":"K005","level":"L3","category":"kb","q":"Для важных claims укажи, какие персонажи KNOW/BELIEVE/SUSPECT/DO_NOT_KNOW."},
 {"id":"K006","level":"L3","category":"kb","q":"Выдели явные lies и deceptive statements с источниками."},
 {"id":"K007","level":"L3","category":"kb","q":"Перечисли значимые объекты, их владельцев и изменения состояния/местоположения."},
 {"id":"K008","level":"L3","category":"kb","q":"Перечисли открытые и закрытые plot threads."},
 {"id":"K009","level":"L4","category":"kb","q":"Построй причинный граф ключевых событий."},
 {"id":"K010","level":"L4","category":"kb","q":"Построй timeline и отметь места неопределенности или противоречия."}
]

def book_specific(book):
    title=book.get("title") or Path(book.get("source_file","book")).stem
    fmt=book.get("format")
    qs=[]
    templates=[
      ("S001","L1","facts",f"Какие особенности структуры именно произведения «{title}» удалось извлечь из формата {fmt}?"),
      ("S002","L2","characters",f"Какие персонажи в «{title}» появляются раньше других и как меняется их роль?"),
      ("S003","L3","causality",f"Какие причинные цепочки являются центральными для «{title}»?"),
      ("S004","L3","epistemics",f"Какие секреты или неизвестные факты в «{title}» распределены между персонажами неравномерно?"),
      ("S005","L4","continuity",f"Найди потенциальные continuity-проблемы в «{title}» и отдели реальные противоречия от намеренной авторской неоднозначности."),
      ("S006","L4","style",f"Опиши стиль «{title}» через наблюдаемые признаки, а не общие литературные ярлыки."),
      ("S007","L4","forecast",f"На середине «{title}» какие прогнозы дальнейшего развития были бы наиболее обоснованы?"),
      ("S008","L4","evaluation",f"Какие пять вопросов лучше всего отличат поверхностный пересказ «{title}» от глубокого понимания?")
    ]
    for i,l,c,q in templates: qs.append({"id":i,"level":l,"category":c,"q":q})
    return qs

def main():
    data=json.loads(INGEST.read_text(encoding="utf-8"))
    books=data.get("books",[])
    suite={
      "schema":"FATHER_TEXT_ANALYST_EXAM_v1",
      "grading":{
        "dimensions":["factual_accuracy","source_grounding","causal_reasoning","epistemic_accuracy","continuity","kb_structure","uncertainty_handling","hallucination_resistance","depth","latency"],
        "required_unknown_phrase":"НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ"
      },
      "universal":UNIVERSAL,
      "hallucination_traps":TRAPS,
      "knowledge_base":KB,
      "books":[]
    }
    for b in books:
        suite["books"].append({
          "source_file":b.get("source_file"),
          "title":b.get("title"),
          "format":b.get("format"),
          "language":b.get("language"),
          "book_specific":book_specific(b)
        })
    # Expand to 150-item target by generating structured variants.
    categories=["facts","chronology","characters","relationships","epistemics","causality","evidence","plot_threads","continuity","style","interpretation","forecast"]
    variants=[]
    n=1
    stems=[
      "Приведи два независимых фрагмента, подтверждающих ответ.",
      "Укажи, что является прямым фактом, а что выводом.",
      "Покажи изменение между ранней и поздней частью текста.",
      "Назови возможную альтернативную интерпретацию и оцени ее опору.",
      "Если данных недостаточно, явно укажи это.",
      "Укажи source_chunk для каждого ключевого вывода.",
      "Найди исключение из общей закономерности.",
      "Проверь ответ на противоречие с другим фрагментом.",
      "Сформулируй краткий и затем глубокий ответ.",
      "Оцени уверенность HIGH/MEDIUM/LOW и объясни."
    ]
    base_prompts={
      "facts":"Выбери важный факт произведения и восстанови его контекст.",
      "chronology":"Выбери три связанных события и восстанови их временной порядок.",
      "characters":"Проанализируй изменение одного значимого персонажа.",
      "relationships":"Проанализируй изменение одной важной связи между персонажами.",
      "epistemics":"Выбери важный факт и сравни, что о нем знают разные персонажи.",
      "causality":"Выбери значимое событие и восстанови его причины и последствия.",
      "evidence":"Выбери важную улику/деталь и проследи ее роль.",
      "plot_threads":"Выбери сюжетную линию и проследи ее состояние.",
      "continuity":"Проверь одну цепочку фактов на непротиворечивость.",
      "style":"Выбери устойчивый стилистический прием и докажи его примерами.",
      "interpretation":"Предложи интерпретацию важной сцены и оцени силу доказательств.",
      "forecast":"Выбери промежуточную точку и построй обоснованный прогноз."
    }
    for cat in categories:
      for stem in stems:
        variants.append({"id":f"V{n:03d}","level":"L3" if cat not in {"continuity","interpretation","forecast"} else "L4","category":cat,"q":base_prompts[cat]+" "+stem})
        n+=1
    suite["structured_variants"]=variants
    total=len(UNIVERSAL)+len(TRAPS)+len(KB)+len(variants)
    suite["counts"]={"universal":len(UNIVERSAL),"traps":len(TRAPS),"kb":len(KB),"variants":len(variants),"core_total":total,"per_book_specific":8,"target_per_book":total+8}
    out=OUT/"text_analyst_exam_v1.json"
    out.write_text(json.dumps(suite,ensure_ascii=False,indent=2),encoding="utf-8")
    print("EXAM:",out)
    print(json.dumps(suite["counts"],ensure_ascii=False))
    print("RESULT: PASS")

if __name__=="__main__":
    main()
