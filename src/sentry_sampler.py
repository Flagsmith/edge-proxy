from contextlib import suppress


def traces_sampler(ctx):
    with suppress(KeyError):
        path = ctx["asgi_scope"]["path"]
        # only trace stream endpoints
        if "stream" in path:
            return 1.0
    return 0.0
