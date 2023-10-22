import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.device_registry import format_mac

from .api import (
    WhatsminerMachine,
    ApiPermissionDenied,
    WhatsminerException,
    TokenExceeded,
    DecodeError,
    MinerOffline,
    WhatsminerApi,
    WhatsminerApi20, UnsupportedVersion
)
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_MAC

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
            self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            host, port, password = (
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_PASSWORD],
            )
            machine = WhatsminerMachine(host, port, password)
            try:
                await machine.check()
                api = await self.async_detect_api(machine)
                version = await api.get_version()
                summary = await api.get_summary()
            except (asyncio.TimeoutError, aiohttp.ClientError):
                _LOGGER.info("Cannot connect to miner")
                errors["base"] = "cannot_connect"
            except DecodeError:
                errors["base"] = "invalid_auth"
            except ApiPermissionDenied:
                errors["base"] = "api_denied"
            except TokenExceeded:
                errors["base"] = "token_exceeded"
            except MinerOffline:
                errors["base"] = "miner_offline"
            except UnsupportedVersion:
                errors["base"] = "unsupported_version"
            except WhatsminerException as e:
                _LOGGER.info("Unexpected miner exception", exc_info=e)
                errors["base"] = "unknown"
            except Exception as e:
                _LOGGER.warning("Unknown error", exc_info=e)
                errors["base"] = "unknown"
            else:
                if version.api_version != "whatsminer v1.4.0" and version.api_version[:-1] != "2.0.":
                    errors["base"] = "unsupported_version"
                else:
                    mac_address = format_mac(summary.mac)
                    await self.async_set_unique_id(mac_address)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Whatsminer", data={CONF_MAC: mac_address, **user_input}
                    )

        data_schema = {
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=4028): int,
            vol.Required(CONF_PASSWORD): str,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_detect_api(self, machine: WhatsminerMachine) -> WhatsminerApi:
        api = WhatsminerApi(machine)
        version = await api.get_version()

        if version.api_version == "whatsminer v1.4.0":
            return api

        if version.api_version[:-1] == "2.0.":
            return WhatsminerApi20(machine)

        raise UnsupportedVersion(version.api_version)
