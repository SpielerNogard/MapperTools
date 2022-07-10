import os
from posixpath import split
from sys import platform
import subprocess
import logging
from threading import local
from tokenize import Triple
import mapper_tools.core.errors as errors
from mapper_tools.devices.atlas import AtlasDevice
from mapper_tools.devices.device import Device
from mapper_tools.devices.mad import MADDevice
from mapper_tools.logging.atlas_logger import AtlasLogger
from shutil import which
import socket
import json


logger = logging.getLogger(__name__)


class DeviceCommander:
    def __init__(self, search_devices: bool = True):
        self._devices = {}
        self._platform = self._check_platform()
        self._search = search_devices
        self._check_for_adb()

        self._ip_range = self._find_ip_range()
        self.check_for_devices()

    @staticmethod
    def _check_platform():
        supported_systems = {"linux": "linux", "darwin": "mac", "win32": "windows"}
        logger.info("checking platform")
        my_platform = supported_systems.get(platform)
        logger.info(f"found {my_platform}")
        if my_platform:
            return my_platform
        raise errors.UnsupportedOS(f"found unsupported os: {platform}")

    @staticmethod
    def _check_for_adb():
        logger.info(f"searching for adb")
        adb = which("adb")
        if adb:
            logger.info(f"adb is installed: {adb}")
        else:
            logger.warning("adb is not installed")
            errors.ADBNotFound(f"cant find ADB in path.")

    @staticmethod
    def _find_ip_range():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"my ip: {local_ip}")
        splitted_ip = local_ip.split(".")
        splitted_ip.pop()
        ip_range = ".".join(splitted_ip)
        logger.info(f"found ip range: {ip_range}")
        return ip_range

    @staticmethod
    def _check_open_port(host):
        port = 5555
        s = socket.socket()
        try:
            s.settimeout(0.4)
            s.connect((host, port))
            logger.info(f"{host} is android device")
            s.close()
            return True
        except (ConnectionRefusedError, socket.timeout):
            logger.info(f"{host} no android device")
            return False

    def check_for_devices(self):
        if self._search:
            found_devices = {}
            for a in range(1, 255):
                if self._check_open_port(f"{self._ip_range}.{a}"):
                    device = Device(ip=f"{self._ip_range}.{a}")
                    if device.search_package("com.pokemod.atlas"):
                        device = AtlasDevice(ip=f"{self._ip_range}.{a}")
                        status = device.get_status()
                    elif device.search_package("com.mad.pogodroid"):
                        device = MADDevice(ip=f"{self._ip_range}.{a}")
                        status = device.get_status()
                    else:
                        status = device.get_status()
                    found_devices[f"{self._ip_range}.{a}"] = status
                    device.disconnect()
            with open("devices.json", "w") as device_file:
                device_file.write(json.dumps(found_devices))
        else:
            with open("devices.json") as device_stats:
                found_devices = json.load(device_stats)
        logger.info(f"{found_devices}")
        self._devices = found_devices
