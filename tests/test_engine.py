"""Tests the slot-filling -> clarifying-question -> grounded-recommendation
flow with the OpenAI and Chroma calls mocked out, so this runs offline with
no API key or vector DB needed."""
import json
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used-in-this-test")

from app.models import ChatRequest, RetrievedSource  # noqa: E402


def _fake_completion(json_payload: dict):
    """Builds a MagicMock that mimics the shape of an OpenAI chat completion
    response with response_format=json_object."""
    mock = MagicMock()
    mock.choices = [MagicMock(message=MagicMock(content=json.dumps(json_payload)))]
    return mock


@patch("app.chat.extractor._client")
def test_asks_clarifying_question_when_few_variables_known(mock_extractor_client):
    from app.chat.engine import handle_message

    # extractor pulls out only one variable from the message
    mock_extractor_client.chat.completions.create.return_value = _fake_completion(
        {"rainfall": "low"}
    )

    req = ChatRequest(session_id="test-session-1", message="Rainfall has been low lately.")
    response = handle_message(req)

    assert response.reply_type == "clarifying_question"
    assert response.follow_up_question is not None
    assert response.recommendations == []


@patch("app.knowledge.retriever.retrieve")
@patch("app.chat.engine._client")
@patch("app.chat.extractor._client")
def test_generates_grounded_recommendation_when_enough_variables_known(
    mock_extractor_client, mock_engine_client, mock_retrieve
):
    from app.chat.engine import handle_message

    mock_extractor_client.chat.completions.create.return_value = _fake_completion({})

    mock_retrieve.return_value = [
        RetrievedSource(
            text="Legume cover crops increase SOC by 15-25% over 2-3 years.",
            source="soil_health — FAO conservation agriculture studies",
            score=0.9,
        )
    ]

    mock_engine_client.chat.completions.create.return_value = _fake_completion(
        {
            "summary": "Low SOC and monoculture wheat are compounding biodiversity decline.",
            "recommendations": [
                {
                    "action": "Introduce legume-based cover crops",
                    "reasoning": "Connects soil organic carbon and land-use monoculture.",
                    "impacted_metrics": ["soil_organic_carbon", "biodiversity_index"],
                    "estimated_improvement": "15-25% SOC increase over 2-3 years",
                    "time_horizon": "medium",
                    "confidence": "medium",
                    "reference": "soil_health — FAO conservation agriculture studies",
                }
            ],
        }
    )

    req = ChatRequest(
        session_id="test-session-2",
        message="Biodiversity is declining on my land.",
        structured_input={
            "soil_organic_carbon_pct": 0.3,
            "rainfall": "low",
            "land_use_type": "monoculture wheat",
        },
    )
    response = handle_message(req)

    assert response.reply_type == "recommendation"
    assert len(response.recommendations) == 1
    rec = response.recommendations[0]
    assert "soil_organic_carbon" in rec.impacted_metrics
    assert rec.reference.startswith("soil_health")
    assert len(response.sources) == 1
