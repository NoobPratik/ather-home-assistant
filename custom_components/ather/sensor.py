from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL, SENSORS_META

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    async_add_entities([AtherSensor(vin, model, key, meta) for key, meta in SENSORS_META.items()])

class AtherSensor(SensorEntity):
    def __init__(self, vin, model, key, meta):
        self._vin = vin
        self._model = model
        self._key = key
        self._parent = meta["parent"]
        
        self._attr_name = f"Ather {model} {meta['name']}"
        self._attr_unique_id = f"ather_{vin}_{key}"
        self._attr_device_class = meta["class"]
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_icon = meta["icon"]
        self._state = None

    @property
    def device_info(self):
        """Tie the sensor entity dynamically to the shared parent vehicle device card."""
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update))

    @callback
    def _handle_update(self, data):
        """Processes incoming delta streaming payloads safely without state loss."""
        if self._parent in data and self._key in data[self._parent]:
            val = data[self._parent][self._key]
            
            if self._key == "odo":
                try: self._state = round(float(val), 1)
                except: pass
            elif self._key in ["battery_soc", "range"]:
                try: self._state = int(float(val))
                except: pass
            else:
                self._state = str(val) if val is not None else None
                
            self.async_write_ha_state()