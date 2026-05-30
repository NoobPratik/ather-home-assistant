# Ather Energy Custom Integration for Home Assistant

Stream live, real-time telemetry metrics from your Ather smart scooter directly into Home Assistant over native WebSockets. No external MQTT bridges or companion scripts required.

## Features Included
* **Real-Time Push Streams:** Telemetry updates instantly the millisecond your vehicle transitions states (Riding, Sleeping, Charging).
* **15+ Native Entities:** Monitors Battery State-of-Charge, Estimated Mode Range, Odometer tracking, Active Charging types, and semantic Binary Sensor troubleshooting alerts.
* **Live Device Mapping:** Generates a real-time `device_tracker` entity providing latitude, longitude, and accuracy updates straight to your Lovelace Map cards.
* **Advanced Entity Categories:** Diagnostic parameters (Software Versions, Privacy Toggles) are correctly bucketed into system diagnostic tabs to keep your main dashboard clean.

## Cryptographic Architecture & Disclaimer
This custom integration interacts directly with internal cloud endpoints utilizing standard dynamic reverse-engineered API signatures. To validate application authenticity against Google Firebase security gates during initialization, the integration utilizes the public cryptographic production signature fingerprint derived from the authoritative Android package archive (`com.athermobileapp`).

*Disclaimer: This project is an independent community development and is not officially affiliated with or endorsed by Ather Energy.*

## Installation Instructions

### Method 1: HACS Custom Repository (Recommended)
Because this integration is not yet indexed in the default HACS store, you can easily add it as a custom repository:

1. Ensure the **HACS** custom component is active in your Home Assistant ecosystem.
2. Open **HACS** ➔ Navigate to the **Integrations** tab.
3. Click the **three dots menu** in the top right corner and select **Custom Repositories**.
4. Paste this repository URL: `https://github.com/pratik2296/ather-home-assistant`
5. Select **Integration** as the Category and click **Add**.
6. The "Ather Energy" card will appear. Click **Download**.
7. **Restart** Home Assistant completely.

### Method 2: Manual Installation
1. Download the latest source package release archive from GitHub.
2. Extract the payload and copy the nested `custom_components/ather/` folder directly into your instance's internal server directory `/config/custom_components/`.
3. **Restart** Home Assistant completely.

## Initial Configuration
1. Navigate to **Settings** ➔ **Devices & Services** ➔ **Add Integration**.
2. Search and select **Ather Energy**.
3. A native UI Config Flow panel will prompt for your details:
   * **Phone Number:** Enter your registered account mobile number.
4. Click **Submit**. A secondary verification card will populate.
5. Input the automated SMS **OTP** (One-Time Password) received on your personal device.
6. Click **Submit**. The integration will automatically discover your vehicle's unique VIN, allocate database shards, and generate your dashboard entities instantly.
