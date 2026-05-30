from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, SENSORS_META

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    async_add_entities([AtherSensor(vin, key, meta) for key, meta in SENSORS_META.items()])

class AtherSensor(SensorEntity):
    def __init__(self, vin, key, meta):
        self._vin = vin
        self._key = key
        self._parent = meta["parent"]
        self._attr_name = f"Ather 450X {meta['name']}"
        self._attr_unique_id = f"ather_{vin}_{key}"
        self._attr_device_class = meta["class"]
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_icon = meta["icon"]
        self._state = None

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._vin)}, "name": "Ather 450X"}

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update))

    @callback
    def _handle_update(self, data):
        if self._parent in data and self._key in data[self._parent]:
            val = data[self._parent][self._key]
            if self._key == "odo":
                self._state = round(float(val), 1)
            elif self._key in ["battery_soc", "range"]:
                self._state = int(float(val))
            else:
                self._state = val
            self.async_write_ha_state()
