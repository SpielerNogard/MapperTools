import json
import logging
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, ip: str):
        self._ip = ip
        self._connected = False
        self._arch = ""
        self._type = "Android"
        self._stats: Dict[str, Any] = {}

        self._load_device()

    @property
    def stats(self) -> Dict[str, Any]:
        self._stats["ip"] = self._ip
        self._stats["arch"] = self._arch
        return self._stats

    @property
    def name(self):
        return self._stats.get("DeviceName", self._stats.get("IP", "0.0.0.0"))

    def _load_device(self) -> None:
        with open("devices.json") as device_stats:
            content = json.load(device_stats)
        self._stats = content.get(self._ip, {})
        logger.info(f"loaded {self._stats=}")

    def adb_command(self, command: str, command_output: bool = True) -> Optional[str]:
        if not self._connected:
            logger.warning(f"{self._ip} is not connected.")
            self.connect()
        logger.info(f"using {command=}")
        if command_output:
            output = subprocess.check_output(
                command,
                shell=True,
            )
            output = output.decode("utf-8").replace("\n", "")
            logger.info(f"{output}")
            return output
        else:
            subprocess.call(command, shell=True)

    def connect(self) -> None:
        command = f"adb connect {self._ip}:5555"
        output = subprocess.check_output(
            command,
            shell=True,
        )
        output = output.decode("utf-8").replace("\n", "")
        logger.info(f"{output}")
        if "connected" in output:
            self._connected = True

    def disconnect(self) -> None:
        output = self.adb_command(f"adb disconnect {self._ip}:5555")
        if "disconnected" in output:
            self._connected = False

    def reboot(self) -> None:
        self.adb_command(f"adb -s {self._ip}:5555 shell reboot", command_output=False)
        self._connected = False

    def force_stop(self, service: str) -> None:
        self.adb_command(
            f"adb -s {self._ip}:5555 shell su -c am force-stop {service}",
            command_output=False,
        )

    def start_service(self, service: str) -> None:
        """
        Method to start a service on device.

        Parameters
        ----------
        service : str
            service to start.
        """
        self.adb_command(
            f"adb -s {self._ip}:5555 shell su -c am startservice {service}",
            command_output=False,
        )

    def get_arch(self) -> str:
        """
        Method to get the architecture for device.

        Returns
        -------
        str
            architecture for device.
        """
        output = self.adb_command(
            f"adb -s {self._ip}:5555 shell getprop ro.product.cpu.abi"
        )
        self._arch = output
        logger.info(f"found architecture {self._arch}")
        return self._arch

    def get_software_version(self, package: str) -> str:
        """
        Method to get the current installed software version for package.

        Parameters
        ----------
        package : str
            full package name to search for.

        Returns
        -------
        str
            installed version of package.
        """
        output = self.adb_command(
            f"adb -s {self._ip}:5555 shell dumpsys package {package} | grep versionName"
        )
        output = output.replace("versionName=", "")
        output = output.replace(" ", "")
        self._stats[package] = output
        logger.info(f"found version for {package=} {output}")
        return output

    def search_package(self, package: str) -> bool:
        """
        Method to search if a package is installed in device.

        Parameters
        ----------
        package : str
            full package to search for.

        Returns
        -------
        bool
            `True` if package is installed.
            `False` if package is not installed.
        """
        logger.info(f"searchig for {package}")
        try:
            self.adb_command(command=f"adb shell pm list packages | grep {package}")
            logger.info("found")
            return True
        except subprocess.CalledProcessError:
            logger.info("not found")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Method to get the current device status.

        Returns
        -------
        Dict[str, Any]
            dict representing the current device status.
            includes the keys `type` and `Architecture`.
        """
        logger.info(f"building status for {self._ip}")
        status = {
            "type": self._type,
            "Architecture": self.get_arch(),
            "IP": self._ip,
        }
        self._status = status
        return status

    def install_apk(self, apk: str):
        """
        Method to install an apk to device.

        Parameters
        ----------
        apk : str
            name of apk to install.
        """
        self.adb_command(command=f"adb install -r {apk}")

    def install_package(self, apks: List[str]):
        """
        Method to install and app package to device.

        Parameters
        ----------
        apks : List[str]
            an package consist multiple apks, that need to be installed in one session.
            input the apk names as list of strings.
        """
        self.adb_command(command=f"adb install-multiple -r {','.join(apks)}")
