import asyncio
import aiohttp
import json
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, CONF_ATHER_TOKEN, CONF_SCOOTER_UUID, CONF_VIN, CONF_MODEL, WS_ENDPOINT, HEADERS_BASE

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ather from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.data[DOMAIN][entry.entry_id] = hass.loop.create_task(
        ather_websocket_loop(hass, entry)
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN][entry.entry_id].cancel()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def ather_websocket_loop(hass: HomeAssistant, entry: ConfigEntry):
    """The background task that streams live data from Ather to Home Assistant."""
    session = async_get_clientsession(hass)
    token = entry.data[CONF_ATHER_TOKEN]
    uuid = entry.data[CONF_SCOOTER_UUID]
    vin = entry.data[CONF_VIN]
    
    url = f"{WS_ENDPOINT}?uuid={uuid}"
    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    signal_name = f"{DOMAIN}_update_{vin}"
    
    while True:
        try:
            async with session.ws_connect(url, headers=headers) as ws:
                _LOGGER.info("Connected to Ather WebSocket!")
                await ws.send_json({"paths": ["telemetry.bike", "telemetry.charging", "telemetry.tpms"]})
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        async_dispatcher_send(hass, signal_name, data)
                        
        except Exception as e:
            _LOGGER.error(f"Ather WebSocket session lost: {e}. Reinitializing connection in 5s...")
            await asyncio.sleep(5)