from homeassistant import config_entries
from custom_components.eg4_inverter.config_flow import ConfigFlow
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_config_flow(hass):
    flow = ConfigFlow()
    result = await flow.async_step_user({
        "username": "test_user",
        "password": "test_password",
        "serial_number": "12345",
        "plant_id": "67890"
    })

    assert result["type"] == "create_entry"
    assert result["title"] == "EG4 Inverter"