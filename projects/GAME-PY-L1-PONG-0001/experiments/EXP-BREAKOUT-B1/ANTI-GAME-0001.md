# `ANTI-GAME-0001` — Unbounded discrete-overlap collision

## Passport

- **What:** record the failure mode where a moving object is considered colliding only when its final position overlaps another object.
- **Why:** at high speed or after a delayed frame, the object can cross a wall, paddle or brick without overlapping it at the sampled endpoint.
- **Alternatives:** ignore tunnelling; cap timestep; subdivide motion; continuous swept collision.
- **Decision:** for small L1 games cap timestep and test declared speed bounds; require substeps or swept collision when those bounds are exceeded.
- **Why chosen:** it preserves a simple deterministic core without pretending the algorithm is valid for arbitrary velocities.
- **Constraints:** the timestep cap is a mitigation, not a proof for all shapes and speeds.
- **Risks:** hidden speed/content changes can invalidate the bound; collision ordering can still produce ambiguous multi-hit results.
- **Evidence:** `REV-PY-PONG-0001`, Pong timestep cap, future Breakout transfer trials.
- **Version/status:** 0.1.0 / proposed, not golden.
- **Links:** `PAT-GAME-0001`, `ARCH-PY-PONG-0001`, `XFER-PY-PONG-0001`.
- **Result:** treatment agents must state the valid motion bound or select a stronger collision strategy.
