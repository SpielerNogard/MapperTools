from tkinter.messagebox import NO
import requests
import json
import logging
import os
import pathlib

logger = logging.getLogger(__name__)


class UpdateChecker:
    def __init__(self) -> None:
        self._url = "https://raw.githubusercontent.com/SpielerNogard/MapperTools/main/version.json"

    def search_versions(self):
        response = requests.get(self._url)
        data = json.loads(response.text)
        return data

    def get_version(self, app: str):
        data = self.search_versions()
        return data.get(app)

    def need_update(self, current_version, found_version):
        if current_version is not None:
            return not current_version == found_version

    def check_devices(self, devices):
        logger.info("checking devices for Updates")
        versions = self.search_versions()
        for device in devices:
            status = device.get_status()
            self.check_for_updates(status, device, versions)

    def check_for_updates(self, status, device, versions):
        if status["type"] == "Atlas":
            if self.need_update(
                status.get("Atlas"), versions.get("Atlas", {}).get("Atlas")
            ):
                self._update_atlas_on_device(
                    device=device, version=versions.get("Atlas", {}).get("Atlas")
                )
            if self.need_update(
                status.get("Pogo"), versions.get("Atlas", {}).get("Pogo")
            ):
                self._update_pogo_on_device(
                    device=device, version=versions.get("Atlas", {}).get("Pogo")
                )
        if status["type"] == "MAD":
            if self.need_update(
                status.get("PogoDroid"), versions.get("MAD", {}).get("PogoDroid")
            ):
                self._update_pd_on_device(
                    device=device, version=versions.get("MAD", {}).get("PogoDroid")
                )
            if self.need_update(
                status.get("Pogo"), versions.get("MAD", {}).get("Pogo")
            ):
                self._update_pogo_on_device(
                    device=device, version=versions.get("MAD", {}).get("Pogo")
                )
        logger.info("device is up to date")

    def download_apk(self, version):
        url = f"http://apks.hupemap.de/uploads/{version}.apk"
        r = requests.get(url, allow_redirects=True)
        open(f"/tmp/MapperTools/{version}.apk", "wb").write(r.content)
        logger.info(f"downloaded /tmp/MapperTools/{version}.apk")

    def _update_pogo_on_device(self, device, version):
        logger.info(f"Installing PoGO {version=} on {device.name}")
        version = version.replace(".", "_")
        if not os.path.exists(f"/tmp/MapperTools/{version}.apk"):
            logger.info(f"cant find PoGo {version=}. Downloading....")
            self.download_apk(version=version)
        device.install_apk(f"/tmp/MapperTools/{version}.apk")

    def _update_atlas_on_device(self, device, version):
        logger.info(f"Installing Atlas {version=} on {device.name}")
        version = version.replace(".", "_")
        if not os.path.exists(f"/tmp/MapperTools/{version}.apk"):
            logger.info(f"cant find Atlas {version=}. Downloading....")
            self.download_apk(version=version)
        device.install_apk(f"/tmp/MapperTools/{version}.apk")

    def _update_pd_on_device(self, device, version):
        logger.info(f"Installing PogoDroid {version=} on {device.name}")
        version = version.replace(".", "_")
        if not os.path.exists(f"/tmp/MapperTools/{version}.apk"):
            logger.info(f"cant find PogoDroid {version=}. Downloading....")
            self.download_apk(version=version)
        device.install_apk(f"/tmp/MapperTools/{version}.apk")
