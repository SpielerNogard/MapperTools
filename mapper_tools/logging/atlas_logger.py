import logging


class AtlasLogger:
    def __init__(self, log_level=logging.INFO):
        self._log_level = log_level
        self._tags = ""
        self.activate_logger()

    def activate_logger(self):
        base_format: str = (
            f"[%(levelname)s] "
            f"[%(name)s.%(funcName)s line:%(lineno)d]"
            f" {self._tags} %(message)s"
        )
        logging.basicConfig(
            format=base_format,
            datefmt="%Y-%m-%d %H:%M:%S%z",
            level=self._log_level,
            force=True,
        )

    def add_tag(self, tag: str):
        self._tags = f"{self._tags} [{tag}]"
        self.activate_logger()
