from typing import SupportsIndex
import sys, pathlib, platform, time, logging
import ctypes
import serial.tools.list_ports


# constants
# CRT defaults
CRT_ADDR = 0
CRT_PSWD = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # [255,255,255,255,255,255]
CRT_BAUD = 9600
BAUD_RATES = [9600, 19200, 38400, 57600, 115200]
ISA_DEFAULT_SN = 3  # default r/w sector number used by ISA
NOMOVE = 0
FRONT = 1
REAR = 2

# === SET PER SITE === #
# assign CRT card password for site (for added security)
CRT_SITE_PSWD = CRT_PSWD
# ie: [1, 2, 3, 4, 5, 6] or use CRT_PSWD for the default
# === site settings === #

# serial ports
COM1 = "/dev/ttyS0"
COM2 = "/dev/ttyS1"
COM3 = "/dev/ttyS2"
COM4 = "/dev/ttyS3"
COM5 = "/dev/ttyS4"
COM6 = "/dev/ttyS5"
# using serial to USB adapter
USB0 = "/dev/ttyUSB0"
USB1 = "/dev/ttyUSB1"
USB2 = "/dev/ttyUSB2"


# === Python LOGGING
def set_logger(logfile):
    # logfile = "logs/" + logfile  # prepend path "logs/"
    loglevel = logging.INFO  # adjust as desired
    dtfmt = "%Y-%m-%d %H:%M:%S"  # date/time format
    logfmt = "%(levelname)s: %(asctime)s: %(message)s"  # logging format
    logging.basicConfig(filename=logfile, level=loglevel, format=logfmt, datefmt=dtfmt)
    return logging.getLogger()  # end method and return some values

logger = set_logger("crt310.log")

# === load shared library or dll (linux only)
def load_crt310_dll():
    if sys.platform != "linux":  # check if Linux
        # logger.error("OS not supported. Requires Linux")
        sys.exit()
    # assign dll based on machine type and architecture
    _machine = platform.machine()
    if _machine.startswith("arm") or _machine.startswith("arm"):
        dll_name = "libs/lib310_arm.so"
    else:
        dll_name = "libs/lib310x64.so" if sys.maxsize > 2 ** 32 else "libs/lib310x86.so"
    try:  # load dll
        c_lib = ctypes.CDLL(pathlib.Path().absolute() / dll_name)
        # logger.info(dll_name + " loaded successfully.")
        print(dll_name+" loaded successfully.")
    except Exception as e:
        logger.critical(str(e))
        print(str(e))
        sys.exit("Failed to load DLL.  Please see logfile for details.  Exiting!")
    return c_lib

lib310 =load_crt310_dll()
# convert string into a list of integers
# ie: str2int("isainc") => [105, 115, 97, 105, 110, 99] or [0x69, 0x73, 0x61, 0x69, 0x6e, 0x63]
def str2int(str_var):
    return [ord(c) for c in str_var]


