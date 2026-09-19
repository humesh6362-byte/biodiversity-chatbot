"""
Extract structured environmental variables from a user message
without using OpenAI.

Uses simple local rule-based extraction so no API key is required.
"""

import re

from app.models import StructuredInput


def extract_slots(message: str) -> dict:
    text = message.lower()
    data = {}

    # Rainfall
    rainfall_match = re.search(
        r"rainfall\s*(?:is|of|around)?\s*(\d+(?:\.\d+)?)\s*(mm|cm)?",
        text,
    )

    if rainfall_match:
        value = rainfall_match.group(1)
        unit = rainfall_match.group(2) or ""
        data["rainfall"] = f"{value}{unit}"

    elif (
        "low rainfall" in text
        or "rainfall is low" in text
        or "rainfall is very low" in text
        or "low rain" in text
    ):
        data["rainfall"] = "low"

    elif (
        "high rainfall" in text
        or "rainfall is high" in text
        or "heavy rainfall" in text
    ):
        data["rainfall"] = "high"

    elif (
        "medium rainfall" in text
        or "rainfall is medium" in text
    ):
        data["rainfall"] = "medium"

    # Soil organic carbon
    soc_match = re.search(
        r"(?:soil organic carbon|organic carbon|soc)\s*(?:is|of|around)?\s*(\d+(?:\.\d+)?)\s*%?",
        text,
    )

    if soc_match:
        data["soil_organic_carbon_pct"] = float(soc_match.group(1))

    # Soil pH
    ph_match = re.search(
        r"(?:soil\s*)?ph\s*(?:is|of|around)?\s*(\d+(?:\.\d+)?)",
        text,
    )

    if ph_match:
        data["soil_ph"] = float(ph_match.group(1))

    # Temperature
    temp_match = re.search(
        r"(?:temperature|temp)\s*(?:is|of|around)?\s*(-?\d+(?:\.\d+)?)\s*(?:°?\s*c)?",
        text,
    )

    if temp_match:
        data["temperature"] = temp_match.group(1) + " C"

    # Crop
    crops = [
        "wheat",
        "rice",
        "millet",
        "maize",
        "corn",
        "sorghum",
        "ragi",
        "cotton",
        "sugarcane",
        "groundnut",
        "soybean",
    ]

    for crop in crops:
        if crop in text:
            data["crop"] = crop
            break

    # Land use
    if "monoculture" in text:
        data["land_use_type"] = "monoculture"

    elif "agroforestry" in text:
        data["land_use_type"] = "agroforestry"

    elif "forest" in text:
        data["land_use_type"] = "forest"

    elif "farmland" in text or "farm land" in text:
        data["land_use_type"] = "farmland"

    elif "agriculture" in text:
        data["land_use_type"] = "agriculture"

    # Pollution
    if "high pollution" in text:
        data["pollution_level"] = "high"

    elif "low pollution" in text:
        data["pollution_level"] = "low"

    elif "pollution" in text:
        data["pollution_level"] = "present"

    elif "pesticide" in text:
        data["pollution_level"] = "pesticide use"

    # Deforestation
    if "high deforestation" in text:
        data["deforestation_rate"] = "high"

    elif "low deforestation" in text:
        data["deforestation_rate"] = "low"

    elif "deforestation" in text:
        data["deforestation_rate"] = "present"

    # Region
    regions = [
        "semi-arid",
        "arid",
        "tropical",
        "subtropical",
        "temperate",
        "coastal",
        "dry",
        "humid",
    ]

    for region in regions:
        if region in text:
            data["region"] = region
            break

    # Validate through Pydantic model
    valid_fields = set(StructuredInput.model_fields.keys())

    filtered = {
        key: value
        for key, value in data.items()
        if key in valid_fields
    }

    valid = StructuredInput(**filtered)

    return valid.model_dump(exclude_none=True)