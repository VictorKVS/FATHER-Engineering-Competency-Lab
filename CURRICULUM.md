# FATHER-TRAIN-0001 — Curriculum

## Goal

Build measurable engineering competence by repeating complete game-development exercises from simple to complex, first with Python, then C++, then Go-oriented game/simulation/networking work.

The books are references and control sources. We do not mirror copyrighted book files into this repository unless their license explicitly permits it.

## Track A — Python game engineering

### Beginner
1. Michael Dawson — *Python Programming for the Absolute Beginner* / Russian editions commonly titled «Программируем на Python».
2. Jason R. Briggs — *Python for Kids: A Playful Introduction to Programming*.
3. Al Sweigart — *Invent Your Own Computer Games with Python*.
4. Eric Matthes — *Python Crash Course* — project section with the Alien Invasion game.
5. Kenlon / Weichler — introductory first-game material from the user-provided candidate list; verify exact bibliographic edition before use.

### Intermediate
6. Craig Richardson — *Adventures in Python*.
7. Bryson Payne — *Teach Your Kids to Code*.
8. Lee Vaughan — *Impractical Python Projects*.
9. Al Sweigart — game-oriented Python/Pygame material; verify exact Russian/English edition before use.
10. *Game Development Projects with Python* — candidate from the initial list; verify exact author/title/edition before adoption.

### Advanced candidates
11. *Python Game Programming By Example* — verify exact edition/authors before adoption.
12. *Learning Python Game Development* — verify exact edition/authors before adoption.
13. Panda3D game-development material — select a current, reproducible edition/tutorial track.
14. Python game-AI material — select a current, reproducible source.
15. Python/OpenGL real-time rendering material — select a current, reproducible source.

> Items marked “verify” are retained as curriculum candidates, not yet asserted as validated bibliography.

## Track B — C++ game engineering

Purpose: repeat the same engineering loop under stricter resource, build, performance, architecture and tooling constraints.

Candidate progression:

1. General C++ problem-solving warm-up.
2. Small 2D game project in C++.
3. A book-led complete game project.
4. Engine-oriented architecture and resource management.
5. Unreal/C++ or lower-level framework project only after the fundamentals are measurable.

A strong candidate for the practical track is *Beginning C++ Game Programming*; current Packt catalog still lists a 2024 edition. The exact edition and source code will be evidence-checked before it becomes the canonical C++ course.

## Track C — Go game / simulation / networking engineering

Go is not selected to imitate the C++/AAA path. The training value is different: simple deployment, concurrency, networking, deterministic server logic, simulation services and multiplayer backends.

Candidate progression:

1. Small terminal simulation/game loop.
2. 2D game using the current Ebitengine ecosystem.
3. Deterministic simulation and replay.
4. Client/server multiplayer exercise.
5. Authoritative game server / matchmaking / telemetry service.
6. Load, race, failure and network tests.

The exact Go book list is not frozen yet. We will prefer current sources with reproducible source code and supplement them with official Ebitengine/Go documentation when a book becomes obsolete.

## Standard experiment loop

For every chapter or exercise:

1. `SOURCE` — record book/reference, edition, chapter and allowed use.
2. `LESSON` — extract the learning objective without copying the full source.
3. `REQ` — Analyst writes measurable requirements.
4. `ARCH` — Architect proposes components/interfaces and trade-offs.
5. `TEST` — QA defines acceptance tests before implementation.
6. `CODE` — Programmer implements.
7. `REVIEW` — Reviewer/Critic records findings.
8. `SEC` — security/dependency/input checks appropriate to the exercise.
9. `BUILD` — clean build/run evidence.
10. `COMPARE` — compare our result with the reference solution where legally and practically available.
11. `DEFECT` — classify defects and escaped defects.
12. `LESSON-LEARNED` — capture reusable patterns and repeated mistakes.
13. `COMPETENCY` — update specialist metrics only from evidence.

## Promotion principle

Completing a chapter does not automatically raise a specialist level. Promotion requires repeated evidence across independent tasks and later transfer to a real MVP outside the game-training domain.
