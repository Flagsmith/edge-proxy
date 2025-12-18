from typing import Any


def filter_out_server_key_only_flags(
    flags: list[dict[str, Any]],
    server_key_only_feature_ids: list[int],
) -> list[dict[str, Any]]:
    return [
        flag
        for flag in flags
        if flag.get("metadata", {}).get("id") not in server_key_only_feature_ids
    ]


def filter_disabled_flags(
    flags: list[dict[str, Any]], hide_disabled: bool
) -> list[dict[str, Any]]:
    if not hide_disabled:
        return flags
    return [flag for flag in flags if flag.get("enabled", False)]
