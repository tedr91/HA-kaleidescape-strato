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


class KaleidescapeClient:
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
        payload = _build_payload(command)
        reader = None
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            if self._debug_commands:
                _LOGGER.info("Kaleidescape command send: %s", payload.decode("latin-1").strip())
            writer.write(payload)
            await writer.drain()

            response = await asyncio.wait_for(reader.readline(), timeout=self._timeout)
            if response:
                decoded_response = response.decode(errors="ignore").strip()
                if self._debug_commands:
                    _LOGGER.info("Kaleidescape command response: %s", decoded_response)
                else:
                    _LOGGER.debug("Kaleidescape command response: %s", decoded_response)
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()
