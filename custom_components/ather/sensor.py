from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN, CONF_VIN, CONF_MODEL, SENSORS_META

async def async_setup_entry(hass, entry, async_add_entities):
    vin = entry.data[CONF_VIN]
    model = entry.data.get(CONF_MODEL, "EV Scooter")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AtherSensor(vin, model, key, meta, coordinator) for key, meta in SENSORS_META.items()]
    entities.append(AtherServiceAtSensor(vin, model, coordinator))
    entities.append(AtherServiceAfterSensor(vin, model, coordinator))
    async_add_entities(entities)

class AtherSensor(SensorEntity):
    def __init__(self, vin, model, key, meta, coordinator):
        self._vin = vin
        self._model = model
        self._key = key
        self._parent = meta["parent"]
        self._coordinator = coordinator
        
        self._attr_name = f"Ather {model} {meta['name']}"
        self._attr_unique_id = f"ather_{vin}_{key}"
        self._attr_device_class = meta["class"]
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_icon = meta["icon"]
        self._state = None

    @property
    def device_info(self):
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
        self._handle_update()

    @callback
    def _handle_update(self):
        cache = self._coordinator.data
        bike = cache.get("telemetry.bike", {})
        charging = cache.get("telemetry.charging", {})

        if self._parent in cache and self._key in cache[self._parent]:
            val = cache[self._parent][self._key]
        else:
            return

        if self._key == "odo":
            try: self._state = round(float(val), 1)
            except: pass

        elif self._key in ["battery_soc", "range"]:
            try:
                parsed_val = int(float(val))
                if parsed_val == 0 and self._state is not None and self._state > 5:
                    return
                self._state = parsed_val
            except: pass

        elif self._key == "chargingStatus":
            raw_status = str(val)
            vehicle_state = bike.get("vehicle_state", "").lower()
            
            if vehicle_state in ["sleep", "standby", "riding", "ride"] or raw_status == "Initializing":
                self._state = "Not Charging"
            else:
                self._state = raw_status

        elif self._key == "vehicle_state":
            raw_state = str(val).lower() if val else "unknown"
            heartbeat = charging.get("chargingHeartBeat", "Off")
            charging_status = charging.get("chargingStatus", "Not Charging")

            if raw_state == "charging" and heartbeat == "Off" and charging_status in ["Not Charging", "Initializing"]:
                current_state = str(self._state).lower() if self._state else "standby"
                self._state = "riding" if current_state == "riding" else "standby"
            else:
                self._state = raw_state

        else:
            self._state = str(val)
        
        self.async_write_ha_state()

class AtherServiceAtSensor(SensorEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Next Service At"
        self._attr_unique_id = f"ather_{vin}_next_service_at"
        self._attr_device_class = "distance"
        self._attr_native_unit_of_measurement = "km"
        self._attr_icon = "mdi:calendar-clock"
        self._state = None

    @property
    def device_info(self):
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
        self._handle_update()

    @callback
    def _handle_update(self):
        service = self._coordinator.data.get("service", {})
        last_service = service.get("last_service_at")
        if last_service is not None:
            self._state = round(float(last_service) + 5000, 1)
        else:
            self._state = None
        self.async_write_ha_state()

class AtherServiceAfterSensor(SensorEntity):
    def __init__(self, vin, model, coordinator):
        self._vin = vin
        self._model = model
        self._coordinator = coordinator
        self._attr_name = f"Ather {model} Next Service After"
        self._attr_unique_id = f"ather_{vin}_next_service_after"
        self._attr_device_class = "distance"
        self._attr_native_unit_of_measurement = "km"
        self._attr_icon = "mdi:map-marker-distance"
        self._state = None

    @property
    def device_info(self):
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
        self._handle_update()

    @callback
    def _handle_update(self):
        service = self._coordinator.data.get("service", {})
        last_service = service.get("last_service_at")
        bike = self._coordinator.data.get("telemetry.bike", {})
        odo = bike.get("odo")

        if last_service is not None and odo is not None:
            try:
                self._state = round(float(last_service) + 5000 - float(odo), 1)
            except (ValueError, TypeError):
                self._state = None
        else:
            self._state = None
        self.async_write_ha_state()