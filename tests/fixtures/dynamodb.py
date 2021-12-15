from decimal import Decimal

_segment_override_feature_state_document = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "segment_override",
    "feature": {
        "name": "feature_2",
        "type": "STANDARD",
        "id": Decimal("2"),
    },
    "enabled": True,
}


_environment_feature_state_1_document = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "feature_1_value",
    "feature": {
        "name": "feature_1",
        "type": "STANDARD",
        "id": Decimal("1"),
    },
    "enabled": False,
}


_environment_feature_state_2_document = {
    "multivariate_feature_state_values": [],
    "feature_state_value": "2.3",
    "feature": {
        "name": "feature_2",
        "type": "STANDARD",
        "id": Decimal("2"),
    },
    "enabled": True,
}


_environment_feature_state_3_document = {
    "multivariate_feature_state_values": [],
    "feature_state_value": None,
    "feature": {
        "name": "feature_3",
        "type": "STANDARD",
        "id": Decimal("3"),
    },
    "enabled": False,
}


_segment_1_document = {
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
    "id": Decimal("1"),
    "feature_states": [_segment_override_feature_state_document],
}


_project_1_document = {
    "name": "project-1",
    "organisation": {
        "feature_analytics": False,
        "name": "org-1",
        "id": Decimal("1"),
        "persist_trait_data": True,
        "stop_serving_flags": False,
    },
    "id": 1,
    "hide_disabled_flags": False,
    "segments": [_segment_1_document],
}


environment_1_document = {
    "feature_states": [
        _environment_feature_state_1_document,
        _environment_feature_state_2_document,
        _environment_feature_state_3_document,
    ],
    "api_key": "environment_1_api_key",
    "project": _project_1_document,
    "id": Decimal("1"),
}
