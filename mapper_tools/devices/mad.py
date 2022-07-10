from mapper_tools.devices.device import Device
import logging

logger = logging.getLogger(__name__)


class MADDevice(Device):
    def __init__(self, ip: str):
        super().__init__(ip=ip)
        self._type = "MAD"
        self._state = ""

    def get_status(self):
        logger.info(f"building status for {self._ip}")
        status = {
            "type": self._type,
            "Pogo": self.get_software_version("com.nianticlabs.pokemongo"),
            "PogoDroid": self.get_software_version("com.mad.pogodroid"),
            "Architecture": self.get_arch(),
            "Status": self._state,
        }
        self._status = status
        return status
