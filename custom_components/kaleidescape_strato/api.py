from __future__ import annotations

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class KaleidescapeClient:
    def __init__(self, host: str, port: int, timeout: float) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout

    async def async_can_connect(self) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            _LOGGER.debug("Unable to connect to Kaleidescape host %s:%s", self._host, self._port)
            return False

    async def async_send_command(self, command: str) -> None:
        payload = f"{command.strip()}\r\n".encode()
        reader = None
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            writer.write(payload)
            await writer.drain()
            await asyncio.sleep(0)
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()
