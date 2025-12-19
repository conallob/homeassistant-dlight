"""Config flow for dLight integration."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    DEFAULT_PORT,
    COMMAND_QUERY_DEVICE_INFO,
    SOCKET_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = DLightHub(data[CONF_HOST], data[CONF_PORT], data[CONF_DEVICE_ID])

    try:
        info = await hub.test_connection()
    except CannotConnect as err:
        raise CannotConnect from err
    except InvalidAuth as err:
        raise InvalidAuth from err
    except Exception as err:
        _LOGGER.exception("Unexpected exception: %s", err)
        raise CannotConnect from err

    return {"title": f"dLight {data[CONF_DEVICE_ID]}", "device_info": info}


class DLightHub:
    """Hub for communicating with dLight devices."""

    def __init__(self, host: str, port: int, device_id: str) -> None:
        """Initialize the hub."""
        self.host = host
        self.port = port
        self.device_id = device_id

    async def test_connection(self) -> dict[str, Any]:
        """Test if we can communicate with the dLight device."""
        query = {
            "commandId": "1",
            "deviceId": self.device_id,
            "commandType": COMMAND_QUERY_DEVICE_INFO,
        }

        try:
            response = await self._make_request(query)
            return response
        except Exception as err:
            _LOGGER.error("Failed to connect to dLight at %s:%s - %s", self.host, self.port, err)
            raise CannotConnect from err

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
            _LOGGER.error("Timeout connecting to dLight")
            raise CannotConnect from err
        except socket.error as err:
            _LOGGER.error("Socket error: %s", err)
            raise CannotConnect from err
        except (json.JSONDecodeError, ValueError) as err:
            _LOGGER.error("Invalid JSON response: %s", err)
            raise InvalidAuth from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dLight."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on device_id
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
