''' SUSI4 Status Codes in decimal values'''
# not yet initialized. call SusiLibInitialize prior to access
SUSI_STATUS_NOT_INITIALIZED = -1            # Library not initialized
SUSI_STATUS_INITIALIZED = -2                # Library is initialized
SUSI_STATUS_ALLOC_ERROR = -3                # Memory Allocation Error
SUSI_STATUS_DRIVER_TIMEOUT = -4             # Timed out in driver
SUSI_STATUS_INVALID_PARAMETER = -257        # Invalid parameter used
SUSI_STATUS_INVALID_BLOCK_ALIGNMENT = -258  # Block Alignment is incorrect
SUSI_STATUS_INVALID_BLOCK_LENGTH = -259     # Block length is too long
SUSI_STATUS_INVALID_DIRECTION = -260        # GPIOs unsupported direction
SUSI_STATUS_INVALID_BITMASK = -261          # bitmask bits/GPIOs not supported
# function/ID not supported by hardware
SUSI_STATUS_UNSUPPORTED = -769
SUSI_STATUS_NOT_FOUND = -1025               # Selected device not found
SUSI_STATUS_TIMEOUT = -1026                 # Device has no response
# device/ID is busy or data collision detected
SUSI_STATUS_BUSY_COLLISION = -1027
SUSI_STATUS_READ_ERROR = -1281              # Error during a read operation
SUSI_STATUS_WRITE_ERROR = -1282             # Error during a write operation
# max buffer size exceeded. Storage buffer overflow was prevented
SUSI_STATUS_MORE_DATA = -1537
# Generic error message. No further error details are available
SUSI_STATUS_ERROR = -3841
SUSI_STATUS_SUCCESS = 0                     # The operation is successful

''' SUSI4 GPIO (digital IO) '''
# Single GPIO ID Mapping
SUSI_ID_GPIO_BASE = 0                   # Single GPIO
SUSI_ID_GPIO0 = 0                       # DIO pin-1
SUSI_ID_GPIO1 = 1                       # DIO pin-2
SUSI_ID_GPIO2 = 2                       # DIO pin-3
SUSI_ID_GPIO3 = 3                       # DIO pin-4
SUSI_ID_GPIO4 = 4                       # DIO pin-5
SUSI_ID_GPIO5 = 5                       # DIO pin-6
SUSI_ID_GPIO6 = 6                       # DIO pin-7
SUSI_ID_GPIO7 = 7                       # DIO pin-8
SUSI_ID_GPIO8 = 8                       # DIO pin-9; common ground
# Item ID; GPIO capabilities item ID, use in SusiGPIOGetCaps
SUSI_ID_GPIO_INPUT_SUPPORT = 0
SUSI_ID_GPIO_OUTPUT_SUPPORT = 1
# Levels
SUSI_GPIO_LOW = 0
SUSI_GPIO_HIGH = 1
# Directions
SUSI_GPIO_INPUT = 1
SUSI_GPIO_OUTPUT = 0

''' SUSI4 HWM (hardware monitor) '''
# Temp ID; Board temperature value ID, use in SusiBoardGetValue
SUSI_ID_HWM_TEMP_CPU = 131072           # CPU
SUSI_ID_HWM_TEMP_CHIPSET = 131073       # Chipset
SUSI_ID_HWM_TEMP_SYSTEM = 131074        # System
# Voltage ID; Board voltage value ID, use in SusiBoardGetValue
SUSI_ID_HWM_VOLTAGE_VCORE = 135168      # Vcore
SUSI_ID_HWM_VOLTAGE_5V = 135172         # 5V
SUSI_ID_HWM_VOLTAGE_12V = 135173        # 12V
SUSI_ID_HWM_VOLTAGE_VBAT = 135176       # CMOS Battery

''' SUSI4 Board Info '''
# Board ID; Board information string ID, use in SusiBoardGetStringA
SUSI_ID_BOARD_MANUFACTURER_STR = 0
SUSI_ID_BOARD_NAME_STR = 1
SUSI_ID_BOARD_BIOS_REVISION_STR = 4
# Board ID; Board information value ID, use in SusiBoardGetValue
SUSI_ID_BOARD_DRIVER_VERSION_VAL = 65536
SUSI_ID_BOARD_LIB_VERSION_VAL = 65537
SUSI_ID_BOARD_FIRMWARE_VERSION_VAL = 65538

SUSI_KELVINS_OFFSET = 2731
# ====================== End SUSI4 constants ====================== #

# a few more constants
BOARD_VER = 0                       # board version number
HWM_VOLT = 1                        # HWM voltage
HWM_TEMP = 2                        # HWM temperature


# Convert SUSI status code to its corresponding description
def susi_code_description(status):
    switcher = {
        SUSI_STATUS_NOT_INITIALIZED: "Error: SUSI library, not yet initialized.",
        SUSI_STATUS_INITIALIZED: "Ok:  SUSI library initialized.",
        SUSI_STATUS_ALLOC_ERROR: "Error: Memory allocation error.",
        SUSI_STATUS_DRIVER_TIMEOUT: "Error: Driver timed-out.",
        SUSI_STATUS_INVALID_PARAMETER: "Error: Invalid parameter passed.",
        SUSI_STATUS_INVALID_BLOCK_ALIGNMENT: "Error: The Block Alignment is incorrect.",
        SUSI_STATUS_INVALID_BLOCK_LENGTH: "Error: Block length is too long.",
        SUSI_STATUS_INVALID_DIRECTION: "Error: Invalid GPIO direction.",
        SUSI_STATUS_INVALID_BITMASK: "Error: Invalid GPIO bitmask.",
        SUSI_STATUS_UNSUPPORTED: "Error: Function or ID not supported for this hardware.",
        SUSI_STATUS_NOT_FOUND: "Error: Selected device was not found.",
        SUSI_STATUS_TIMEOUT: "Error: Device timed-out.",
        SUSI_STATUS_BUSY_COLLISION: "Error: Device or ID is busy.",
        SUSI_STATUS_READ_ERROR: "Error: Read operation.",
        SUSI_STATUS_WRITE_ERROR: "Error: Write operation.",
        SUSI_STATUS_MORE_DATA: "Error: Data exceeds the buffer size.",
        SUSI_STATUS_ERROR: "Error: Unknown.",
        SUSI_STATUS_SUCCESS: "Success.",
    }
    # return status description, if no match found above, return "nothing"
    return switcher.get(status, "nothing")
