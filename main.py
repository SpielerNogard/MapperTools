from mapper_tools.core.commander import DeviceCommander
from mapper_tools.logging.atlas_logger import AtlasLogger

AtlasLogger()
commander = DeviceCommander(search_devices=False)
