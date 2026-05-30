from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, BINARY_SENSORS_META

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    async_add_entities([AtherBinarySensor(vin, key, meta) for key, meta in BINARY_SENSORS_META.items()])

class AtherBinarySensor(BinarySensorEntity):
    def __init__(self, vin, key, meta):
        self._vin = vin
        self._key = key
        self._parent = meta["parent"]
        self._on_value = meta["on_value"]
        self._attr_name = f"Ather 450X {meta['name']}"
        self._attr_unique_id = f"ather_{vin}_{key}"
        self._attr_device_class = meta["class"]
        self._attr_icon = meta["icon"]
        self._is_on = False

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._vin)}, "name": "Ather 450X"}

    @property
    def is_on(self):
        return self._is_on

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update))

    @callback
    def _handle_update(self, data):
        if self._parent in data and self._key in data[self._parent]:
            self._is_on = data[self._parent][self._key] == self._on_value
            self.async_write_ha_state()
