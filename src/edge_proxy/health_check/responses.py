import typing
from datetime import datetime
from typing import Optional

from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask


class HealthCheckResponse(ORJSONResponse):
    def __init__(
        self,
        status_code: int = 200,
        status: str = "ok",
        reason: Optional[str] = None,
        last_successful_update: Optional[datetime] = None,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ):
        content = {
            "status": status,
            "reason": reason,
            "last_successful_update": last_successful_update,
        }
        super().__init__(status_code=status_code, content=content, headers=headers, media_type=media_type, background=background)
