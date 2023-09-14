import asyncio
import logging
import time
from asyncio import AbstractEventLoop
from typing import Any, Dict, List, NoReturn, Tuple

import pytest
from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture

from fastapi_utils.tasks import repeat_every

logging.basicConfig(level=logging.INFO)


def ignore_exception(_loop: AbstractEventLoop, _context: Dict[str, Any]) -> None:
    pass


@pytest.fixture(autouse=True)
def setup_event_loop(event_loop: AbstractEventLoop) -> None:
    event_loop.set_exception_handler(ignore_exception)


@pytest.mark.asyncio
async def test_repeat_unlogged_error(caplog: LogCaptureFixture) -> None:
    # Given
    @repeat_every(seconds=0.07)
    def log_exc() -> NoReturn:
        raise ValueError("repeat")

    # When
    await log_exc()
    await asyncio.sleep(0.1)

    # Then
    record_tuples = [x for x in caplog.record_tuples if x[0] == __name__]
    assert len(record_tuples) == 0


@pytest.mark.asyncio
async def test_repeat_log_error(caplog: LogCaptureFixture) -> None:
    # Given
    logger = logging.getLogger(__name__)

    @repeat_every(seconds=0.1, logger=logger)
    def log_exc() -> NoReturn:
        raise ValueError("repeat")

    # When
    await log_exc()
    n_record_tuples = 0
    record_tuples: List[Tuple[Any, ...]] = []
    start_time = time.time()
    while n_record_tuples < 2:  # ensure multiple records are logged
        time_elapsed = time.time() - start_time
        if time_elapsed > 1:
            print(record_tuples)
            assert False, "Test timed out"
        await asyncio.sleep(0.05)

        # Then
        record_tuples = [x for x in caplog.record_tuples if x[0] == __name__]
        n_record_tuples = len(record_tuples)


@pytest.mark.asyncio
async def test_repeat_raise_error(
    caplog: LogCaptureFixture, capsys: CaptureFixture
) -> None:
    # Given
    logger = logging.getLogger(__name__)

    @repeat_every(seconds=0.07, raise_exceptions=True, logger=logger)
    def raise_exc() -> NoReturn:
        raise ValueError("repeat")

    # When
    await raise_exc()
    await asyncio.sleep(0.1)
    out, err = capsys.readouterr()

    # Then
    assert out == ""
    assert err == ""
    record_tuples = [x for x in caplog.record_tuples if x[0] == __name__]
    assert len(record_tuples) == 1
