import os
from mapper_tools.devices.device import Device
import logging
import json

logger = logging.getLogger(__name__)


class AtlasDevice(Device):
    def __init__(self, ip: str):
        super().__init__(ip=ip)
        self._type = "Atlas"
        self._state = ""

    def get_status(self):
        logger.info(f"building status for {self._ip}")
        status = {
            "type": self._type,
            "Pogo": self.get_software_version("com.nianticlabs.pokemongo"),
            "Atlas": self.get_software_version("com.pokemod.atlas"),
            "Architecture": self.get_arch(),
            "DeviceName": self.get_device_name(),
            "Status": self._state,
            "IP": self._ip,
        }
        self._status = status
        return status

    def get_device_name(self):
        self.adb_command(
            f"adb -s {self._ip}:5555 pull /data/local/tmp/atlas_config.json",
            command_output=False,
        )
        with open("atlas_config.json") as json_file:
            content = json.load(json_file)
        os.remove("atlas_config.json")
        return content.get("deviceName")

    def reset(self):
        self.force_stop("com.nianticlabs.pokemongo")
        self.force_stop("com.pokemod.atlas")
        self.start_service(
            "com.pokemod.atlas/com.pokemod.atlas.services.MappingService"
        )
