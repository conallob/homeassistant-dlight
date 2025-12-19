"""Platform for dLight light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DLightDataUpdateCoordinator
from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    MIN_MIREDS,
    MAX_MIREDS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the dLight light platform."""
    coordinator: DLightDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [DLightEntity(coordinator, config_entry.data[CONF_DEVICE_ID])],
        update_before_add=True,
    )


class DLightEntity(CoordinatorEntity[DLightDataUpdateCoordinator], LightEntity):
    """Representation of a dLight."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_min_mireds = MIN_MIREDS
    _attr_max_mireds = MAX_MIREDS

    def __init__(
        self,
        coordinator: DLightDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the dLight entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = device_id

    @property
    def device_info(self):
        """Return device information about this dLight."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"dLight {self._device_id}",
            "manufacturer": "Google",
            "model": "dLight",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("on", False)

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light (0-255)."""
        if self.coordinator.data is None:
            return None
        # Convert from 0-100 to 0-255
        brightness_pct = self.coordinator.data.get("brightness", 0)
        return int(brightness_pct * 255 / 100)

    @property
    def color_temp(self) -> int | None:
        """Return the color temperature in mireds."""
        if self.coordinator.data is None:
            return None
        # Get temperature in Kelvin and convert to mireds
        color_data = self.coordinator.data.get("color", {})
        temperature_k = color_data.get("temperature", 3800)
        return int(1000000 / temperature_k)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        commands = {"on": True}

        if ATTR_BRIGHTNESS in kwargs:
            # Convert from 0-255 to 0-100
            brightness_pct = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            commands["brightness"] = brightness_pct

        if ATTR_COLOR_TEMP in kwargs:
            # Convert from mireds to Kelvin
            temperature_k = int(1000000 / kwargs[ATTR_COLOR_TEMP])
            commands["color"] = {"temperature": temperature_k}

        await self.coordinator.async_send_command([commands])

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.coordinator.async_send_command([{"on": False}])
