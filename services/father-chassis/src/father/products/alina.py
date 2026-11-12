from dataclasses import dataclass, field

@dataclass
class CharacterState:
    character_id: str
    attributes: dict = field(default_factory=dict)

@dataclass
class SceneState:
    scene_id: str
    events: list[dict] = field(default_factory=list)
    characters: list[str] = field(default_factory=list)
    location: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

@dataclass
class Forecast:
    hypothesis: str
    probability: float
    evidence_ids: list[str]

class AlinaNarrativePack:
    """Domain pack only. Chassis services remain shared."""
    def extract_scene(self, scene_id: str, payload: dict) -> SceneState:
        return SceneState(
            scene_id=scene_id,
            events=list(payload.get("events", [])),
            characters=list(payload.get("characters", [])),
            location=payload.get("location"),
            evidence_ids=list(payload.get("evidence_ids", [])),
        )

    def forecast(self, scene: SceneState) -> Forecast:
        p = 0.5 + min(0.4, len(scene.events) * 0.05)
        return Forecast(
            hypothesis=f"Next event is conditioned by {len(scene.events)} known event(s)",
            probability=round(p, 2),
            evidence_ids=scene.evidence_ids,
        )

    def backtest(self, forecast: Forecast, known_future: str) -> dict:
        hit = bool(known_future and forecast.hypothesis)
        return {
            "hit": hit,
            "forecast": forecast.hypothesis,
            "known_future": known_future,
            "score": 1.0 if hit else 0.0,
        }
