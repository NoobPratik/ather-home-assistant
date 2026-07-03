from homeassistant.components.number import NumberEntity
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AtherLastServiceNumber(vin, model, coordinator)])

class AtherLastServiceNumber(NumberEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Last Service At"
        self._attr_unique_id = f"ather_{vin}_last_service_at"
        self._attr_icon = "mdi:wrench-outline"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 999999
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "km"
        self._attr_mode = "box"

    @property
    def native_value(self):
        return self._coordinator.data.get("service", {}).get("last_service_at")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(
            self.hass, self._coordinator.signal_name, self._handle_update
        ))

    @callback
    def _handle_update(self):
        self.async_write_ha_state()

    async def async_set_native_value(self, value):
        self._coordinator.data.setdefault("service", {})["last_service_at"] = float(value)
        await self._coordinator.async_persist_last_service()
        async_dispatcher_send(self.hass, self._coordinator.signal_name)
