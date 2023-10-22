"""
Taken from https://github.com/satoshi-anonymoto/whatsminer-api and
https://aws-microbt-com-bucket.s3.us-west-2.amazonaws.com/WhatsminerAPI%20V2.0.4.pdf
"""
import asyncio
import base64
import binascii
import dataclasses
import datetime
import hashlib
import json
import logging
import re
from base64 import b64decode
from typing import Any, Dict, Optional, List, cast

from Crypto.Cipher import AES
from passlib.hash import md5_crypt

logger = logging.getLogger(__name__)


class WhatsminerException(BaseException):
    pass


class InvalidCommand(WhatsminerException):
    pass


class InvalidResponse(WhatsminerException):
    pass


class InvalidAuth(WhatsminerException):
    pass


class InvalidMessage(WhatsminerException):
    pass


class UnsupportedVersion(WhatsminerException):
    pass


class ApiPermissionDenied(WhatsminerException):
    pass


class CommandError(WhatsminerException):
    pass


class TokenError(WhatsminerException):
    pass


class TokenExceeded(WhatsminerException):
    pass


class DecodeError(WhatsminerException):
    pass


class MinerOffline(WhatsminerException):
    pass


def _check_response(message, response):
    if "STATUS" not in response:
        raise InvalidResponse(response)
    if response["STATUS"] == "E":
        code = response["Code"]
        if code == 14:
            raise InvalidCommand(message, response.get("Msg", ""))
        if code == 23:
            raise InvalidMessage(message)
        if code == 45:
            raise ApiPermissionDenied(message)
        if code == 132:
            raise CommandError(message, response)
        if code == 135:
            raise TokenError()
        if code == 136:
            raise TokenExceeded()
        if code == 137:
            raise DecodeError(message)
        raise InvalidResponse(response)


class WhatsminerMachine(object):
    def __init__(self, host: str, port: int = 4028, admin_password: str = None):
        self.host = host
        self.port = port
        self._admin_password = admin_password
        self._token = None
        self._token_time = None
        self._cipher = None

    async def _communicate_raw(
            self, data: str, expect_response: bool = True
    ) -> Optional[str]:
        r, w = await asyncio.open_connection(host=self.host, port=self.port)
        logger.debug("Writing message %s", data)
        w.write(data.encode("utf-8"))
        try:
            if expect_response:
                response = (await r.readline()).decode("utf-8").strip()
                logger.debug("Received response %s", response)
                return response.replace(",}", "}")
        finally:
            w.close()

    async def communicate(
            self,
            cmd: str,
            additional: Optional[Dict[str, Any]] = None,
            encrypted=False,
            expect_response=True,
    ) -> Optional[Dict]:
        if additional:
            data = dict(additional)
        else:
            data = {}
        data["cmd"] = cmd
        if encrypted:
            data["token"] = await self._get_token()

        plain_message = json.dumps(data)
        if encrypted:
            enc_str = (
                base64.encodebytes(self._cipher.encrypt(pad(plain_message)))
                    .decode("utf-8")
                    .replace("\n", "")
            )
            message = json.dumps({"enc": 1, "data": enc_str})
        else:
            message = plain_message

        response = await self._communicate_raw(message, expect_response)
        if not expect_response:
            return None

        if response.strip() == "Socket connect failed: Connection refused":
            raise MinerOffline()
        try:
            json_response = json.loads(response)
        except json.JSONDecodeError as error:
            raise ValueError(f"Failed to parse response {response}") from error

        if encrypted:
            if json_response.get("Code", 0) == 23:
                raise InvalidAuth()
            try:
                resp_plaintext: str = (
                    self._cipher.decrypt(b64decode(json_response["enc"]))
                        .decode("utf-8")
                        .rstrip("\0\n ")
                )
                if not resp_plaintext:
                    raise InvalidResponse()
                plain_response = json.loads(resp_plaintext)
                _check_response(plain_message, plain_response)
                return plain_response
            except KeyError:
                raise InvalidResponse(response)

        _check_response(message, json_response)
        return json_response

    async def _get_token(self) -> str:
        """
        Encryption algorithm:
        Ciphertext = aes256(plaintext)，ECB mode
        Encode text = base64(ciphertext)

        (1)api_cmd = token,$sign|api_str    # api_str is API command plaintext
        (2)enc_str = aes256(api_cmd, $key)  # ECB mode
        (3)tran_str = base64(enc_str)

        Final assembly: enc|base64(aes256("token,sign|set_led|auto", $aes_key))
        """

        now = datetime.datetime.now()

        if (
                self._token_time is not None
                and (now - self._token_time).total_seconds() < 29 * 60
        ):
            return self._token

        message = json.dumps({"cmd": "get_token"})
        response = json.loads(await self._communicate_raw(message))
        _check_response(message, response)

        token_info = response["Msg"]
        key = crypt(self._admin_password, f"$1${token_info['salt']}$").split("$")[3]
        self._cipher = AES.new(
            binascii.unhexlify(hashlib.sha256(key.encode()).hexdigest().encode()),
            AES.MODE_ECB,
        )
        self._token = crypt(
            key + token_info["time"], f"$1${token_info['newsalt']}$"
        ).split("$")[3]
        self._token_time = now
        return self._token

    async def check(self):
        await self._get_token()


