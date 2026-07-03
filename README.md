# ⚡ Ather Energy

![Ather Banner](https://inc42.com/wp-content/uploads/2020/01/Untitled-design-2020-01-29T150600.950.jpg)

[![GitHub Release](https://img.shields.io/github/v/release/NoobPratik/ather-home-assistant?style=for-the-badge&logo=github&logoColor=white&label=RELEASE&color=10B981)](https://github.com/NoobPratik/ather-home-assistant/releases)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/NoobPratik/ather-home-assistant/total?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=2341BDF5&label=HACS%20Downloads&color=341BDF5)
[![License](https://img.shields.io/github/license/NoobPratik/ather-home-assistant?style=for-the-badge&logo=scroll&logoColor=white&label=LICENSE&color=orange)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**Home Assistant integration for Ather Energy smart scooters (450X, Rizta, Apex).**

Connects directly to your Ather scooter over native WebSockets to stream live, real-time data. No MQTT, no external bridges, no companion scripts.

---

## ✨ Features

- ✅ **Live Real-Time Data** — Telemetry updates instantly via WebSocket when your scooter changes state (Sleeping, Riding, Charging, etc.)
- ✅ **15+ Sensors** — Battery SOC, estimated range (per ride mode), odometer, tyre pressure, charging status, ride mode, and more
- ✅ **Live Location Tracking** — `device_tracker` entity for real-time GPS position on your map
- ✅ **Binary Sensors** — Alerts for incognito mode, smart eco, charger connection, and low tyre pressure
- ✅ **Service Tracking** — Log your last service odometer reading and get an automatic countdown to your next service
- ✅ **Automatic Reconnection** — WebSocket auto-reconnects on drop; triggers re-auth if token expires
- ✅ **Simple Setup** — Phone number + OTP, auto-detects VIN and scooter model

---

## Available Sensors

### Numerical Sensors

| Sensor              | Unit | Description                                                                 |
| ------------------- | ---- | --------------------------------------------------------------------------- |
| Battery Level       | %    | Current battery state of charge                                             |
| Estimated Range     | km   | Predicted range for current riding mode                                     |
| Odometer            | km   | Total distance travelled                                                    |
| Vehicle State       |      | Current state (Sleeping, Riding, Charging, etc.)                            |
| Active Ride Mode    |      | Eco, Ride, Sport, Warp, etc.                                                |
| Front Tyre Pressure | psi  | Front tyre pressure                                                         |
| Rear Tyre Pressure  | psi  | Rear tyre pressure                                                          |
| Charging Status     |      | Charging state (Charging, Not Charging, etc.)                               |
| Charger Type        |      | Type of charger connected                                                   |
| Next Service At     | km   | Odometer reading at which your next service is due (last service + 5000 km) |
| Next Service After  | km   | Distance remaining until your next service is due                           |

### Binary Sensors

| Sensor               | Description                         |
| -------------------- | ----------------------------------- |
| Incognito Mode       | Privacy mode active                 |
| Smart Eco Mode       | Smart Eco assist active             |
| Charger Connected    | Charger physically plugged in       |
| Front Tyre Low Alert | Front tyre pressure below threshold |
| Rear Tyre Low Alert  | Rear tyre pressure below threshold  |

### Device Tracker

| Entity         | Description                               |
| -------------- | ----------------------------------------- |
| Ather Location | Real-time GPS coordinates of your scooter |

### Button

| Entity           | Description                                                                          |
| ---------------- | ------------------------------------------------------------------------------------ |
| Record Servicing | Press after a service to log the current odometer reading as your last service point |

### Number

| Entity          | Unit | Description                                                                                  |
| --------------- | ---- | -------------------------------------------------------------------------------------------- |
| Last Service At | km   | Odometer reading at your last service. Editable, and persists across Home Assistant restarts |

---

## 🔧 Service Tracking

Press **Record Servicing** right after your scooter's serviced to log the current odometer reading. The integration then tracks your next due service based on Ather's standard 5000 km interval, and the **Next Service After** sensor shows how far you have left.

You can also manually set or correct the **Last Service At** value at any time using its number entity — handy if you're onboarding the integration after already having some service history.

---

## 🔒 Privacy & Data Security

Your data belongs to you. This integration runs entirely locally on your Home Assistant instance. **No data is ever stored, collected, or tracked by any third-party services.** All communication happens directly between your Home Assistant and the official Ather cloud servers.

---

## ⚠️ Disclaimer

This integration is **not affiliated with, endorsed by, or sponsored by Ather Energy.** It uses reverse-engineered API signatures and can break at any time if Ather changes their backend.

_This is an independent community project._

---

## 🚀 Installation

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=NoobPratik&repository=ather-home-assistant&category=integration)

Since this integration isn't in the default HACS store yet, add it as a custom repository:

1. Open **HACS** → **Integrations**
2. Click the **three dots menu** (top right) → **Custom Repositories**
3. Paste: `https://github.com/NoobPratik/ather-home-assistant`
4. Select **Integration** as the Category → **Add**
5. Click **Download** on the Ather Energy card
6. **Restart** Home Assistant

### Option 2: Manual

1. [Download the latest release](https://github.com/NoobPratik/ather-home-assistant/releases)
2. Extract the `ather` folder from `custom_components/` into your `config/custom_components/`
3. **Restart** Home Assistant

---

## ⚙️ Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ather)

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for and select **Ather Energy**
3. Enter your registered Ather account **phone number**
4. Enter the **OTP** sent to your phone
5. The integration automatically detects your VIN and scooter model
6. Sensors and device tracker appear instantly on your dashboard

---

## 🛵 Supported Models

| Model               | Status                     |
| ------------------- | -------------------------- |
| Ather 450X          | ✅ Tested                  |
| Ather Rizta         | ⚠️ Untested — likely works |
| Ather 450 Apex      | ⚠️ Untested — likely works |
| Ather 450 (Gen 1/2) | ⚠️ Untested — unknown      |

If you own a different model, please [open an issue](https://github.com/NoobPratik/ather-home-assistant/issues) with logs and data payloads to help expand compatibility!

---

## Requirements

- Home Assistant 2024.10.0 or higher
- Python 3.12+
- Ather Energy smart scooter with active Ather account
- Registered mobile number with Ather

---

## Data Flow

```
Ather Cloud (WebSocket) ← → Home Assistant
        ↓
  AtherDataCoordinator (in-memory cache + persistent service data)
        ↓
  Sensors / Binary Sensors / Device Tracker / Button / Number
        ↓
  Dispatcher updates all entities in real-time
```

Data is pushed from Ather's cloud via WebSocket the instant your scooter changes state — no polling required. Service tracking data (last service odometer reading) is separately persisted to disk so it survives Home Assistant restarts.

---

## 🤝 Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

- [Report a Bug](https://github.com/NoobPratik/ather-home-assistant/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/NoobPratik/ather-home-assistant/issues/new?template=feature_request.md)

---

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=NoobPratik/ather-home-assistant&type=date&legend=top-left)](https://www.star-history.com/?repos=NoobPratik%2Father-home-assistant&type=date&legend=top-left)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

_If you find this integration useful, please consider giving it a star on GitHub!_
