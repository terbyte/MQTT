import os
import subprocess
import sys
import time
import ctypes
import pathlib
import elevate
from elevate import elevate
import getpass
from ctypes import *
# from gpioscanner_functions import *



dll_name = 'libs/libSUSI-4.00.so'
libsusi = ctypes.CDLL(pathlib.Path().absolute() / dll_name)

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








def susi_input_is_activated(gpio):
	gpio_direction = susi_get_gpio_direction(gpio)
	if gpio_direction != "INPUT":
		return 0#False
	gpio_level = susi_get_gpio_level(gpio)
	if gpio_level != "LOW":
		return 0#False
	else:
		return 1#True

def susi_set_gpio_direction(Id, Direction):
    # set SUSI function to call
    susifunc = libsusi.SusiGPIOSetDirection
    # uint32_t SusiGPIOSetDirection(uint32_t Id, uint32_t Bitmask, uint32_t Direction)
    susifunc.argtypes = [c_uint32, c_uint32, c_uint32]
    susifunc.restype = c_uint32
    # call susifunc
    status = susifunc(Id, 0, Direction)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    return True 	



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
# set level=HIGH, for a number of seconds (Delay) then set back Level=LOW
def susi_trigger(Id, Delay):
    susi_set_gpio_level(Id, SUSI_GPIO_HIGH)
    time.sleep(Delay)
    susi_set_gpio_level(Id, SUSI_GPIO_LOW)
    print("done trigger")

def susi_set_gpio_level(Id, Level):
    # set SUSI function to call
    susifunc = libsusi.SusiGPIOSetLevel
    # uint32_t SusiGPIOSetLevel(uint32_t Id, uint32_t Bitmask, uint32_t Level)
    susifunc.argtypes = [c_uint32, c_uint32, c_uint32]
    susifunc.restype = c_uint32
    # call susifunc
    status = susifunc(Id, 0, Level)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    return True 

# get GPIOx level (1=high; 0=low)
def susi_get_gpio_level(Id):
    # set SUSI function to call
    susifunc = libsusi.SusiGPIOGetLevel
    # uint32_t SusiGPIOGetLevel(uint32_t Id, uint32_t Bitmask, uint32_t *pLevel)
    susifunc.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
    susifunc.restype = c_uint32
    pLevel = c_uint32()
    # call susifunc
    status = susifunc(Id, 0, pLevel)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    if pLevel.value == 0:
        return "LOW"
    if pLevel.value == 1:
        return "HIGH"
    return pLevel.value       

# get GPIOx direction (1=input; 0=output)
def susi_get_gpio_direction(Id):
    # set SUSI function to call
    susifunc = libsusi.SusiGPIOGetDirection
    # uint32_t SusiGPIOGetDirection(uint32_t Id, uint32_t Bitmask, uint32_t *pDirection)
    susifunc.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
    susifunc.restype = c_uint32
    pDirection = c_uint32()
    # call susifunc
    status = susifunc(Id, 0, pDirection)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    if pDirection.value == 0:
        return "OUTPUT"
    if pDirection.value == 1:
        return "INPUT"
    return pDirection.value



tfile="TRIG.txt"
gfolder ="templates"
gfile ="GPIO.txt"
gpath=pathlib.Path().absolute()/gfolder/gfile
print(gpath)
abs_path=os.path.dirname(pathlib.Path().absolute())
# print(abs_path)
FILENAME =abs_path+'/'+tfile
print(FILENAME)
def get_moddate():
    return os.stat(FILENAME)[8]



elevate(graphical=False)
load_susi = libsusi.SusiLibInitialize()
if (load_susi == SUSI_STATUS_ERROR):
	print("SusiLibInitialize() failed! ROOT privileges required.")
if (load_susi != SUSI_STATUS_SUCCESS and load_susi != SUSI_STATUS_INITIALIZED):
	print(susi_code_description(load_susi))
print("SUSI initialized successfully! -gpio_scanner.py")
susi_set_gpio_direction(SUSI_ID_GPIO0, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO1, SUSI_GPIO_OUTPUT)
susi_set_gpio_direction(SUSI_ID_GPIO2, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO3, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO4, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO5, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO6, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO7, SUSI_GPIO_INPUT)
susi_set_gpio_direction(SUSI_ID_GPIO8, SUSI_GPIO_INPUT)
susi_trigger(SUSI_ID_GPIO1, 0.5)
last_value=0
moddate=get_moddate()
while True:

	val_pin0 = susi_input_is_activated(SUSI_ID_GPIO0)
	val_pin1 = susi_input_is_activated(SUSI_ID_GPIO1)
	val_pin2 = susi_input_is_activated(SUSI_ID_GPIO2)
	val_pin3 = susi_input_is_activated(SUSI_ID_GPIO3)
	val_pin4 = susi_input_is_activated(SUSI_ID_GPIO4)
	val_pin5 = susi_input_is_activated(SUSI_ID_GPIO5)
	val_pin6 = susi_input_is_activated(SUSI_ID_GPIO6)
	val_pin7 = susi_input_is_activated(SUSI_ID_GPIO7)
	val_pin8 = susi_input_is_activated(SUSI_ID_GPIO8)

	val0 =val_pin0 * (2**0)
	val1 =val_pin1 * (2**1)
	val2 =val_pin2 * (2**2)
	val3 =val_pin3 * (2**3)
	val4 =val_pin4 * (2**4)
	val5 =val_pin5 * (2**5)
	val6 =val_pin6 * (2**6)
	val7 =val_pin7 * (2**7)
	val8 =val_pin8 * (2**8)

	gpio_value =val8+val7+val6+val5+val4+val3+val2+val1+val0

	moddate2 = get_moddate()
	if moddate != moddate2:
		print('file has changed')
		moddate = moddate2
		susi_trigger(SUSI_ID_GPIO1, 0.5)

	
	if gpio_value!=last_value:
		last_value=gpio_value
		with open(gpath, 'w')  as f:
			f.write(str(gpio_value))
		print(gpio_value)
			
	
	time.sleep(0.2)