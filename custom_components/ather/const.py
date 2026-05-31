DOMAIN = "ather"
CONF_PHONE = "phone"
CONF_ATHER_TOKEN = "ather_token"
CONF_SCOOTER_UUID = "scooter_uuid"
CONF_VIN = "vin"
CONF_MODEL = "model"

BASE_URL = "https://cerberus.ather.io"
WS_ENDPOINT = "wss://cerberus.ather.io/api/v1/ws/devices/shadows/onchange"
FIREBASE_API_KEY = "AIzaSyBj-mQpnmYrd6Cnl6M5RzmP2tcsUZEk4ik"

HEADERS_BASE = {
    "Source": "ATHER_APP/13.1.0",
    "X-Platform": "Android",
    "X-Platform-Version": "11",
    "X-Device-Info": "Google Pixel 4",
    "User-Agent": "Android/11 (Google Pixel 4)",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip",
}

# Standard Numerical/String Sensors
SENSORS_META = {
    "battery_soc": {"name": "Battery Level", "class": "battery", "unit": "%", "icon": "mdi:battery", "parent": "telemetry.bike"},
    "range": {"name": "Estimated Range", "class": "distance", "unit": "km", "icon": "mdi:map-marker-distance", "parent": "telemetry.bike"},
    "odo": {"name": "Odometer", "class": "distance", "unit": "km", "icon": "mdi:speedometer", "parent": "telemetry.bike"},
    "vehicle_state": {"name": "Vehicle State", "class": None, "unit": None, "icon": "mdi:motorbike", "parent": "telemetry.bike"},
    "mode": {"name": "Active Ride Mode", "class": None, "unit": None, "icon": "mdi:car-sports", "parent": "telemetry.bike"},
    "front_tyre_pressure": {"name": "Front Tyre Pressure", "class": None, "unit": "psi", "icon": "mdi:tire", "parent": "telemetry.tpms"},
    "rear_tyre_pressure": {"name": "Rear Tyre Pressure", "class": None, "unit": "psi", "icon": "mdi:tire", "parent": "telemetry.tpms"},
    "chargingStatus": {"name": "Charging Status", "class": None, "unit": None, "icon": "mdi:battery-charging", "parent": "telemetry.charging"},
    "chargerType": {"name": "Charger Type", "class": None, "unit": None, "icon": "mdi:ev-plug-type2", "parent": "telemetry.charging"},
}

# Boolean Binary Sensors (On/Off states)
BINARY_SENSORS_META = {
    "incognito": {"name": "Incognito Mode", "class": "privacy", "icon": "mdi:incognito", "parent": "telemetry.bike", "on_value": True},
    "smart_eco_status": {"name": "Smart Eco Mode", "class": "power", "icon": "mdi:leaf", "parent": "telemetry.bike", "on_value": "On"},
    "chargerConnected": {"name": "Charger Connected", "class": "plug", "icon": "mdi:power-plug", "parent": "telemetry.charging", "on_value": "On"},
    "front_low_pressure_flag": {"name": "Front Tyre Low Alert", "class": "problem", "icon": "mdi:tire", "parent": "telemetry.tpms", "on_value": True},
    "rear_low_pressure_flag": {"name": "Rear Tyre Low Alert", "class": "problem", "icon": "mdi:tire", "parent": "telemetry.tpms", "on_value": True},
}