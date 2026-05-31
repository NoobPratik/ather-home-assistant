import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_PHONE, CONF_ATHER_TOKEN, CONF_SCOOTER_UUID, CONF_VIN, CONF_MODEL, BASE_URL, HEADERS_BASE

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
            
            payload = {"contact_no": self.phone, "country_code": self.country_code, "email": "", "notification_medium": {"sms": True, "whatsapp": False}}
            async with session.post(f"{BASE_URL}/auth/v2/generate-login-otp", json=payload, headers=HEADERS_BASE) as resp:
                data = await resp.json()
                if "attemptsLeft" in data:
                    return await self.async_step_otp()
                else:
                    errors["base"] = "otp_failed"

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
            
            payload = {"contact_no": self.phone, "country_code": self.country_code, "email": "", "userOtp": otp, "is_mobile_login": True}
            async with session.post(f"{BASE_URL}/auth/v2/verify-login-otp", json=payload, headers=HEADERS_BASE) as resp:
                data = await resp.json()
                if data.get("status") == "success":
                    ather_token = data["token"]
                    
                    auth_headers = HEADERS_BASE.copy()
                    auth_headers["Authorization"] = f"Bearer {ather_token}"
                    
                    async with session.get(f"{BASE_URL}/api/v2/auth/user/scooters/firebase-dbs", headers=auth_headers) as shard_resp:
                        shard_data = await shard_resp.json()
                        scooter_uuid = shard_data["shardDetails"][0]["scooter_uuid"]
                        
                    async with session.get(f"{BASE_URL}/api/v1/devices/shadows/scooters/properties", headers=auth_headers, params={"uuid": scooter_uuid, "state": "reported"}) as props_resp:
                        props = (await props_resp.json()).get("data", {})
                        vin = props.get("vin", "Unknown_VIN")
                        scooter_model = props.get("model_type", "EV Scooter").strip()

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

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({vol.Required("otp"): str}),
            errors=errors
        )