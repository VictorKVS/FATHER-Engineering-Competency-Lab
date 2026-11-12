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

    def health(self) -> bool:
        """Composite readiness: at least one route can currently serve requests."""
        return any(self._healthy(model) for model in self._models.values())

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


    def generate(self, prompt: str, trace, requested: str | None = None):
        """Generate with runtime failover.

        Explicitly requested routes are strict: failure is returned to the caller.
        Default routing may move through configured fallbacks when a provider is
        unhealthy or generation fails at runtime.
        """
        if requested:
            model = self.resolve(requested)
            return model, model.generate(prompt, trace)

        candidates = (self.default,) + self.fallbacks + tuple(
            n for n in self._models if n not in {self.default, *self.fallbacks}
        )
        errors: list[str] = []
        for candidate in candidates:
            model = self._models[candidate]
            if not self._healthy(model):
                errors.append(f"{candidate}: unhealthy")
                continue
            try:
                return model, model.generate(prompt, trace)
            except Exception as exc:
                errors.append(f"{candidate}: {type(exc).__name__}: {exc}")
                continue

        raise NoHealthyModel("no model could generate successfully; " + " | ".join(errors))
