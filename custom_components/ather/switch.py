import time
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AtherRemoteChargingSwitch(vin, model, coordinator)])

class AtherRemoteChargingSwitch(SwitchEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Remote Charging"
        self._attr_unique_id = f"ather_{vin}_remote_charging_switch"
        self._attr_icon = "mdi:ev-station"
        self._is_on = False
        self._last_command_time = 0

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
        cache = self._coordinator.data
        bike = cache.get("telemetry.bike", {})
        charging = cache.get("telemetry.charging", {})

        vehicle_state = str(bike.get("vehicle_state", "")).lower()
        charging_status = str(charging.get("chargingStatus", "")).lower()
        heartbeat = str(charging.get("chargingHeartBeat", "")).lower()

        if vehicle_state in ["charging", "charged"] or charging_status == "charging" or heartbeat == "on":
            return True
        return False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update)
        )
        self._handle_update()

    @callback
    def _handle_update(self):
        if time.time() - self._last_command_time < 6:
            return

        cache = self._coordinator.data
        remote_charging = cache.get("scooters.remote_charging", {})
        charging_telemetry = cache.get("telemetry.charging", {})

        action = remote_charging.get("action")
        if action == "start":
            self._is_on = True
        elif action == "stop":
            self._is_on = False
        else:
            self._is_on = (charging_telemetry.get("chargingStatus") == "Charging")

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        if not self.available:
            raise HomeAssistantError("Cannot control remote charging when charger is not connected.")

        self._is_on = True
        self._last_command_time = time.time()
        self.async_write_ha_state()

        payload = {
            "state": 1,
            "action": "start",
            "error": "0",
            "timestamp": int(time.time() * 1000)
        }
        success = await self._coordinator.async_send_shadow_command("remote_charging", payload)
        if not success:
            self._last_command_time = 0
            self._handle_update()

    async def async_turn_off(self, **kwargs):
        if not self.available:
            raise HomeAssistantError("Cannot control remote charging when charger is not connected.")

        self._is_on = False
        self._last_command_time = time.time()
        self.async_write_ha_state()

        payload = {
            "state": 1,
            "action": "stop",
            "error": "0",
            "timestamp": int(time.time() * 1000)
        }
        success = await self._coordinator.async_send_shadow_command("remote_charging", payload)
        if not success:
            self._last_command_time = 0
            self._handle_update()