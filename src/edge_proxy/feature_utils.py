from typing import Any
from flag_engine.result.types import FlagResult


def build_feature_types_lookup(
    environment_document: dict[str, Any],
) -> dict[int, str]:
    return {
        fs["feature"]["id"]: fs["feature"].get("type", "STANDARD")
        for fs in environment_document.get("feature_states", [])
    }


def filter_out_server_key_only_flags(
    flags: list[FlagResult[Any]],
    server_key_only_feature_ids: list[int],
) -> list[FlagResult[Any]]:
    return [
        flag
        for flag in flags
        if flag.get("metadata", {}).get("id") not in server_key_only_feature_ids
    ]


def filter_disabled_flags(
    flags: list[FlagResult[Any]], hide_disabled: bool
) -> list[FlagResult[Any]]:
    if not hide_disabled:
        return flags
    return [flag for flag in flags if flag.get("enabled", False)]
