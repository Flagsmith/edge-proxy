from flag_engine.environments.models import EnvironmentModel
from flag_engine.features.models import FeatureStateModel


def filter_out_server_key_only_feature_states(
    feature_states: list[FeatureStateModel],
    environment: EnvironmentModel,
) -> list[FeatureStateModel]:
    return [
        feature_state
        for feature_state in feature_states
        if feature_state.feature.id
        not in environment.project.server_key_only_feature_ids
    ]
