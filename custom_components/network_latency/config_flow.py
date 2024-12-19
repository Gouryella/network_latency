import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN
from . import DEFAULT_SCAN_INTERVAL

class NetworkLatencyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("ip"): str,
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)
