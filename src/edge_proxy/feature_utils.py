from typing import Any


def filter_out_server_key_only_flags(
    flags: list[dict[str, Any]],
    server_key_only_feature_ids: list[int],
) -> list[dict[str, Any]]:
    """
    Filter out server-key-only flags from the list.

    Args:
        flags: List of flag results
        server_key_only_feature_ids: List of feature IDs that are server-key-only

    Returns:
        Filtered list of flags excluding server-key-only features
    """
    return [
        flag
        for flag in flags
        if flag.get("metadata", {}).get("id") not in server_key_only_feature_ids
    ]


def filter_disabled_flags(
    flags: list[dict[str, Any]], hide_disabled: bool
) -> list[dict[str, Any]]:
    """
    Filter out disabled flags if hide_disabled is enabled.

    Args:
        flags: List of flag results
        hide_disabled: Whether to filter out disabled flags

    Returns:
        Filtered list of flags excluding disabled ones if hide_disabled is True
    """
    if not hide_disabled:
        return flags
    return [flag for flag in flags if flag.get("enabled", False)]
