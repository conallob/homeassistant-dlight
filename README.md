# dLight Integration for Home Assistant

A modern Home Assistant integration for controlling Google's dLight smart light devices via local network API.

## Features

- UI-based configuration (no YAML needed)
- Brightness control (0-100%)
- Color temperature control (2600K-6000K / 167-385 mireds)
- Local polling for state updates
- HACS compatible

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots menu in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/conallob/homeassistant-dlight`
6. Select category "Integration"
7. Click "Add"
8. Find "dLight" in the integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/dlight` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "dLight"
4. Enter your dLight device details:
   - **Host IP Address**: The IP address of your dLight device
   - **Device ID**: Your dLight device ID
   - **Port**: Default is 3333 (usually no need to change)
5. Click "Submit"

Your dLight will now appear as a light entity that you can control.

## Usage

Once configured, you can:
- Turn the light on/off
- Adjust brightness
- Change color temperature

The integration works with all standard Home Assistant light controls, automations, and scenes.

## API Protocol

The dLight uses a JSON-based TCP socket protocol on port 3333 (default). Commands are sent as JSON objects and responses include a 4-byte length prefix.

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.
