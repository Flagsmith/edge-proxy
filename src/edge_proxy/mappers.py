from typing import Any
from flag_engine.engine import ContextValue

from edge_proxy.schemas import APIFeatureStateSchema

_api_feature_state_schema = APIFeatureStateSchema()


def map_flag_result_to_response_data(
    flag_result: dict[str, Any],
) -> dict[str, Any]:
    """Map a single flag result to API response format."""
    return {
        "feature": {
            "id": flag_result.get("metadata", {}).get("id"),
            "name": flag_result["name"],
            "type": flag_result.get("type", "STANDARD"),
        },
        "enabled": flag_result["enabled"],
        "feature_state_value": flag_result["value"],
    }


def map_flag_results_to_response_data(
    flag_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Map multiple flag results to API response format."""
    return [
        map_flag_result_to_response_data(flag_result) for flag_result in flag_results
    ]


def map_traits_to_response_data(
    traits: dict[str, ContextValue],
) -> list[dict[str, Any]]:
    """Convert traits dict to API response format (list of trait objects)."""
    return [{"trait_key": k, "trait_value": v} for k, v in traits.items()]
