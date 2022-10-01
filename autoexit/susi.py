'''
Created on Sept. 2020
@author: ISA
'''
import os
import subprocess
import sys
import time
import ctypes
import pathlib
from elevate import elevate
import getpass
from ctypes import *
from .susi_constants import *

# load library; Adjust path and filename as necessary
dll_name = 'libSUSI-4.00.so'
libsusi = ctypes.CDLL(pathlib.Path().absolute() / dll_name)

print(dll_name + " loaded sucessfully - susi.py")




# initializes SUSI
def susi_initialize():
    elevate(graphical=False)
    dll_name = 'libSUSI-4.00.so'
    libsusi = ctypes.CDLL(pathlib.Path().absolute() / dll_name)
    print(dll_name + " loaded sucessfully")

    # uint32_t SusiLibInitialize(void)
    status = libsusi.SusiLibInitialize()
    # abort if not enough linux privilege
    if (status == SUSI_STATUS_ERROR):
        sys.exit("SusiLibInitialize() failed! ROOT privileges required. Aborting!")
        
    # abort if not initialized
    if (status != SUSI_STATUS_SUCCESS and status != SUSI_STATUS_INITIALIZED):
        return susi_code_description(status)
    # proceed if no errors
    return True


# Un-initializes SUSI
def susi_uninitialize():
    elevate(graphical=False)
    # uint32_t SusiLibUninitialize(void)
    status = libsusi.SusiLibUninitialize()
    if (status != SUSI_STATUS_SUCCESS):
        return susi_code_description(status)
    return True


# get Name/string : board info
def susi_boardinfo_str(Id):
    elevate(graphical=False)
    # SUSI function to call
    susifunc = libsusi.SusiBoardGetStringA
    # uint32_t SusiBoardGetStringA(uint32_t Id, char *pBuffer, uint32_t *pBufLen)
    susifunc.argtypes = [c_uint32, POINTER(c_char), POINTER(c_uint32)]
    susifunc.restype = c_uint32
    pBuflen = c_uint32()
    # call susifunc to retrieve pBuflen or simply get the string length
    status = susifunc(Id, c_char_p(0), pBuflen)
    # intialize string buffer with the correct length
    pBuffer = create_string_buffer(pBuflen.value)
    # call susifunc again to retrieve the correct string buffer values
    status = susifunc(Id, pBuffer, pBuflen)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    return pBuffer.value.decode("utf-8")


# get Version no. : board info
def susi_boardinfo_val(Id, valType):
    elevate(graphical=False)
    # set SUSI function to call
    susifunc = libsusi.SusiBoardGetValue
    # uint32_t SusiBoardGetValue(uint32_t Id, uint32_t *pValue)
    susifunc.argtypes = [c_uint32, POINTER(c_uint32)]
    susifunc.restype = c_uint32
    pValue = c_uint32()
    # call susifunc
    status = susifunc(Id,  pValue)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    # return version info
    if valType == BOARD_VER:
        # version (major.minor.build) -> convert pValue.value to readable string
        verMajor = str(pValue.value >> 24)
        verMinor = str((pValue.value >> 16) & 255)
        verBuild = str(pValue.value & 65535)
        return verMajor+"."+verMinor+"."+verBuild
    # return HWM temperature in celsius
    if valType == HWM_TEMP:
        celsius = (pValue.value - SUSI_KELVINS_OFFSET) / 10
        return str(celsius) + " celsius"
    # return HWM voltage
    if valType == HWM_VOLT:
        return str(pValue.value / 1000) + " volts"
    # return nothing
    return


# get GPIOx capability (x = 0..7)
def susi_get_gpio_cap(Id):
    # set SUSI function to call
    susifunc = libsusi.SusiGPIOGetCaps
    # uint32_t SusiGPIOGetCaps(uint32_t Id, uint32_t ItemId, uint32_t *pValue)
    susifunc.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
    susifunc.restype = c_uint32
    pValue = c_uint32()
    cap_str = ""
    # call susifunc (check input support)
    status = susifunc(Id, SUSI_ID_GPIO_INPUT_SUPPORT, pValue)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    if pValue.value == 1:
        cap_str = cap_str+"INPUT is supported.  "
    else:
        cap_str = cap_str+"INPUT is NOT supported.  "
    # call susifunc (check output support)
    status = susifunc(Id, SUSI_ID_GPIO_OUTPUT_SUPPORT, pValue)
    if status != SUSI_STATUS_SUCCESS:
        return susi_code_description(status)
    if pValue.value == 1:
        cap_str = cap_str+"OUTPUT is supported."
    else:
        cap_str = cap_str+"OUTPUT is NOT supported."
    return cap_str


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


# set GPIOx direction (1=input; 0=output)
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


# set GPIOx level (1=high; 0=low)
# INPUT: default Level=HIGH; Level=LOW if triggered or grounded
# OUTPUT: default Level=LOW; set Level=HIGH to send trigger, then return to LOW
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


# set level=HIGH, for a number of seconds (Delay) then set back Level=LOW
def susi_trigger(Id, Delay):
    susi_set_gpio_level(Id, SUSI_GPIO_HIGH)
    time.sleep(Delay)
    susi_set_gpio_level(Id, SUSI_GPIO_LOW)
    print("done trigger")


def susi_input_is_activated(gpio):
    gpio_direction = susi_get_gpio_direction(gpio)
    if gpio_direction != "INPUT":
        #print("Error: GPIO-{} direction must be INPUT.".format(gpio))
        return 0#False
    gpio_level = susi_get_gpio_level(gpio)
    if gpio_level != "LOW":
        return 0#False
    else:
        print("GPIO-{} has been sucessfully activated.".format(gpio))
        return 1#True


def trigger_relay_if_button_pressed(bttn, relay):
    while True:
        bttn_status = susi_input_is_activated(bttn)
        if bttn_status:
            susi_set_gpio_level(relay, SUSI_GPIO_HIGH)
            # time.sleep(0.300)
        else:
            susi_set_gpio_level(relay, SUSI_GPIO_LOW)
        time.sleep(0.2)


def susi_connection():
    
    if susi_initialize()==True:
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
        return True
    else:
        print("susi_initialize()=False")
        return False


        




        


        
        

