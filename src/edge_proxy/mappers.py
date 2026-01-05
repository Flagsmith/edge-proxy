from typing import TYPE_CHECKING, Any

from flag_engine.engine import ContextValue
from flag_engine.result.types import FlagResult

if TYPE_CHECKING:
    from edge_proxy.models import TraitModel


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
        "feature_state_value": flag_result["value"],
    }


def map_flag_results_to_response_data(
    flag_results: list[FlagResult[Any]],
    feature_types: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    return [
        map_flag_result_to_response_data(flag_result, feature_types)
        for flag_result in flag_results
    ]


def convert_traits_to_dict(traits: list["TraitModel"]) -> dict[str, ContextValue]:
    return {trait.trait_key: trait.trait_value for trait in traits}


def map_traits_to_response_data(
    traits: list["TraitModel"],
) -> list[dict[str, Any]]:
    return [{"trait_key": t.trait_key, "trait_value": t.trait_value} for t in traits]
