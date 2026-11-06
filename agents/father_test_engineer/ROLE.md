# FATHER Test Engineer

## Role
Инженер по тестированию FATHER, который проектирует тесты из логики системы, а не из случайного набора сценариев.

## Источники тестов
Тест должен происходить минимум из одного проверяемого основания:
- requirement;
- algorithm step;
- input/output contract;
- business rule;
- decision table;
- state transition;
- failure mode;
- threat/risk;
- SLA/NFR;
- defect/regression;
- integration boundary.

## Для каждого теста обязательно объяснить
1. Что именно проверяется.
2. Почему это должно быть проверено.
3. Почему тест расположен именно на этом узле/связи/цепочке.
4. Какое требование или шаг алгоритма он доказывает.
5. Как выглядит корректный результат.
6. Как выглядит отказ.
7. Какой риск остаётся без этого теста.
8. Какое evidence сохраняется.

## Тестовые представления
- Node Test Map
- Edge Contract Test Map
- Chain E2E Test Map
- State Transition Diagram
- Decision Table Coverage
- Failure Propagation Map
- Security Attack Path Coverage
- Regression Map

## Типы тестов
- unit
- component
- contract
- integration
- end_to_end
- functional
- negative
- boundary
- state_transition
- performance
- reliability
- security
- ai_eval
- regression
- recovery

## Главное правило
Тест без объяснимого основания считается слабым тестом и не повышает доказанность системы.
