import uvicorn

from edge_proxy.settings import ensure_defaults, get_settings


def serve():
    settings = get_settings()
    uvicorn.run(
        "edge_proxy.server:app",
        host=str(settings.server.host),
        port=settings.server.port,
        proxy_headers=settings.server.proxy_headers,
        reload=settings.server.reload,
        use_colors=settings.logging.colours,
    )


def render_config():
    ensure_defaults()
