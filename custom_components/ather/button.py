import time
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        AtherPingButton(vin, model, coordinator),
        AtherShutdownButton(vin, model, coordinator),
    ])

class AtherPingButton(ButtonEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Ping Scooter"
        self._attr_unique_id = f"ather_{vin}_ping_scooter"
        self._attr_icon = "mdi:bullhorn"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    async def async_press(self):
        payload = {
            "state": 1,
            "timestamp": int(time.time() * 1000)
        }
        await self._coordinator.async_send_shadow_command("ping_my_scooter", payload)

class AtherShutdownButton(ButtonEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Remote Shutdown"
        self._attr_unique_id = f"ather_{vin}_remote_shutdown"
        self._attr_icon = "mdi:power"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    @property
    def available(self) -> bool:
        """Grey out button if scooter is actively charging."""
        cache = self._coordinator.data
        bike = cache.get("telemetry.bike", {})
        charging = cache.get("telemetry.charging", {})

        vehicle_state = str(bike.get("vehicle_state", "")).lower()
        charging_status = str(charging.get("chargingStatus", "")).lower()

        if vehicle_state == "charging" or charging_status == "charging":
            return False
        return True

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update)
        )
        self._handle_update()

    @callback
    def _handle_update(self):
        self.async_write_ha_state()

    async def async_press(self):
        if not self.available:
            raise HomeAssistantError("Cannot shutdown scooter while actively charging.")

        payload = {
            "state": 1,
            "timestamp": int(time.time() * 1000)
        }
        await self._coordinator.async_send_shadow_command("remote_shutdown", payload)