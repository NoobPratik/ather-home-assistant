import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_PHONE, CONF_ATHER_TOKEN, CONF_SCOOTER_UUID, CONF_VIN, CONF_MODEL, BASE_URL, HEADERS_BASE

_LOGGER = logging.getLogger(__name__)

class AtherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.phone = None
        self.country_code = "IN"

    async def async_step_user(self, user_input=None):
        """Step 1: Ask for Phone Number."""
        errors = {}
        if user_input is not None:
            self.phone = user_input[CONF_PHONE]
            session = async_get_clientsession(self.hass)
            
            payload = {
                "contact_no": self.phone, 
                "country_code": self.country_code, 
                "email": "", 
                "notification_medium": {"sms": True, "whatsapp": False}
            }
            
            try:
                async with session.post(f"{BASE_URL}/auth/v2/generate-login-otp", json=payload, headers=HEADERS_BASE, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "attemptsLeft" in data:
                            return await self.async_step_otp()
                        else:
                            errors["base"] = "otp_failed"
                    else:
                        _LOGGER.error("Ather API returned status %s during OTP generation", resp.status)
                        errors["base"] = "api_error"
            except Exception as e:
                _LOGGER.error("Connection error during OTP generation: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_PHONE): str}),
            errors=errors
        )

    async def async_step_otp(self, user_input=None):
        """Step 2: Ask for OTP, fetch tokens, and resolve scooter model."""
        errors = {}
        if user_input is not None:
            otp = user_input["otp"]
            session = async_get_clientsession(self.hass)
            
            payload = {
                "contact_no": self.phone, 
                "country_code": self.country_code, 
                "email": "", 
                "userOtp": otp, 
                "is_mobile_login": True
            }
            
            try:
                async with session.post(f"{BASE_URL}/auth/v2/verify-login-otp", json=payload, headers=HEADERS_BASE, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "success":
                            ather_token = data["token"]
                            
                            auth_headers = HEADERS_BASE.copy()
                            auth_headers["Authorization"] = f"Bearer {ather_token}"
                            
                            async with session.get(f"{BASE_URL}/api/v2/auth/user/scooters/firebase-dbs", headers=auth_headers, timeout=10) as shard_resp:
                                if shard_resp.status != 200:
                                    return self.async_show_form(step_id="otp", errors={"base": "api_error"})
                                
                                shard_data = await shard_resp.json()
                                scooters = shard_data.get("shardDetails", [])
                                
                                if not scooters:
                                    return self.async_abort(reason="no_scooters_found")
                                
                                if len(scooters) > 1:
                                    _LOGGER.warning("Multiple scooters detected. Setting up primary: %s", scooters[0].get("scooter"))
                                
                                scooter_uuid = scooters[0].get("scooter_uuid")
                            
                            async with session.get(f"{BASE_URL}/api/v1/devices/shadows/scooters/properties", headers=auth_headers, params={"uuid": scooter_uuid, "state": "reported"}, timeout=10) as props_resp:
                                if props_resp.status != 200:
                                    return self.async_show_form(step_id="otp", errors={"base": "api_error"})
                                
                                props = (await props_resp.json()).get("data", {})
                                vin = props.get("vin", "Unknown_VIN")
                                scooter_model = props.get("model_type", "EV Scooter").strip()

                            existing_entry = await self.async_set_unique_id(vin)
                            if existing_entry:
                                self.hass.config_entries.async_update_entry(existing_entry, data={
                                    CONF_PHONE: self.phone,
                                    CONF_ATHER_TOKEN: ather_token,
                                    CONF_SCOOTER_UUID: scooter_uuid,
                                    CONF_VIN: vin,
                                    CONF_MODEL: scooter_model
                                })
                                self.hass.async_create_task(self.hass.config_entries.async_reload(existing_entry.entry_id))
                                return self.async_abort(reason="reauth_successful")

                            return self.async_create_entry(
                                title=f"Ather {scooter_model} ({vin})",
                                data={
                                    CONF_PHONE: self.phone,
                                    CONF_ATHER_TOKEN: ather_token,
                                    CONF_SCOOTER_UUID: scooter_uuid,
                                    CONF_VIN: vin,
                                    CONF_MODEL: scooter_model
                                }
                            )
                        else:
                            errors["base"] = "invalid_otp"
                    elif resp.status in [400, 401, 403]:
                        errors["base"] = "invalid_otp"
                    else:
                        errors["base"] = "api_error"
            except Exception as e:
                _LOGGER.error("Connection error during OTP verification: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({vol.Required("otp"): str}),
            errors=errors
        )

    async def async_step_reauth(self, entry_data):
        self.phone = entry_data[CONF_PHONE]
        return await self.async_step_user()