from typing import Any, Optional

from flag_engine.features.models import FeatureStateModel
from flag_engine.identities.traits.models import TraitModel

from src.schemas import APIFeatureStateSchema

_api_feature_state_schema = APIFeatureStateSchema()


def map_feature_state_to_response_data(
    feature_state: FeatureStateModel,
    identity_hash_key: Optional[str] = None,
) -> dict[str, Any]:
    data = _api_feature_state_schema.dump(feature_state)
    data["feature_state_value"] = feature_state.get_value(identity_id=identity_hash_key)
    return data


def map_feature_states_to_response_data(
    feature_states: list[FeatureStateModel],
    identity_hash_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    return [
        map_feature_state_to_response_data(feature_state, identity_hash_key)
        for feature_state in feature_states
    ]


def map_traits_to_response_data(
    traits: list[TraitModel],
) -> list[dict[str, Any]]:
    return [trait.dict() for trait in traits]
