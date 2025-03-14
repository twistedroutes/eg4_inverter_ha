
# EG4 Inverter Integration for Home Assistant

This custom component integrates an **EG4 Inverter** with Home Assistant. It enables you to monitor inverter metrics and status updates right from your Home Assistant dashboard.

## Features

- Retrieves status and production metrics from an EG4 Inverter.
- Allows you to expose the inverter’s data to Home Assistant sensors.
- Easy setup and configuration via `configuration.yaml`.

## Requirements

- **Home Assistant** 2022.5 or later (earlier versions may work, but are untested).
- A working EG4 Inverter on your local network.

## Installation

### 1. Download the files
You can download this custom component directly from GitHub:

**[Download ZIP](https://github.com/twistedroutes/eg4_inverter_ha/archive/refs/heads/main.zip)**

Once downloaded, unzip the folder.

### 2. Copy to Home Assistant
1. In your Home Assistant configuration directory (usually `~/.homeassistant` on Linux), navigate to the `custom_components` folder. If it does not exist, create it.
2. Copy the entire `eg4_inverter` folder (including all files) into the `custom_components` folder. Your final structure should look like:
```
config/
├── custom_components/
│   └── eg4_inverter/
│       ├── __init__.py
│       ├── manifest.json
│       ├── services.yaml
│       └── ...
├── configuration.yaml
```

### 3. Configure Home Assistant
GO to Settings -> Devices & Services -> "+ Add Integration" and search for EG4.  You can also add your settings to `configuration.yaml`:

```yaml
eg4_inverter:
  ....
```

### 4. Restart Home Assistant
After updating `configuration.yaml` or adding the integration through the UI:
1. **Restart** Home Assistant.
2. Check the **Logs** to confirm the component loaded correctly.

## Usage

Once restarted, the **EG4 Inverter** sensors should appear in the Home Assistant **Developer Tools** → **States**. You can then add these sensors to your **Lovelace** dashboards, automations, or any other place you need them.

## Contributing

If you have improvements or encounter issues:
1. Fork this repository.
2. Create a new branch for your feature or bugfix.
3. Submit a Pull Request detailing your changes.

## Disclaimer

This integration is provided as-is and is not an official product of EG4 or Home Assistant. Use at your own discretion and verify that the component works correctly in your own environment.

## TODO


I've got to write up some tests, validate the data scaling (e.g. where EG4 provide 5100 to represent 51.00 V), likely create a few virtual sensors (a sensor made from other sensors data, like capacity in KWh = voltage and capacity in amp-hours).

Then add some switches and inputs to change data

Then add an example dashboard (though this data can already be used in the Energy dashboard)

