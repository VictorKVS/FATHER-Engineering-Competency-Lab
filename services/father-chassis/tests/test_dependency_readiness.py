from father.bootstrap import build_runtime
from father.core.health import health_report


class HealthyState:
    def health(self) -> bool:
        return True

    def set(self, namespace, key, value):
        pass

    def get(self, namespace, key, default=None):
        return default

    def snapshot(self, namespace):
        return {}


class ToggleEventBus:
    def __init__(self, healthy: bool):
        self.healthy = healthy

    def health(self) -> bool:
        return self.healthy

    def publish(self, event):
        pass


class Model:
    def __init__(self, name: str, healthy: bool):
        self.name = name
        self._healthy = healthy

    def health(self) -> bool:
        return self._healthy

    def generate(self, prompt, trace):
        return self.name


def test_active_event_bus_participates_in_readiness():
    bus = ToggleEventBus(healthy=False)
    runtime = build_runtime(
        state=HealthyState(),
        event_bus=bus,
    )

    report = health_report(runtime.registry, runtime.emergency_stop)

    assert report.ready is False
    assert report.blocks["FTH-EVENT-BUS-001"] is False


def test_model_router_ready_when_primary_down_but_fallback_healthy():
    primary = Model("primary", healthy=False)
    secondary = Model("secondary", healthy=True)
    runtime = build_runtime(
        primary_model=primary,
        secondary_model=secondary,
    )

    report = health_report(runtime.registry, runtime.emergency_stop)

    assert report.blocks["FTH-MODEL-ROUTER-001"] is True
    assert report.ready is True


def test_model_router_not_ready_when_all_models_down():
    primary = Model("primary", healthy=False)
    secondary = Model("secondary", healthy=False)
    runtime = build_runtime(
        primary_model=primary,
        secondary_model=secondary,
    )

    report = health_report(runtime.registry, runtime.emergency_stop)

    assert report.blocks["FTH-MODEL-ROUTER-001"] is False
    assert report.ready is False