# CRT-310 card type (s1, s2) description
def crt310_card_desc(s1, s2):
    sx_str = s2
    if s1 == 78:  # 'N' or 0x4e = Negative response
        switcher = {
            48: "0: No card inside",
            49: "1: Unknown card type",
            50: "2: Card is not in the right position where it can be operated.",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    if s1 == 48:  # '0' or 0x30 = RFID cards
        switcher = {
            48: "0: Contactless RFID card (S50)",
            49: "1: Contactless S70 card",
            50: "2: Contactless UL card",
            52: "4: ISO14443 TYPEA CPU card",
            53: "5: ISO14443 TYPEB CPU card",
            57: "9: Contactless RFID card but unknown type",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    if s1 == 49:  # '1' or 0x31 = CPU cards
        switcher = {
            48: "0: T=0 contact CPU card",
            49: "1: T=1 contact CPU card",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    if s1 == 50:  # '2' or 0x32 = 24Cxx cards
        switcher = {
            48: "0: 24C01 card",
            49: "1: 24C02 card",
            50: "2: 24C04 card",
            51: "3: 24C08 card",
            52: "4: 24C16 card",
            53: "5: 24C32 card",
            54: "6: 24C64 card",
            55: "7: 24C128 card",
            56: "8: 24C256 card",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    if s1 == 51:  # '3' or 0x33 = SL442x cards
        switcher = {
            48: "0: SL4442 card",
            49: "1: SL4428 card",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    if s1 == 52:  # '4' or 0x34 = ATxxxxx cards
        switcher = {
            48: "0: AT88S102 card",
            49: "1: AT88S1604 card",
            50: "2: AT45D041 card",
            51: "3: AT88SC1608 card",
        }
        return switcher.get(sx_str, "unknown type code:" + str(sx_str))
    return sx_str


# CRT-310 status codes (stx) description
def crt310_stx(stx, stcode):
    st_str = stcode
    if stx == 0:  # card position
        switcher = {
            70: "0x46: Too long-card.",
            71: "0x47: Too short-card.",
            72: "0x48: Card exist in front without holding position.",
            73: "0x49: Card exist in front with holding position.",
            74: "0x4A: Card in the reader position.",
            75: "0x4B: Card in IC card operation position and contact with IC contact.",
            76: "0x4C: Card at the rear side position with holding card.",
            77: "0x4D: Card at the rear side position without holding card.",
            78: "0x4E: No card in the reader.",
        }
        return switcher.get(st_str, "unknown status code:" + str(st_str))
    if stx == 1:  # front settings
        switcher = {
            73: "0x49: Card-in only by magnetic signal.",
            74: "0x4A: Card-in only by switch signal.",
            75: "0x4B: Card-in by magnetic signal.",
            78: "0x4E: Prohibit card in.",
        }
        return switcher.get(st_str, "unknown status code:" + str(st_str))
    if stx == 2:  # rear settings
        switcher = {
            74: "0x4A: Allow card in from rear side.",
            78: "0x4E: Prohibit card in from rear side.",
        }
        return switcher.get(st_str, "unknown status code:" + str(st_str))
    return st_str


# CRT-310 sensor status codes (pssx) description
def crt310_ssx(ssx, sensorcode):
    ssc_str = sensorcode
    if 0 <= ssx <= 4:  # infrared sensor
        switcher = {
            48: "0x30: no card on the sensor position " + str(ssx),
            49: "0x31: with card on the sensor position " + str(ssx),
        }
        return switcher.get(ssc_str, "unknown sensor code:" + str(ssc_str))
    if ssx == 5:  # shutter sensor
        switcher = {
            48: "0x30: shutter is closed.",
            49: "0x31: shutter is opened.",
        }
        return switcher.get(ssc_str, "unknown sensor code:" + str(ssc_str))
    if ssx == 6:  # card entry switch sensor
        switcher = {
            48: "0x30: no card-in signal.",
            49: "0x31: card-in signal.",
        }
        return switcher.get(ssc_str, "unknown sensor code:" + str(ssc_str))
    return ssc_str


# CRT-310 error codes (Error byte E) description
def crt310_error(crt_error):
    switcher = {
        0: "0x00: CM (command) byte error.",
        1: "0x01: PM (parameter) byte error.",
        2: "0x02: Command error. Command cannot be executed.",
        4: "0x04: Data package error.",
        5: "0x05: Input Voltage is not within the range of the voltage.",
        6: "0x06: Non-standard length of card in the reader.",
        7: "0x07: Main power down and backup power is off-power.",
    }
    return switcher.get(crt_error, "unknown error code" + str(crt_error))


# CRT-310 operation status code description
def crt310_osc(osc):
    switcher = {
        48: "0: Card not valid.",
        49: "1: Wrong sector number.",
        50: "2: Wrong serial number or uid.",
        51: "3: Wrong password.",
        52: "4: Data read error.",
        69: "E: No card in reader.",
        78: "N: No card in reader.",
        87: "W: Card is not in the right position.",
    }
    return switcher.get(osc, "unknown operation status code: " + str(osc))


# close/release COM port on com_handle/port_fd
def crt310_close(port_fd):
    # int close_port(int fd)
    status = lib310.ComClose(port_fd)
    if status != 0:
        logger.error("crt310_close(): status=" + str(status))
        # print("Error: Failed to close port with error code: `{}`. ".format(status))
    else:
        logger.info("crt310_close(): fd=" + str(port_fd))
    return status  # end method and return some values


# set/open device on COM port w/ baud; returns com_handle/port_fd
def crt310_open(com_port, baud_rate=9600):  # int ComOpen(char* port)
    port_fd = lib310.ComOpen(com_port.encode("utf-8"), baud_rate)
    if port_fd < 0:
        logger.warning(
            "crt310_open(): port=" + str(com_port) + " baud=" + str(baud_rate)
        )
        # print("Error: Port `{}` failed. Check your connections.".format(com_port))
    else:
        logger.info(
            "crt310_open_wbaud(): com="
            + com_port
            + " @ "
            + str(baud_rate)
            + "; fd="
            + str(port_fd)
        )
    return port_fd  # end method and return some values


# execute crt command via serial port; return status, rxdata
# port_fd=int, cmd_list=list, [dev_addr=int]
def crt310_execute_cmd(port_fd, cmd_list):
    if port_fd < 0:  # check if crt is connected
        logger.error("crt310_execute_cmd(): No crt571 found, fd=" + str(port_fd))
        return port_fd, []
    txdata = bytes(cmd_list)  # convert string to bytes
    rxdata = ctypes.create_string_buffer(520)  # rxdata=text(8)+data(512 max)
    rxreply = ctypes.c_ubyte()
    rxlen = ctypes.c_int()
    cfunc = lib310.RS232_ExeCommand_EX  # assign C function to call
    cfunc.argtypes = [  # cfunc arguments
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_int),
    ]
    cfunc.restype = ctypes.c_int  # cfunc response type
    # call cfunc
    status = cfunc(port_fd, txdata, len(txdata), rxreply, rxdata, rxlen)
    result = rxdata[: rxlen.value]
    logger.debug("crt310_execute_cmd(): rxdata=" + result.decode("utf-8", "ignore"))
    return status, result  # end method and return some values


# Initialize CRT-310
def crt310_initialize(port_fd, rf_movement=0):  # port_fd=int
    if rf_movement == 0:  # no card movement
        status, rxdata = crt310_execute_cmd(port_fd, [0x30, 0x30])
    elif rf_movement == 1:  # eject to front
        status, rxdata = crt310_execute_cmd(port_fd, [0x30, 0x31])
    else:  # eject to rear
        status, rxdata = crt310_execute_cmd(port_fd, [0x30, 0x32])
    if status != 0:  # command failed
        logger.warning("crt310_initialize(): No CRT-310 found")
        return False
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("crt310_initialize(): error=" + error_desc)
        return False
    logger.info("crt310_intialize(): OK. device=" + rxdata.decode("utf-8"))
    return True


# autoscan CRT device(s) then initialize
def crt310_autoscan():
    com_handles = []
    com_ports = []
    # print("\nAutoscanning for CRT device, please wait ...")
    ports = serial.tools.list_ports.comports()  # scan available COM ports
    for port in sorted(ports):  # check each COM ports for CRT device
        for b in BAUD_RATES:  # check per baud
            com_handle = crt310_open(port.device, b)
            # initialize device per com_handle
            if crt310_initialize(com_handle):
                logger.info(
                    "crt310_autoscan(): CRT-310 on port="
                    + port.device
                    + " @ "
                    + str(b)
                    + "; fd="
                    + str(com_handle)
                )
                com_ports.append(port.device)
                com_handles.append(com_handle)
                # break  # device found, move on to the next port
                return com_handles,com_ports
    if not com_handles:  # check if list is empty
        logger.warning("crt310_autoscan(): No CRT-310 device found.")
    return com_handles, com_ports  # end method and return some values


# CRT-310 Seek RFID card
def crt310_seek_rfid(port_fd):
    try:
        status, rxdata = crt310_execute_cmd(port_fd, [0x35, 0x30])
        if status == 0:
            if len(rxdata)<=2:
                print(f'length of rxdata:{len(rxdata)}')
                return False
           
            osc = rxdata[2]  # operation status code
            if osc != 89:  # not ('Y' or 0x59)
                error_desc = crt310_osc(osc)
                logger.warning("crt310_seek_rfid(): " + error_desc)
                return False
        else:
            logger.error("crt310_seek_rfid(): command failed")
            return False
        logger.info("crt310_seek_rfid(): Success!")
        return True  # end method and return some values
    except:
        return False


# CRT-310 identify card type
def crt310_card_type(port_fd):
    status, rxdata = crt310_execute_cmd(port_fd, [0x31, 0x31])
    print("  card type rxdata:", rxdata.hex())
    if status == 0:
        if rxdata[0] == 78:  # Negative response
            card_desc = crt310_card_desc(rxdata[0], rxdata[1])
            logger.error(card_desc)
        else:
            osc = rxdata[2]  # operation status code
            card_desc = crt310_card_desc(osc, rxdata[3])
            logger.info("crt310_card_type(): " + card_desc)
    else:
        card_desc = "crt310_card_type(): command failed"
        logger.error(card_desc)
    return card_desc  # end method and return some values


# RF card key (password) verification
# port_fd=int, [sn=int, ks=str]
def crt310_verify_sector_password(port_fd, sn):
    tx_cmd = [0x35, 0x32]  # rf verify key-A
    tx_cmd.append(sn)
    tx_cmd += CRT_SITE_PSWD  # add pass/key data
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    if status == 0:
        osc = rxdata[3]  # operation status code
        if osc != 89:  # not ('Y' or 0x59)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_verify_sector_password(): " + error_desc)
            return False
    else:
        logger.error("crt310_verify_sector_password(): command failed")
        return False
    logger.info("crt310_verify_sector_password(): OK.")
    return True  # end method and return some values


# Change RF sector password (key-A)
# port_fd, sn=int, new_key=str
def crt310_change_sector_password(port_fd, sn, new_key):
    tx_cmd = [0x35, 0x35]  # rf change sector password
    tx_cmd.append(sn)
    pdata = str2int(new_key)  # convert from string to int/hex list
    tx_cmd += pdata  # append new pass/key
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    if status == 0:
        osc = rxdata[3]  # operation status code
        if osc != 89:  # not ('Y' or 0x59)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_change_sector_password(): " + error_desc)
            return False
    else:
        logger.error("crt310_change_sector_password(): command failed")
        return False
    logger.info("crt310_change_sector_password(): Success!")
    return True  # end method and return some values


# read rf data
def crt310_read_rf_data(port_fd, sn=3, bn=0):  # port_fd=int[,sn,bn=int]
    # sn: sector number; bn: block number;
    tx_cmd = [0x35, 0x33]  # rf read
    tx_cmd.extend([sn, bn])
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    if status == 0:
        osc = rxdata[4]  # operation status code
        if osc != 89:  # NOT ('Y' or 0x59 or success)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_read_rf_data(): " + error_desc)
            return error_desc
    else:
        error_desc = "crt310_read_rf_data(): Command failed"
        logger.error(error_desc)
        return error_desc
    card_data = rxdata[5:].decode("utf-8", "ignore")  # card data as string
    logger.info("crt310_read_rf_data(): OK.")
    return card_data  # end method and return some values


#  write rf data
# port_fd=int, [,sn,bn=int], [strdata=string]
def crt310_write_rf_data(port_fd, sn=3, bn=0, strdata=""):
    # sn: sector number; bn: block number; strdata: data to write
    if strdata == "":
        wdata = [0] * 16    # clear block by writing zeros (decimal/hex)
    else:
        strdata = "{:16}".format(strdata)  # pad spaces if less than 16chars
        wdata = str2int(strdata)  # convert string type to a list of int type
    # combine list to form the required tx_cmd
    tx_cmd = [0x35, 0x34]  # rf write
    tx_cmd.extend([sn, bn])
    tx_cmd += wdata
    # perform rfid write command
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    if status == 0:
        osc = rxdata[4]  # operation status code
        if osc != 89:  # NOT ('Y' or 0x59 or success)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_write_rf_data(): " + error_desc)
            return error_desc
    else:
        error_desc = "crt310_write_rf_data(): Command failed"
        logger.error(error_desc)
        return error_desc
    card_data = rxdata[5:].decode("utf-8", "ignore")  # card data as string
    logger.info("crt310_write_rf_data(): OK.")
    return True  # end method and return some values


# read rf multiblock data
# port_fd=int[,sn,sb,nb=int]
def crt310_read_mblock(port_fd, sn=3, sb=0, nb=1):
    # sn: sector number; sb: start block; nb: no. of blocks
    tx_cmd = [0x35, 0x45]  # rf multiblock read
    tx_cmd.extend([sn, sb, nb])
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    # print("rxdata:", rxdata.hex())
    if status == 0:
        osc = rxdata[5]  # operation status code
        if osc != 89:  # NOT ('Y' or 0x59 or success)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_read_mblock(): " + error_desc)
            return error_desc
    else:
        error_desc = "crt310_read_mblock(): Command failed"
        logger.error(error_desc)
        return error_desc
    card_data = rxdata[6:].decode("utf-8", "ignore")  # card data as string
    logger.info("crt310_read_mblock(): OK.")
    return card_data  # end method and return some values


#  write rf multiblock data
# port_fd=int, [,sn,sb,nb=int], [strdata=string]
def crt310_write_mblock(port_fd, sn=3, sb=0, nb=1, strdata=""):
    # sn: sector number; sb: start block; nb: no. of blocks; strdata: data to write
    if strdata == "":
        wdata = [0] * (16 * nb)    # clear block by writing zeros (decimal/hex)
    else:
        strdata = "{:48}".format(strdata)  # pad spaces if less than 48chars
        wdata = str2int(strdata)  # convert string type to a list of int type
    # combine list to form the required tx_cmd
    tx_cmd = [0x35, 0x46]  # rf multiblock write
    tx_cmd.extend([sn, sb, nb])
    tx_cmd += wdata
    # perform rfid write command
    status, rxdata = crt310_execute_cmd(port_fd, tx_cmd)
    if status == 0:
        osc = rxdata[5]  # operation status code
        if osc != 89:  # NOT ('Y' or 0x59 or success)
            error_desc = crt310_osc(osc)
            logger.warning("crt310_write_mblock(): " + error_desc)
            return error_desc
    else:
        error_desc = "crt310_write_mblock(): Command failed"
        logger.error(error_desc)
        return error_desc
    card_data = rxdata[5:].decode("utf-8", "ignore")  # card data as string
    logger.info("crt310_write_mblock(): OK.")
    return True  # end method and return some values


# crt-310 device status
def crt310_device_status(port_fd):
    _, rxdata = crt310_execute_cmd(port_fd, [0x31, 0x30])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("crt310_device_status: error=" + error_desc)
        return error_desc
        # print("Status-device:", error_desc)
    device_status = rxdata[2:].hex()
    logger.info("crt310_device_status: " + device_status)
    return device_status


# crt-310 sensor status
def crt310_sensor_status(port_fd):
    _, rxdata = crt310_execute_cmd(com_handle, [0x31, 0x2F])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("crt310_sensor_status: error=" + error_desc)
        return error_desc
    sensor_status = rxdata[2:].hex()
    logger.info("crt310_sensor_status:" + sensor_status)
    return sensor_status


# crt-310 get cardcode or UID
def crt310_get_cardcode(port_fd):
    try:
        # get rf cardcode (s/n or uid)
        _, rxdata = crt310_execute_cmd(port_fd, [0x35, 0x31])
        if len(rxdata)<=2:
            print(f'length of rxdata:{len(rxdata)}')
            return "~"
        osc = rxdata[2]  # operation status code
        cardcode = rxdata[3:].hex()
        if osc != 89:  # 'Y' or 0x59
            error_desc = crt310_osc(osc)
            logger.error("crt310_get_cardcode(): " + error_desc)
            return "~"#error_desc
        logger.info("crt310_get_cardcode(): " + cardcode)
        return cardcode
    except:
        return "~"


# Eject card (front or back)
def crt310_eject_card(port_fd, eject_to=REAR):
    # [0x32, 0x33]  REAR no hold
    # [0x32, 0x30]  FRONT no hold    
    if eject_to == REAR:  # eject card to rear if present (card move operation)
        _, rxdata = crt310_execute_cmd(port_fd, [0x32, 0x33])
    if eject_to == FRONT:  # eject card to front if present (card move operation)
        _, rxdata = crt310_execute_cmd(port_fd, [0x32, 0x30])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[2])
        logger.error("crt310_eject_card(): " + error_desc)
        return False
    logger.info("crt310_eject_card(): OK.")
    return True

def crt310_release_card(port_fd, release_to=FRONT):    
    # [0x32, 0x32]  REAR with hold
    # [0x32, 0x31]  FRONT with hold
    try:
        if release_to == REAR:  # release card to rear if present (card move operation)
            _, rxdata = crt310_execute_cmd(port_fd, [0x32, 0x32])
        if release_to == FRONT:  # release card to front if present (card move operation)
            _, rxdata = crt310_execute_cmd(port_fd, [0x32, 0x31])
        if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
            error_desc = crt310_error(rxdata[2])
            logger.error("crt310_release_card(): " + error_desc)
            return False
        logger.info("crt310_release_card(): OK.")
        return True
    except:
        return False
        



# SAMPLE USAGE
if __name__ == "__main__":
    print("\n=== CRT-310 card capturer DEMO ===")
    logger = set_logger("crt310.log")  # set log filename
    lib310 = load_crt310_dll()  # load DLL

    com_handle = crt310_open(COM2)  # open com port
    # com_handle = crt310_open(USB0)    # open com port

    # initialize CRT
    if crt310_initialize(com_handle, 0):
        print("Initialize : OK")
    else:
        print("CRT-310 initialization failed!  \nBye, bye!")
        sys.exit()

    # get crt-310 s/n
    _, rxdata = crt310_execute_cmd(com_handle, [0x30, 0x3A])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("TX310_GET_SNO: error=" + error_desc)
        print("CRT-310 S/N:", error_desc)
    else:
        print("CRT-310 S/N:", rxdata[3:].decode("utf-8"))

    # display crt-310 device status
    print("Device status:", crt310_device_status(com_handle))

    # display crt-310 sensor status
    print("Sensor status:", crt310_sensor_status(com_handle))

    ans = input("\nWould you like to perform card operations? (y/n):")
    if ans.lower() == "y":
        while True:  # loop until users exits from rf operations
            while True:  # loop until rfid card is ready
                # Seek if RFID is present
                if not crt310_seek_rfid(com_handle):
                    print("No valid RFID card present.")
                    input("### Please insert card, then press <Enter> to continue...")
                    continue
                else:
                    break

            # display rf cardcode (s/n or uid)
            print("\nCardcode:", crt310_get_cardcode(com_handle))

            # ask for operations parameters
            print("\nPlease provide the following...")
            sn = int(input("  Sector number (1-15) : "))
            bn = int(input("  Block number (0-2)   : "))

            # verify Key-A password
            if not crt310_verify_sector_password(com_handle, sn):
                print("Sector password verification: Failed!")
                break

            # write oprations
            ans = input("\nWrite data to RFID ? (y/n):")
            if ans.lower() == "y":
                wdata = input("  Please enter data to write (16chars max):")
                # write data to rfid
                mycard_data = crt310_write_rf_data(com_handle, sn, bn, wdata)
                if mycard_data:
                    print("  RFID data write operation, success!")
                else:
                    print(f"  RFID data write error: {mycard_data}")

            # read oprations
            ans = input("\nRead RFID data ? (y/n):")
            if ans.lower() == "y":
                # read rfid data
                mycard_data = crt310_read_rf_data(com_handle, sn, bn)
                print(f"  RFID read operations data: {mycard_data}")

            # asks to do card operations again
            ans = input("\nDo you want to do RFID operations again? (y/n):")
            if ans.lower() != "y":
                break

    # Multi-block operations (read and write)
    ans = input("\nPerform Multi-block card operations? (y/n):")
    if ans.lower() == "y":
        while True:  # loop until users exits from multiblock operations
            while True:  # loop until rfid card is ready
                # Seek if RFID is present
                if not crt310_seek_rfid(com_handle):
                    print("No valid RFID card present.")
                    input("### Please insert card, then press <Enter> to continue...")
                    continue
                else:
                    break

            # display rf cardcode (s/n or uid)
            print("\nCardcode:", crt310_get_cardcode(com_handle))

            # ask for operations parameters
            print("\nPlease provide the following...")
            sn = int(input("  Sector number (1-15)     : "))
            sb = int(input("  Start of block (0-2)     : "))
            nb = int(input("  Number of blocks (max 3) : "))

            # verify Key-A password
            if not crt310_verify_sector_password(com_handle, sn):
                print("Sector password verification: Failed!")
                break

            # multi-block write oprations
            ans = input("\nWrite multi-block data to RFID ? (y/n):")
            if ans.lower() == "y":
                wdata = input("  Please enter data to write (48chars max):")
                # write multi-block data to rfid
                card_data = crt310_write_mblock(com_handle, sn, sb, nb, wdata)
                if card_data:
                    print(f"  Multi-block data write operation, success!")
                else:
                    print(f"  Multi-block data write error: {card_data}")

            # multi-block read oprations
            ans = input("\nRead multi-block data from RFID ? (y/n):")
            if ans.lower() == "y":
                # read rfid data
                card_data = crt310_read_mblock(com_handle, sn, sb, nb)
                print(f"  RFID multi-block data: {card_data}")

            # asks to do multiblock operations again
            ans = input("\nDo you want to do Multiblock operations again? (y/n):")
            if ans.lower() != "y":
                break

    # crt310_eject_card(com_handle)  # eject card if present
    # release com_port / exit
    if crt310_close(com_handle) == 0:
        print("\nPort closed properly. \nBye-bye!")
