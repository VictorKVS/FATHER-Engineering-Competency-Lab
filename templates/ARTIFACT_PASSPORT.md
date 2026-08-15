# Artifact Passport Template

Every meaningful course artifact must begin with or link to a passport built from this structure.

## Identity

- Artifact ID: `TYPE-TRACK-LXX-NNN`
- Artifact type:
- Lesson ID:
- Track: `PY / CPP / GO / OTHER`
- Version:
- Status: `DRAFT / REVIEW / ACCEPTED / SUPERSEDED`
- Owner role:
- Reviewers:
- Date created:
- Last reviewed:

## Problem and context

### What problem is this artifact solving?

Describe the concrete problem in plain language.

### Why is this needed now?

Explain why the decision or artifact is necessary at this stage of the lesson.

### Inputs

List source chapter, analyst brief, requirements, architecture constraints, security findings, previous patterns or other evidence used.

## Decision

### What was decided?

State the decision precisely.

### Why was this option selected?

Explain the reasoning. Avoid statements such as "because it is easier" unless the specific engineering meaning of easier is described.

## Alternatives considered

For every meaningful alternative record:

### Alternative A
- Description:
- Advantages:
- Disadvantages:
- Risks:
- Why rejected / deferred:

### Alternative B
- Description:
- Advantages:
- Disadvantages:
- Risks:
- Why rejected / deferred:

Add alternatives as needed. If no meaningful alternative exists, explain why.

## Constraints and assumptions

- Technical constraints:
- Educational constraints:
- Time / complexity constraints:
- Security constraints:
- Assumptions:

## Trade-offs

Record what was deliberately gained and what was deliberately sacrificed: simplicity vs extensibility, speed vs abstraction, memory vs readability, security vs convenience, testability vs direct coupling, and so on.

## Architecture impact

- Components affected:
- Interfaces affected:
- Data/state affected:
- New dependencies:
- Architectural debt introduced:
- ADR reference if applicable:

## Security impact

- Trust boundaries affected:
- Inputs / untrusted data:
- Secrets:
- File/network access:
- Dependency risk:
- Abuse/failure cases:
- Required security tests:

If the artifact has no meaningful security impact, record the reasoning instead of writing only `N/A`.

## Test and evidence plan

- What must be tested?
- What observable result proves success?
- Negative tests:
- Reproducibility evidence:
- Expected evidence files / logs / screenshots / test reports:

## Result

### What actually happened?

Record the implemented or observed outcome.

### Deviations from the decision

Describe any implementation deviation and why it occurred.

### Defects discovered

Link `DEF-*` items.

### Review findings

Link `REV-*`, `SEC-*`, `TEST-*` or other findings.

## Comparison with reference

Where a book/reference solution exists:

- What is the reference approach?
- What is different in our approach?
- Which is simpler?
- Which is more maintainable?
- Which assumptions differ?
- What did the reference teach us?
- What would we keep from our own solution?

## Lessons learned

- What should be repeated?
- What should be avoided?
- What surprised us?
- What knowledge was missing?
- What should be added to a checklist?
- What should become a reusable pattern?

## Reuse and knowledge extraction

- Candidate pattern ID: `PAT-*`
- Candidate anti-pattern ID: `ANTI-*`
- Related lessons:
- Applicable contexts:
- Non-applicable contexts:

## Promotion decision

- Evidence sufficient: `YES / PARTIAL / NO`
- Artifact accepted: `YES / NO`
- Competence signal produced:
- Follow-up action:

---

**Core rule:** an artifact passport must preserve the reasoning path, not merely the final answer. Future agents should be able to understand what was known at the time, what options existed, why one path was chosen, what failed and what evidence justified the result.
