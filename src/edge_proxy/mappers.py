from typing import Any

from flag_engine.engine import ContextValue
from flag_engine.result.types import FlagResult


def convert_feature_value_to_type(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value
    try:
        int_val = int(value)
        if str(int_val) == value:
            return int_val
    except ValueError:
        pass
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def map_flag_result_to_response_data(
    flag_result: FlagResult[Any],
    feature_types: dict[int, str] | None = None,
) -> dict[str, Any]:
    feature_id = flag_result.get("metadata", {}).get("id")
    feature_type = (feature_types or {}).get(feature_id, "STANDARD")
    return {
        "feature": {
            "id": feature_id,
            "name": flag_result["name"],
            "type": feature_type,
        },
        "enabled": flag_result["enabled"],
        "feature_state_value": convert_feature_value_to_type(flag_result["value"]),
    }


def map_flag_results_to_response_data(
    flag_results: list[FlagResult[Any]],
    feature_types: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    return [
        map_flag_result_to_response_data(flag_result, feature_types)
        for flag_result in flag_results
    ]


def map_traits_to_response_data(
    traits: dict[str, ContextValue],
) -> list[dict[str, Any]]:
    return [{"trait_key": k, "trait_value": v} for k, v in traits.items()]