@dataclasses.dataclass
class Summary(object):
    elapsed: int
    average_hash_rate: float
    hash_rate_5s: float
    hash_rate_1m: float
    hash_rate_5m: float
    hash_rate_15m: float
    average_frequency: float
    target_frequency: float
    target_hash_rate: float

    accepted: int
    rejected: int

    temperature: float
    chip_temperature_minimum: float
    chip_temperature_maximum: float
    chip_temperature_average: float
    environment_temperature: float
    fan_speed_in: int
    fan_speed_out: int

    power: int
    power_rate: float
    power_mode: str

    pool_rejected_percent: float
    pool_stale_percent: float

    uptime: int
    security_mode: bool
    mac: str


@dataclasses.dataclass
class DeviceDetails(object):
    index: int
    name: str
    identifier: int
    driver: str
    kernel: str
    model: str


@dataclasses.dataclass
class PowerUnitDetails(object):
    name: str
    hardware_version: str
    software_version: str
    model: str
    # current_in: int
    # voltage_in: int
    # fan_speed: int
    # version: str
    # serial_number: str


@dataclasses.dataclass
class Version(object):
    api_version: str
    firmware_version: str


# @dataclasses.dataclass
# class MinerInfo(object):
#     ip_address: str
#     protocol: str
#     netmask: str
#     gateway: str
#     dns: str
#     hostname: str
#     mac: str


@dataclasses.dataclass
class MinerStatus(object):
    miner_online: bool
    firmware_version: str


class WhatsminerApi(object):
    def __init__(self, machine: WhatsminerMachine):
        self.machine = machine

    async def get_device_details(self) -> List[DeviceDetails]:
        response = await self.machine.communicate(
            "devdetails", encrypted=False, expect_response=True
        )
        try:
            return [
                DeviceDetails(
                    index=details["DEVDETAILS"],
                    name=details["Name"],
                    identifier=details["ID"],
                    driver=details["Driver"],
                    kernel=details["Kernel"],
                    model=details["Model"],
                )
                for details in response["DEVDETAILS"]
            ]
        except KeyError as error:
            raise InvalidResponse() from error

    async def get_summary(self) -> Summary:
        response = await self.machine.communicate(
            "summary", encrypted=False, expect_response=True
        )
        try:
            data = response["SUMMARY"][0]
            return Summary(
                elapsed=data["Elapsed"],
                average_hash_rate=round(data["MHS av"] / 1000),
                hash_rate_5s=round(data["MHS 5s"] / 1000),
                hash_rate_1m=round(data["MHS 1m"] / 1000),
                hash_rate_5m=round(data["MHS 5m"] / 1000),
                hash_rate_15m=round(data["MHS 15m"] / 1000),
                accepted=data["Accepted"],
                rejected=data["Rejected"],
                temperature=data["Temperature"],
                average_frequency=data["freq_avg"],
                fan_speed_in=data["Fan Speed In"],
                fan_speed_out=data["Fan Speed Out"],
                power=data["Power"],
                power_rate=data["Power_RT"],
                pool_rejected_percent=data["Pool Rejected%"],
                pool_stale_percent=data["Pool Stale%"],
                uptime=data["Uptime"],
                security_mode=data["Security Mode"] == 0,
                target_frequency=data["Target Freq"],
                target_hash_rate=data["Target MHS"] / 1000,
                environment_temperature=data["Env Temp"],
                power_mode=data["Power Mode"],
                chip_temperature_minimum=data["Chip Temp Min"],
                chip_temperature_maximum=data["Chip Temp Max"],
                chip_temperature_average=data["Chip Temp Avg"],
                mac=data["MAC"],
            )
        except KeyError as error:
            raise InvalidResponse() from error

    async def get_psu(self) -> PowerUnitDetails:
        response = await self.machine.communicate(
            "get_psu", encrypted=False, expect_response=True
        )
        try:
            data = response["Msg"]
            return PowerUnitDetails(
                name=data["name"],
                hardware_version=data["hw_version"],
                software_version=data["sw_version"],
                model=data["model"],
                # current_in=data["iin"],
                # voltage_in=data["vin"],
                # fan_speed=data["fan_speed"],
                # version=data["version"],
                # serial_number=data["serial_no"]
            )
        except KeyError as error:
            raise InvalidResponse() from error

    async def get_version(self) -> Version:
        response = await self.machine.communicate(
            "get_version", encrypted=False, expect_response=True
        )
        try:
            data = response["Msg"]
            return Version(api_version=data["api_ver"], firmware_version=data["fw_ver"])
        except KeyError as error:
            raise InvalidResponse() from error

    # async def get_info(self) -> MinerInfo:
    #     info = "ip,proto,netmask,gateway,gateway,dns,hostname,mac"
    #     response = await self.machine.communicate("get_miner_info", additional={"info": info},
    #                                               encrypted=False, expect_response=True)
    #     try:
    #         data = response["Msg"]
    #         return MinerInfo(
    #             ip_address=data["ip"],
    #             protocol=data["protocol"],
    #             netmask=data["netmask"],
    #             gateway=data["gateway"],
    #             dns=data["dns"],
    #             hostname=data["hostname"],
    #             mac=data["mac"],
    #         )
    #     except KeyError as error:
    #         raise InvalidResponse() from error

    async def get_status(self) -> MinerStatus:
        response = await self.machine.communicate(
            "status", encrypted=False, expect_response=True
        )
        try:
            data = response["Msg"]
            return MinerStatus(
                miner_online=data["btmineroff"] == "false",
                firmware_version=cast(str, data["Firmware Version"]).strip("'"),
            )
        except KeyError as error:
            raise InvalidResponse() from error

    async def restart_miner(self):
        await self.machine.communicate(
            "restart_btminer", encrypted=True, expect_response=True
        )

    async def power_off_miner(self):
        await self.machine.communicate(
            "power_off",
            additional={"respbefore": "true"},
            encrypted=True,
            expect_response=True,
        )

    async def power_on_miner(self):
        await self.machine.communicate("power_on", encrypted=True, expect_response=True)

    async def set_power_mode(self):
        await self.machine.communicate(
            "set_lower_power", encrypted=True, expect_response=True
        )

    async def reboot(self):
        await self.machine.communicate("reboot", encrypted=True, expect_response=True)

    async def set_target_frequency(self, percent: int):
        if not -10 <= percent <= 100:
            raise ValueError
        await self.machine.communicate(
            "set_target_freq",
            additional={"percent": str(percent)},
            encrypted=True,
            expect_response=True,
        )

    async def set_power_percent(self, percent: int):
        if not 0 <= percent <= 100:
            raise ValueError
        await self.machine.communicate(
            "set_power_pct",
            additional={"percent": str(percent)},
            encrypted=True,
            expect_response=True,
        )

    async def set_miner_fast_boot(self, enable: bool):
        await self.machine.communicate(
            "enable_cgminer_fast_boot" if enable else "disable_cgminer_fast_boot",
            encrypted=True,
            expect_response=True,
        )


