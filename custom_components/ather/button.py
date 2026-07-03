from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, CONF_VIN, CONF_MODEL

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AtherServiceButton(vin, model, coordinator)])

class AtherServiceButton(ButtonEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Record Servicing"
        self._attr_unique_id = f"ather_{vin}_record_service"
        self._attr_icon = "mdi:wrench"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    async def async_press(self):
        cache = self._coordinator.data
        bike = cache.get("telemetry.bike", {})
        odo = bike.get("odo")

        if odo is None:
            return

        self._coordinator.data.setdefault("service", {})["last_service_at"] = round(float(odo), 1)
        await self._coordinator.async_persist_last_service()
        async_dispatcher_send(self.hass, self._coordinator.signal_name)
