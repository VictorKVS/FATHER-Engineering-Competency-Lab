# FATHER Narrative Intelligence — MVP-01

Минимальный рабочий проект базы знаний для рассказа.

## Что доказывает
- рассказ хранится как отдельный проект;
- сцены, персонажи, события, объекты, claims, statements и plot threads разделены;
- ground truth отделён от того, что персонажи знают/думают;
- можно отвечать на вопросы "кто знает?", "во что верит?", "кто солгал?", "где предмет?", "какие сюжетные линии открыты?";
- knowledge violation проверяется детерминированно.

## Тестовый рассказ
`narrative_demo/demo_story.md`

## Структурированная фикстура
`narrative_demo/demo_story_fixture.json`

На MVP-01 фикстура создаётся вручную специально: мы проверяем модель данных и запросы независимо от качества LLM-extraction.

## Запуск
```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_NARRATIVE_MVP01.ps1
```

Runtime DB:
`narrative_demo/demo_story.db`

Evidence:
`evidence/narrative_demo_mvp01.json`

## Следующий этап
MVP-02: LLM extractor получает обычный .txt/.md рассказ и автоматически предлагает entities/events/claims/perspectives в режиме propose → validate → commit.
