"""
Core reasoning engine.

Uses:
- Local slot extraction
- Local SentenceTransformer RAG
- Local Ollama LLM

No OpenAI API key is required.
"""

import json

import ollama

from app.models import (
    ChatRequest,
    ChatResponse,
    Recommendation,
)
from app.chat import session as session_store
from app.chat.extractor import extract_slots
from app.knowledge.retriever import retrieve


ENV_VARIABLE_KEYS = [
    "soil_organic_carbon_pct",
    "soil_ph",
    "rainfall",
    "land_use_type",
    "crop",
    "temperature",
    "pollution_level",
    "deforestation_rate",
]

MIN_VARIABLES_REQUIRED = 3


CLARIFYING_CATEGORIES = {
    "soil": (
        "soil_organic_carbon_pct",
        "soil organic carbon % "
        "(or a rough sense: low/medium/high)",
    ),
    "climate": (
        "rainfall",
        "rainfall pattern "
        "(low/medium/high, or mm/year)",
    ),
    "land_use": (
        "land_use_type",
        "current land use / crop type "
        "(e.g. monoculture wheat, agroforestry)",
    ),
    "human_impact": (
        "pollution_level",
        "any pollution, pesticide use, "
        "or deforestation nearby",
    ),
}


def _category_of(key: str) -> str:
    mapping = {
        "soil_organic_carbon_pct": "soil",
        "soil_ph": "soil",
        "rainfall": "climate",
        "temperature": "climate",
        "land_use_type": "land_use",
        "crop": "land_use",
        "pollution_level": "human_impact",
        "deforestation_rate": "human_impact",
    }

    return mapping.get(key, "other")


def _missing_categories(slots: dict) -> list:
    missing = []

    for category, (_key, _desc) in CLARIFYING_CATEGORIES.items():

        has_any = any(
            slots.get(k)
            for k in ENV_VARIABLE_KEYS
            if _category_of(k) == category
        )

        if not has_any:
            missing.append(category)

    return missing


def _count_known_variables(slots: dict) -> int:
    return sum(
        1
        for key in ENV_VARIABLE_KEYS
        if slots.get(key)
    )


def _build_clarifying_question(slots: dict) -> str:
    missing = _missing_categories(slots)

    have_count = _count_known_variables(slots)

    needed = MIN_VARIABLES_REQUIRED - have_count

    asks = [
        CLARIFYING_CATEGORIES[c][1]
        for c in missing[:max(needed, 1)]
    ]

    return (
        f"I have {have_count} environmental variable(s) so far. "
        "To give you a grounded, multi-metric recommendation "
        "(not generic advice), could you also share: "
        + "; ".join(asks)
        + "?"
    )


def _slots_description(slots: dict) -> str:
    parts = [
        f"{key}: {value}"
        for key, value in slots.items()
        if value is not None
    ]

    return (
        "; ".join(parts)
        if parts
        else "no structured data yet"
    )


SYSTEM_PROMPT = """
You are an AI environmental scientist for Darukaa.Earth.

You must give evidence-grounded recommendations about
biodiversity, land health, agriculture and environmental
conditions.

IMPORTANT RULES:

1. Use ONLY the supplied knowledge context for factual claims.
2. Do not invent statistics.
3. Give 2-4 practical recommendations.
4. Each recommendation must connect at least two environmental
   variables.
5. Explain the mechanism connecting the variables.
6. Cite the provided source label.
7. Return ONLY valid JSON.

Required JSON format:

{
  "summary": "1-3 sentence summary",
  "recommendations": [
    {
      "action": "specific action",
      "reasoning": "explanation connecting at least two variables",
      "impacted_metrics": ["metric1", "metric2"],
      "estimated_improvement": null,
      "time_horizon": "short",
      "confidence": "medium",
      "reference": "source label"
    }
  ]
}
"""


def _generate_recommendations(
    slots: dict,
    message: str,
    history_block: str,
    context_block: str,
):
    user_prompt = f"""
Known environmental variables:

{_slots_description(slots)}

Recent conversation:

{history_block}

User's latest message:

{message}

Knowledge context:

{context_block}

Generate the required JSON response.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        options={
            "temperature": 0.3,
        },
    )

    content = response["message"]["content"]

    # Remove accidental markdown fences
    content = content.strip()

    if content.startswith("```"):
        content = content.replace(
            "```json",
            "",
            1,
        )

        content = content.replace(
            "```",
            "",
        )

        content = content.strip()

    return json.loads(content)


def handle_message(req: ChatRequest) -> ChatResponse:

    session_store.add_turn(
        req.session_id,
        "user",
        req.message,
    )

    explicit_slots = (
        req.structured_input.model_dump(
            exclude_none=True
        )
        if req.structured_input
        else {}
    )

    extracted_slots = extract_slots(
        req.message
    )

    merged_new = {
        **extracted_slots,
        **explicit_slots,
    }

    slots = session_store.update_slots(
        req.session_id,
        merged_new,
    )

    known_count = _count_known_variables(slots)

    if known_count < MIN_VARIABLES_REQUIRED:

        question = _build_clarifying_question(
            slots
        )

        session_store.add_turn(
            req.session_id,
            "assistant",
            question,
        )

        return ChatResponse(
            session_id=req.session_id,
            reply_type="clarifying_question",
            message=question,
            follow_up_question=question,
            known_variables=slots,
            recommendations=[],
            sources=[],
        )

    retrieval_query = (
        f"{req.message} | "
        f"known variables: "
        f"{_slots_description(slots)}"
    )

    sources = retrieve(
        retrieval_query,
        k=6,
    )

    context_block = "\n\n".join(
        f"[{source.source}] {source.text}"
        for source in sources
    )

    history = session_store.get_session(
        req.session_id
    )["history"]

    history_block = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history[-6:]
    )

    try:
        parsed = _generate_recommendations(
            slots=slots,
            message=req.message,
            history_block=history_block,
            context_block=context_block,
        )

    except Exception as error:

        print(
            "Local LLM generation error:",
            error,
        )

        fallback = (
            "I found enough environmental information "
            "to analyze the situation, but the local AI "
            "model could not generate the recommendation. "
            "Please make sure Ollama is running and "
            "llama3.2:3b is installed."
        )

        session_store.add_turn(
            req.session_id,
            "assistant",
            fallback,
        )

        return ChatResponse(
            session_id=req.session_id,
            reply_type="recommendation",
            message=fallback,
            follow_up_question=None,
            known_variables=slots,
            recommendations=[],
            sources=sources,
        )

    recommendations = [
        Recommendation(**recommendation)
        for recommendation
        in parsed.get(
            "recommendations",
            [],
        )
    ]

    summary = parsed.get(
        "summary",
        "",
    )

    session_store.add_turn(
        req.session_id,
        "assistant",
        summary,
    )

    return ChatResponse(
        session_id=req.session_id,
        reply_type="recommendation",
        message=summary,
        follow_up_question=None,
        known_variables=slots,
        recommendations=recommendations,
        sources=sources,
    )