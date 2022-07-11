from mapper_tools.core.commander import DeviceCommander
from mapper_tools.core.update_checker import UpdateChecker
from mapper_tools.logging.atlas_logger import AtlasLogger

AtlasLogger()
commander = DeviceCommander(search_devices=False)


from mapper_tools.logging.atlas_logger import AtlasLogger
from mapper_tools.devices.atlas import AtlasDevice

AtlasLogger()
device = AtlasDevice(ip="192.168.44.29")
checker = UpdateChecker()
checker.check_devices(devices=[device])
