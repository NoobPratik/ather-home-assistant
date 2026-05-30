from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    async_add_entities([AtherDeviceTracker(vin)])

class AtherDeviceTracker(TrackerEntity):
    def __init__(self, vin):
        self._vin = vin
        self._attr_name = "Ather 450X Location"
        self._attr_unique_id = f"ather_{vin}_location"
        self._latitude = None
        self._longitude = None
        self._accuracy = 0

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._vin)}, "name": "Ather 450X"}

    @property
    def latitude(self): return self._latitude
    @property
    def longitude(self): return self._longitude
    @property
    def gps_accuracy(self): return self._accuracy
    @property
    def source_type(self): return SourceType.GPS

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, f"{DOMAIN}_update_{self._vin}", self._handle_update))

    @callback
    def _handle_update(self, data):
        if "telemetry.bike" in data and "gps_location" in data["telemetry.bike"]:
            gps = data["telemetry.bike"]["gps_location"]
            if "lat" in gps and "lng" in gps:
                self._latitude = gps["lat"]
                self._longitude = gps["lng"]
                self._accuracy = gps.get("Accuracy", 0)
                self.async_write_ha_state()
