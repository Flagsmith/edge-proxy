import asyncio
import sqlite3

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from .sse_models import Environment
from .sse_models import mapper_registry

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
mapper_registry.metadata.create_all(engine)

router = APIRouter()
db = sqlite3.connect("sse.db")


@router.post("/environments/{environment_key}/queue-change")
async def environment_updated(environment_key: str):
    session = Session(engine, autoflush=True)
    environment = Environment(key=environment_key)
    session.add(environment)
    session.commit()
    session.close()

    return JSONResponse(status_code=200)


@router.get("/home", response_class=HTMLResponse)
async def read_items():

    html_sse = """
        <html>
        <body>
            <h1>Response from server:</h1>
            <div id="response"></div>
            <script>
                let environment_key = prompt("paste Environment Key");
                document.getElementById('response').innerText = 'Hello World!';
                var evtSource = new EventSource("/stream?environment_key=" + environment_key);
                console.log("evtSource: ", evtSource);
                evtSource.onmessage = function(e) {
                    document.getElementById('response').innerText = e.data;
                    console.log(e);
                    if (e.data == 20) {
                        console.log("Closing connection after 20 numbers.")
                        evtSource.close()
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_sse, status_code=200)


STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond


@router.get("/environments/{environment_key}/stream")
async def message_stream(request: Request, environment_key: str):
    session = Session(engine, autoflush=True)

    async def new_messages():
        environment_updated = False
        environment = session.get(Environment, environment_key)
        if environment:
            environment_updated = True
            session.delete(environment)

        session.commit()
        return environment_updated

    async def event_generator():
        count = 0
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                session.close()
                print("Streaming stopped")
                break
            # Checks for new messages and return them to client if any
            if await new_messages():
                yield {
                    "event": "message",
                    "id": "message_id",
                    "retry": RETRY_TIMEOUT,
                    "data": f"message_content {count}, for environment_key: {environment_key}",
                }
                count = count + 1

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())
