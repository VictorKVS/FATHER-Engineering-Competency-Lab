# Test Rationale Views

В редакторе тест должен быть виден не только списком.

## 1. Test-on-Node
Выбор узла показывает:
- implemented programs;
- linked requirements;
- algorithm steps;
- attached tests;
- coverage;
- failed tests;
- evidence.

## 2. Test-on-Edge
Выбор связи показывает:
- producer/consumer;
- schema;
- auth;
- latency;
- retry;
- error contract;
- corresponding contract tests.

## 3. Test-on-Chain
Выбор цепочки показывает:

Requirement
→ Algorithm
→ Node A
→ Flow
→ Node B
→ Flow
→ Node C
→ Outcome

Под каждым элементом:
- tests;
- metrics;
- evidence;
- risk coverage.

## 4. Why this test?
По клику на тест открывается Explain panel:

WHY TEST EXISTS
→ source requirement
→ algorithm step
→ contract
→ risk/failure mode
→ expected behavior
→ PASS/FAIL oracle

Это обязательная функция FATHER Test Engineering.
