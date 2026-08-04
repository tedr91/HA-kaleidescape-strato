from __future__ import annotations

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

LOCAL_CPDID = "01"


def _build_payload(command: str) -> bytes:
    normalized = command.strip()
    if "/" in normalized:
        wire_command = normalized
    else:
        wire_command = f"{LOCAL_CPDID}/0/{normalized.upper()}:"
    return f"{wire_command}\n".encode("latin-1")


class KaleidescapeRawClient:
    """Fire-and-forget sender for commands that pykaleidescape does not wrap."""

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float,
        debug_commands: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._debug_commands = debug_commands

    async def async_send_command(self, command: str) -> None:
        writer: asyncio.StreamWriter | None = None
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            payload = _build_payload(command)
            if self._debug_commands:
                _LOGGER.info("Kaleidescape raw send: %s", payload.decode("latin-1").strip())
            writer.write(payload)
            await writer.drain()
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()
