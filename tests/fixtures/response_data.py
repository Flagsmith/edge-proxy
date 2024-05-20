_segment_override_feature_state = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "segment_override",
    "feature": {
        "name": "feature_2",
        "type": "STANDARD",
        "id": 2,
    },
    "enabled": True,
}


_environment_feature_state_1 = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "feature_1_value",
    "feature": {
        "name": "feature_1",
        "type": "STANDARD",
        "id": 1,
    },
    "enabled": False,
}


_environment_feature_state_2 = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "2.3",
    "feature": {
        "name": "feature_2",
        "type": "STANDARD",
        "id": 2,
    },
    "enabled": True,
}


_environment_feature_state_3 = {
    "multivariate_feature_state_values": [],
    "feature_state_value": None,
    "feature": {
        "name": "feature_3",
        "type": "STANDARD",
        "id": 3,
    },
    "enabled": False,
}


_segment_1 = {
    "name": "segment_1",
    "rules": [
        {
            "conditions": [],
            "type": "ALL",
            "rules": [
                {
                    "conditions": [
                        {
                            "value": "test",
                            "operator": "EQUAL",
                            "property_": "first_name",
                        }
                    ],
                    "type": "ANY",
                    "rules": [],
                }
            ],
        }
    ],
    "id": 1,
    "feature_states": [_segment_override_feature_state],
}


_project_1 = {
    "name": "project-1",
    "organisation": {
        "feature_analytics": False,
        "name": "org-1",
        "id": 1,
        "persist_trait_data": True,
        "stop_serving_flags": False,
    },
    "id": 1,
    "hide_disabled_flags": False,
    "segments": [_segment_1],
    "server_key_only_feature_ids": [3],
}

environment_1_api_key = "environment_1_api_key"


environment_1 = {
    "feature_states": [
        _environment_feature_state_1,
        _environment_feature_state_2,
        _environment_feature_state_3,
    ],
    "identity_overrides": [
        {
            "identifier": "overridden-id",
            "identity_uuid": "0f21cde8-63c5-4e50-baca-87897fa6cd01",
            "created_date": "2019-08-27T14:53:45.698555Z",
            "updated_at": "2023-07-14 16:12:00.000000",
            "environment_api_key": environment_1_api_key,
            "identity_features": [
                {
                    "id": 1,
                    "feature": {"id": 1, "name": "feature_1", "type": "STANDARD"},
                    "featurestate_uuid": "1bddb9a5-7e59-42c6-9be9-625fa369749f",
                    "feature_state_value": "identity_override",
                    "enabled": True,
                    "environment": 1,
                }
            ],
        }
    ],
    "api_key": environment_1_api_key,
    "project": _project_1,
    "id": 1,
}
