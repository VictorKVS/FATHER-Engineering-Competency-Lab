from __future__ import annotations

from .contracts import ModelAdapter


class NoHealthyModel(RuntimeError):
    pass


class ModelRouter:
    def __init__(self, models: dict[str, ModelAdapter], default: str, fallbacks: tuple[str, ...] = ()) -> None:
        if default not in models:
            raise ValueError(f"default model {default!r} is not registered")
        self._models = dict(models)
        self.default = default
        self.fallbacks = tuple(fallbacks)

    def _healthy(self, model: ModelAdapter) -> bool:
        checker = getattr(model, "health", None)
        return bool(checker()) if callable(checker) else True

    def resolve(self, requested: str | None = None) -> ModelAdapter:
        name = requested or self.default
        if requested:
            try:
                model = self._models[name]
            except KeyError as exc:
                raise KeyError(f"unknown model route: {name}") from exc
            if not self._healthy(model):
                raise NoHealthyModel(f"requested model is unhealthy: {name}")
            return model

        candidates = (self.default,) + self.fallbacks + tuple(n for n in self._models if n not in {self.default,*self.fallbacks})
        for candidate in candidates:
            model = self._models[candidate]
            if self._healthy(model):
                return model
        raise NoHealthyModel("no healthy model is available")