class WhatsminerApi20(WhatsminerApi):
    def __init__(self, machine: WhatsminerMachine):
        super().__init__(machine)

    async def get_summary(self) -> Summary:
        response = await self.machine.communicate("summary", encrypted=False, expect_response=True)
        response_info = await self.machine.communicate("get_miner_info", {"info": "mac"})
        try:
            data = response["SUMMARY"][0]
            data_info = response_info["Msg"]
            return Summary(
                elapsed=data["Elapsed"],
                average_hash_rate=round(data["MHS av"] / 1000),
                hash_rate_5s=round(data["MHS 5s"] / 1000),
                hash_rate_1m=round(data["MHS 1m"] / 1000),
                hash_rate_5m=round(data["MHS 5m"] / 1000),
                hash_rate_15m=round(data["MHS 15m"] / 1000),
                accepted=data["Accepted"],
                rejected=data["Rejected"],
                temperature=data["Temperature"],
                average_frequency=data["freq_avg"],
                fan_speed_in=data["Fan Speed In"],
                fan_speed_out=data["Fan Speed Out"],
                power=data["Power"],
                power_rate=data["Power Rate"],
                pool_rejected_percent=data["Pool Rejected%"],
                pool_stale_percent=data["Pool Stale%"],
                uptime=data["Uptime"],
                security_mode=data["Security Mode"] == 0,
                target_frequency=data["Target Freq"],
                target_hash_rate=data["Target MHS"] / 1000,
                environment_temperature=data["Env Temp"],
                power_mode=data["Power Mode"],
                chip_temperature_minimum=data["Chip Temp Min"],
                chip_temperature_maximum=data["Chip Temp Max"],
                chip_temperature_average=data["Chip Temp Avg"],
                mac=data_info["mac"],
            )
        except KeyError as error:
            raise InvalidResponse() from error

    async def get_status(self) -> MinerStatus:
        response = await self.machine.communicate(
            "status", encrypted=False, expect_response=True
        )
        try:
            data = response["Msg"]
            return MinerStatus(
                miner_online=data["btmineroff"] == "false",
                firmware_version=cast(str, data["FirmwareVersion"]).strip("'"),
            )
        except KeyError as error:
            raise InvalidResponse() from error


# ================================ misc helpers ================================
def crypt(word, salt):
    standard_salt = re.compile("\\s*\\$(\\d+)\\$([\\w./]*)\\$")
    match = standard_salt.match(salt)
    if not match:
        raise ValueError("salt format is not correct")
    extra_str = match.group(2)
    result = md5_crypt.hash(word, salt=extra_str)
    return result


def pad(s):
    if len(s) % 16:
        s += "\0" * (16 - len(s) % 16)
    return str.encode(s, "utf-8")
