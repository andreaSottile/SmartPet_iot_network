TOPIC_ACTUATOR_HATCH = "hatch_actuator"
TOPIC_ACTUATOR_FOOD = "food_actuator"
TOPIC_SENSOR_HATCH = "hatch_sensor"
TOPIC_SENSOR_HEARTBEAT = "heart_sensor"
TOPIC_SENSOR_FOOD = "food_sensor"
TOPIC_ID_CONFIG = "id_config"
# Hatch sensor message:
DEFAULT_SENSOR_HATCH_MSG = "hatch:%d;direction:%d"
DEFAULT_SENSOR_HEARTBEAT_MSG = "pet:%d;freq:%d"
DEFAULT_SENSOR_FOOD_MSG = "bowl:%d;food-level:%d"

# Commands
COMMAND_OPEN_HATCH = "open_hatch"
COMMAND_CLOSE_HATCH = "closed_hatch"
COMMAND_REFILL_START_FOOD = "start_refill"
COMMAND_REFILL_STOP_FOOD = "stop_refill"

COMMAND_ID_REGISTER = "%s %d awakens"
COMMAND_ID_DENY = "%s %d denied"

debug_mode = False
