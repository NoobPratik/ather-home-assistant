from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL, BINARY_SENSORS_META

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        AtherBinarySensor(vin, model, key, meta, coordinator) 
        for key, meta in BINARY_SENSORS_META.items()
    ])

class AtherBinarySensor(BinarySensorEntity):
    def __init__(self, vin, model, key, meta, coordinator):
        self._vin = vin
        self._model = model
        self._key = key
        self._parent = meta["parent"]
        self._on_value = meta["on_value"]
        self._coordinator = coordinator
        
        self._attr_name = f"Ather {model} {meta['name']}"
        self._attr_unique_id = f"ather_{vin}_{key}"
        self._attr_device_class = meta["class"]
        self._attr_icon = meta["icon"]
        self._is_on = False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin)},
            "name": f"Ather {self._model}",
            "manufacturer": "Ather Energy",
            "model": self._model
        }

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update))
        self._handle_update()

    @callback
    def _handle_update(self):
        cache = self._coordinator.data
        bike = cache.get("telemetry.bike", {})
        charging = cache.get("telemetry.charging", {})

        if self._key == "chargerConnected":
            vehicle_state = bike.get("vehicle_state", "").lower()
            heartbeat = charging.get("chargingHeartBeat", "Off")
            
            if vehicle_state in ["charging", "charged"] or heartbeat == "On":
                if vehicle_state == "charging" and heartbeat == "Off" and charging.get("chargingStatus") == "Not Charging":
                    self._is_on = False
                else:
                    self._is_on = True
            else:
                self._is_on = False
        elif self._parent in cache and self._key in cache[self._parent]:
            val = cache[self._parent][self._key]
            self._is_on = (val == self._on_value)

        self.async_write_ha_state()