# Ather Energy Custom Integration for Home Assistant

This is a custom Home Assistant integration that connects directly to your Ather smart scooter over native WebSockets to stream live, real-time data. No need for clumsy MQTT setups, external bridges, or companion scripts.

## What it tracks
* **Real-Time Data:** Telemetry updates instantly the second your scooter changes states (e.g., switching from Sleeping to Riding or Charging).
* **15+ Sensors:** Keeps tabs on your Battery State-of-Charge (SoC), estimated range for different riding modes, odometer, charging types, and system alerts.
* **Live Mapping:** Provides a `device_tracker` entity so you can see your scooter's live location (latitude, longitude, and accuracy) right on your Home Assistant map cards.
* **Clean Organization:** Diagnostic info (like software versions and privacy toggles) are automatically hidden away in diagnostic tabs so they don't clutter your main dashboard.

## 🔒 Privacy & Data Security
Your data belongs to you. This integration runs entirely locally on your Home Assistant instance. **No data is ever stored, collected, or tracked by any third-party services.** All communication happens strictly and directly between your Home Assistant hardware and the official Ather cloud servers.

## ⚠️ Disclaimer & Current State
**This is a very early, experimental, and fragile build.** Because this integration relies on reverse-engineered API signatures to communicate with Ather's cloud (including working around Google Firebase gates via the mobile app's signature), **it can break at any time** if Ather changes their backend. 

Please use this with that expectation in mind! 

*This project is an independent community development and is not officially affiliated with or endorsed by Ather Energy.*

## 🛵 Supported Models & Call for Testers!
Right now, this integration has **only been tested on the Ather 450X**, as that is the only vehicle I own. 

While Ather uses a unified mobile app backend, I am currently unsure if other models—like the **Ather Rizta, 450 Apex, or older generations of the 450/450X**—send the exact same telemetry data layout. 

If you own a Rizta, Apex, or an older 450 model and want to help make this integration work flawlessly for everyone:
1. Try installing it and see what works or breaks.
2. Open an Issue with your vehicle model and any logs or data anomalies you notice.
3. Sharing your anonymized data layouts/payloads will help me expand and fix the script for all models!

## 🤝 Contributions & Feedback Welcome!
Since this is an early build, things will break, and there is plenty of room for improvement. If you find a bug, have a feature suggestion, or want to help improve the code:
* Please feel free to **open an Issue** or submit a **Pull Request (PR)**. 
* All feedback, suggestions, and code improvements are incredibly welcome!

## Installation Instructions

### Method 1: HACS Custom Repository (Recommended)
Since this integration isn't in the official HACS default store yet, you can easily add it manually:

1. Make sure you have **HACS** installed and working.
2. Open **HACS** ➔ Go to the **Integrations** tab.
3. Click the **three dots menu** in the top right corner and click **Custom Repositories**.
4. Paste this repository URL: `https://github.com/NoobPratik/ather-home-assistant`
5. Select **Integration** as the Category and click **Add**.
6. Click **Download** on the Ather Energy card that pops up.
7. **Restart** Home Assistant.

### Method 2: Manual Installation
1. Download the latest source code ZIP from this repository.
2. Extract it and copy the `ather` folder (found inside `custom_components/`) into your Home Assistant server's `/config/custom_components/` directory.
3. **Restart** Home Assistant.

## Initial Configuration
1. In Home Assistant, go to **Settings** ➔ **Devices & Services** ➔ **Add Integration**.
2. Search for and select **Ather Energy**.
3. Type in your registered Ather account **Phone Number** and hit Submit.
4. You will receive an automated SMS **OTP** (One-Time Password) on your phone. Enter it into the next box and click Submit.
5. The integration will automatically find your scooter's VIN and spin up all your dashboard entities instantly!
