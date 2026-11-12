from father.core.model_router import ModelRouter, NoHealthyModel
from father.core.contracts import TraceContext


class HealthyModel:
    def __init__(self, name: str, result: str):
        self.name = name
        self.result = result

    def health(self) -> bool:
        return True

    def generate(self, prompt: str, trace: TraceContext) -> str:
        return self.result


class UnhealthyModel(HealthyModel):
    def health(self) -> bool:
        return False


class FailingModel(HealthyModel):
    def generate(self, prompt: str, trace: TraceContext) -> str:
        raise ConnectionError("provider down")


def test_router_skips_unhealthy_primary_and_uses_secondary():
    primary = UnhealthyModel("primary", "never")
    secondary = HealthyModel("secondary", "fallback-ok")
    router = ModelRouter(
        {"primary": primary, "secondary": secondary},
        default="primary",
        fallbacks=("secondary",),
    )

    model, output = router.generate("prompt", TraceContext())

    assert model.name == "secondary"
    assert output == "fallback-ok"


def test_router_fails_over_when_primary_generation_raises():
    primary = FailingModel("primary", "never")
    secondary = HealthyModel("secondary", "fallback-ok")
    router = ModelRouter(
        {"primary": primary, "secondary": secondary},
        default="primary",
        fallbacks=("secondary",),
    )

    model, output = router.generate("prompt", TraceContext())

    assert model.name == "secondary"
    assert output == "fallback-ok"


def test_explicit_requested_model_is_strict_and_does_not_fallback():
    primary = FailingModel("primary", "never")
    secondary = HealthyModel("secondary", "fallback-ok")
    router = ModelRouter(
        {"primary": primary, "secondary": secondary},
        default="primary",
        fallbacks=("secondary",),
    )

    try:
        router.generate("prompt", TraceContext(), requested="primary")
    except ConnectionError as exc:
        assert "provider down" in str(exc)
    else:
        raise AssertionError("explicit requested route unexpectedly fell back")


def test_router_raises_when_no_model_can_generate():
    primary = FailingModel("primary", "never")
    secondary = UnhealthyModel("secondary", "never")
    router = ModelRouter(
        {"primary": primary, "secondary": secondary},
        default="primary",
        fallbacks=("secondary",),
    )

    try:
        router.generate("prompt", TraceContext())
    except NoHealthyModel as exc:
        assert "no model could generate successfully" in str(exc)
    else:
        raise AssertionError("NoHealthyModel was not raised")
