# FATHER Product Field v0.1

Первое главное поле фабрики.

## Концепция
На поле существует один продукт как живой инженерный объект.

Он:
- появляется при регистрации идеи;
- меняет цвет по статусу;
- показывает текущего специалиста и gate;
- показывает прогресс и evidence;
- по нажатию раскрывает Product Dossier.

## Status colors
- IDEA — neutral gray
- IN WORK — blue
- HOLD — amber
- PASS — green
- FAIL — red

Цвет имеет только инженерный смысл.

## Product Dossier
Tabs:
- Overview
- Documents
- Analysis
- Tests
- Evidence
- History

В следующих версиях документы будут открываться по реальным GitHub artifact refs, а специалисты — добавлять собственные overlay-разделы.

## Runtime hook
`window.setFatherProductState(state, stage, gate, progress)`

Example:
`setFatherProductState("pass","AG-001 ALINA","ANALYSIS READY",28)`

This is a UI prototype. It does not yet execute agents or load live GitHub artifacts.
