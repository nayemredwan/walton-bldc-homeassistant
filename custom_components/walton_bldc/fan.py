from __future__ import annotations

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DEVICE,
    CONF_REMOTE,
    DEFAULT_NAME,
    MAX_SPEED,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    async_add_entities([WaltonBLDCFan(entry)])


class WaltonBLDCFan(FanEntity):
    _attr_has_entity_name = True
    _attr_supported_features = FanEntityFeature.SET_SPEED

    def __init__(self, entry: ConfigEntry):
        self._entry = entry

        self._attr_name = entry.data.get("name", DEFAULT_NAME)
        self._remote = entry.data[CONF_REMOTE]
        self._device = entry.data[CONF_DEVICE]

        self._attr_is_on = False
        self._speed = 1

    @property
    def percentage(self):
        return int((self._speed / MAX_SPEED) * 100)

    async def async_turn_on(self, percentage=None, **kwargs):
        self._attr_is_on = True

        if percentage is not None:
            await self.async_set_percentage(percentage)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage):
        if percentage <= 0:
            await self.async_turn_off()
            return

        self._attr_is_on = True

        self._speed = max(
            1,
            min(
                MAX_SPEED,
                round((percentage / 100) * MAX_SPEED),
            ),
        )

        self.async_write_ha_state()

    async def _send_command(self, command: str):
        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._remote,
                "device": self._device,
                "command": command,
            },
            blocking=True,
        )
