from contextlib import suppress

from .settings import Settings

settings = Settings()


def traces_sampler(ctx):
    with suppress(KeyError):
        path = ctx["asgi_scope"]["path"]
        # only trace stream endpoints
        if "stream" in path:
            return settings.stream_endpoint_sample_rate
    return 0.0
