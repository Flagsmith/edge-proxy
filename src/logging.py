import logging
import logging.handlers

import structlog

from .settings import LogFormat, LoggingSettings


def _extract_gunicorn_access_log_event(
    record: logging.LogRecord,
    name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    # Extract logger args from Gunicorn access log entry
    # and map them to Flagsmith's JSON log format.
    # Argument positions taken from
    # https://github.com/encode/uvicorn/blob/a2219eb2ed2bbda4143a0fb18c4b0578881b1ae8/uvicorn/logging.py#L99-L105
    if event_dict.get("logger") == "uvicorn.access":
        remote_ip, method, path, _, status = event_dict["positional_args"]
        event_dict["remote_ip"] = remote_ip
        event_dict["method"] = method
        event_dict["path"] = path
        event_dict["status"] = status
    return event_dict


def setup_logging(settings: LoggingSettings) -> None:
    """
    Configure stdlib logger to use structlog processors and formatters so that
    uvicorn and application logs are consistent.
    """
    is_generic_format = settings.log_format is LogFormat.GENERIC

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        _extract_gunicorn_access_log_event,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if is_generic_format:
        # For `generic` format, set `exc_info` on the log event if the log method is
        # `exception` and `exc_info` is not already set.
        #
        # Rendering of `exc_info` is handled by ConsoleRenderer.
        processors.append(structlog.dev.set_exc_info)
    else:
        # For `json` format `exc_info` must be set explicitly when
        # needed, and is translated into a formatted `exception` field.
        processors.append(structlog.processors.format_exc_info)

    processors.append(structlog.processors.EventRenamer(settings.log_event_field_name))

    structlog.configure(
        processors=processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if is_generic_format:
        log_renderer = structlog.dev.ConsoleRenderer(
            event_key=settings.log_event_field_name
        )
    else:
        log_renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        use_get_message=False,
        pass_foreign_args=True,
        foreign_pre_chain=processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(settings.log_level.to_logging_log_level())

    # Propagate uvicorn logs instead of letting uvicorn configure the format
    for name in ["uvicorn", "uvicorn.error"]:
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = settings.enable_access_log
