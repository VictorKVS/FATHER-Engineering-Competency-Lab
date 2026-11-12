from father.adapters.models import GroundedTemplateModel, OpenAICompatibleModel


def test_grounded_template_health_is_always_true():
    model = GroundedTemplateModel()
    assert model.health() is True


def test_openai_compatible_health_returns_false_for_unreachable_endpoint():
    model = OpenAICompatibleModel(
        "http://127.0.0.1:9/v1",
        "unreachable-test-model",
    )
    assert model.health() is False
