import asyncio
import aiohttp
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import DOMAIN, CONF_ATHER_TOKEN, CONF_SCOOTER_UUID, CONF_VIN, WS_ENDPOINT, HEADERS_BASE

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor", "device_tracker", "button", "number"]

class AtherDataCoordinator:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.data = {
            "telemetry.bike": {},
            "telemetry.charging": {},
            "telemetry.tpms": {},
            "service": {"last_service_at": None}
        }
        self.last_synced_time = 0
        self.vin = entry.data[CONF_VIN]
        self.signal_name = f"{DOMAIN}_update_{self.vin}"
        self._store = Store(hass, 1, f"{DOMAIN}_last_service_{self.vin}")

    async def async_restore_last_service(self):
        stored = await self._store.async_load()
        if stored and isinstance(stored, dict) and "last_service_at" in stored:
            self.data["service"]["last_service_at"] = stored["last_service_at"]

    async def async_persist_last_service(self):
        val = self.data.get("service", {}).get("last_service_at")
        await self._store.async_save({"last_service_at": val})

    def update_data(self, delta_data):
        bike_data = delta_data.get("telemetry.bike", {})
        new_timestamp = bike_data.get("last_synced_time")

        if new_timestamp:
            try:
                ts = int(new_timestamp)
                if ts < self.last_synced_time:
                    _LOGGER.debug("Dropped stale Ather telemetry packet. TS: %s < %s", ts, self.last_synced_time)
                    return
                self.last_synced_time = ts
            except (ValueError, TypeError):
                pass

        for parent_key, child_dict in delta_data.items():
            if parent_key in self.data and isinstance(child_dict, dict):
                self.data[parent_key].update(child_dict)

        async_dispatcher_send(self.hass, self.signal_name)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = AtherDataCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_restore_last_service()
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    coordinator.loop_task = hass.loop.create_task(ather_websocket_loop(hass, entry, coordinator))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN][entry.entry_id]
        coordinator.loop_task.cancel()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def ather_websocket_loop(hass: HomeAssistant, entry: ConfigEntry, coordinator: AtherDataCoordinator):
    session = async_get_clientsession(hass)
    token = entry.data[CONF_ATHER_TOKEN]
    uuid = entry.data[CONF_SCOOTER_UUID]
    
    url = f"{WS_ENDPOINT}?uuid={uuid}"
    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    while True:
        try:
            async with session.ws_connect(url, headers=headers, heartbeat=30) as ws:
                _LOGGER.info("Connected to Ather WebSocket!")
                await ws.send_json({"paths": ["telemetry.bike", "telemetry.charging", "telemetry.tpms"]})
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        coordinator.update_data(data)
                        
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        _LOGGER.warning("Ather WebSocket closed. Code: %s", ws.close_code)
                        if ws.close_code in [401, 403, 4000, 4001]:
                            _LOGGER.error("Ather API Token Expired. Triggering HA Re-Auth.")
                            entry.async_start_reauth(hass)
                            return
                        break
                        
        except aiohttp.WSServerHandshakeError as e:
            _LOGGER.error("WebSocket Handshake Error (Status %s). Token might be expired.", e.status)
            if e.status in [401, 403]:
                entry.async_start_reauth(hass)
                return
            await asyncio.sleep(10)
        except Exception as e:
            _LOGGER.debug("Ather WebSocket connection broke: %s. Reconnecting in 10s...", e)
            await asyncio.sleep(10)