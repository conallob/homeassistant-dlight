"""The dLight integration."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    COMMAND_QUERY_DEVICE_STATES,
    UPDATE_INTERVAL,
    SOCKET_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up dLight from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = DLightDataUpdateCoordinator(
        hass,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_DEVICE_ID],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class DLightDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching dLight data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        device_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.host = host
        self.port = port
        self.device_id = device_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the dLight device."""
        query = {
            "commandId": "2",
            "deviceId": self.device_id,
            "commandType": COMMAND_QUERY_DEVICE_STATES,
        }

        try:
            response = await self._make_request(query)
            if "states" not in response:
                raise UpdateFailed("Invalid response from dLight device")
            return response["states"]
        except Exception as err:
            raise UpdateFailed(f"Error communicating with dLight: {err}") from err

    async def async_send_command(self, commands: list[dict[str, Any]]) -> dict[str, Any]:
        """Send a command to the dLight device."""
        query = {
            "commandId": "3",
            "deviceId": self.device_id,
            "commandType": "EXECUTE",
            "commands": commands,
        }

        try:
            response = await self._make_request(query)
            # Refresh data after command
            await self.async_request_refresh()
            return response
        except Exception as err:
            _LOGGER.error("Error sending command to dLight: %s", err)
            raise

    async def _make_request(self, query: dict[str, Any]) -> dict[str, Any]:
        """Make a request to the dLight device."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_request, query)

    def _sync_request(self, query: dict[str, Any]) -> dict[str, Any]:
        """Synchronous request to the dLight device."""
        import socket

        jquery = json.dumps(query)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(SOCKET_TIMEOUT)
                sock.connect((self.host, self.port))
                sock.sendall(jquery.encode("UTF-8"))
                data = sock.recv(8 * 1024)
                recv = data.decode("UTF-8")

            # Skip the first 4 bytes (length prefix)
            response = json.loads(recv[4:])
            return response
        except socket.timeout as err:
            raise UpdateFailed("Timeout connecting to dLight") from err
        except socket.error as err:
            raise UpdateFailed(f"Socket error: {err}") from err
        except (json.JSONDecodeError, ValueError) as err:
            raise UpdateFailed(f"Invalid JSON response: {err}") from err
