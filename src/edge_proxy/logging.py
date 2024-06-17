import logging
import logging.config
import logging.handlers

import structlog

from edge_proxy.settings import LogFormat, LoggingSettings


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


def _drop_color_message(
    record: logging.LogRecord,
    name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    # Uvicorn logs the message a second time in the extra `color_message`, but we don't
    # need it. This processor drops the key from the event dict if it exists.
    event_dict.pop("color_message", None)
    return event_dict


COMMON_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    _extract_gunicorn_access_log_event,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.stdlib.ExtraAdder(),
    _drop_color_message,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.TimeStamper(fmt="iso"),
]


def setup_logging(settings: LoggingSettings) -> None:
    processors = [
        *COMMON_PROCESSORS,
        structlog.processors.EventRenamer(settings.log_event_field_name),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Propagate uvicorn logs instead of letting uvicorn configure the format
    for name in ["uvicorn", "uvicorn.error"]:
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = settings.enable_access_log

    override = settings.override
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                LogFormat.GENERIC.value: {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "use_get_message": False,
                    "pass_foreign_args": True,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(
                            event_key=settings.log_event_field_name,
                            colors=settings.colours,
                        ),
                    ],
                    "foreign_pre_chain": processors,
                },
                LogFormat.JSON.value: {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "use_get_message": False,
                    "pass_foreign_args": True,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": processors,
                },
                **(override.get("formatters") or {}),
            },
            "handlers": {
                "default": {
                    "level": settings.log_level.to_logging_log_level(),
                    "class": "logging.StreamHandler",
                    "formatter": settings.log_format.value,
                },
                **(override.get("handlers") or {}),
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": settings.log_level.to_logging_log_level(),
                    "propagate": True,
                },
                **(override.get("loggers") or {}),
            },
        }
    )
