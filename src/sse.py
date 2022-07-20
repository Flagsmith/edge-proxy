import asyncio

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def read_items():

    html_sse = """
        <html>
        <body>
            <h1>Response from server:</h1>
            <div id="response"></div>
            <script>
                document.getElementById('response').innerText = 'Hello World!';
                var evtSource = new EventSource("/stream");
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


@router.get("/stream")
async def message_stream(request: Request):
    print("Streaming started")

    def new_messages():
        print("new_messages")
        # Add logic here to check for new messages
        yield "Hello World"

    async def event_generator():
        count = 0
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                print("Streaming stopped")
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                print("new_messages")
                yield {
                    "event": "message",
                    "id": "message_id",
                    "retry": RETRY_TIMEOUT,
                    "data": f"message_content {count}",
                }
                count = count + 1

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())
