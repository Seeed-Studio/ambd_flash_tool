


import os
import sys
import platform
import shutil
import struct
import re

try:
    import pathlib
except ImportError:
    print("Installing pathlib module")
    res = os.system("pip3 install pathlib")
    if res != 0:
        print("pathlib module installation failed")
        sys.exit(1)
    import pathlib

from pathlib import Path

try:
    import click
except ImportError:
    print("Installing Click module")
    res = os.system("pip3 install Click")
    if res != 0:
        print("Click module installation failed")
        sys.exit(1)
    import click

try:
    import colorama
except ImportError:
    print("Installing colorama module")
    res = os.system("pip3 install colorama")
    if res != 0:
        print("Colorama module installation failed")
        sys.exit(1)
    import colorama

from colorama import init, Fore, Back, Style

try:
    import serial
except ImportError:
    print("Installing pyserial module")
    res = os.system("pip3 install pyserial")
    if res != 0:
        print("pyserial module installation failed")
        sys.exit(1)
    import serial

if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))

# List of supported board USB IDs.  Each board is a tuple of unique USB vendor
# ID, USB product ID.
BOARD_IDS = \
    [{
        "name": "wio terminal",
        "info": ("2886", "802D")
    }]

def getAllPortInfo():
    return comports(include_links=False)
    
def getAvailableBoard():
    for info in getAllPortInfo():
        port, desc, hwid = info 
        ii = hwid.find("VID:PID")
        #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
        if ii != -1:
            for b in  BOARD_IDS:
                (vid, pid) = b["info"]
                if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                    return port

    return None



def windows_full_port_name(portname):
    # Helper function to generate proper Windows COM port paths.  Apparently
    # Windows requires COM ports above 9 to have a special path, where ports below
    # 9 are just referred to by COM1, COM2, etc. (wacky!)  See this post for
    # more info and where this code came from:
    # http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/
    m = re.match("^COM(\d+)$", portname)
    if m and int(m.group(1)) < 10:
        return portname
    else:
        return "\\\\.\\{0}".format(portname)

def normalized_port(portname):
    _portname = portname
    _platform = platform.platform()
    if _platform.find('Windows') >= 0:
        _portname = windows_full_port_name(portname)

    return _portname

def get_flash_tool():
    _tool = str(Path(os.path.split(os.path.realpath(__file__))[0], 'tool'))
    _platform = platform.platform()
    if _platform.find('Windows') >= 0:
        _tool = str(Path(_tool, 'windows', "amebad_image_tool.exe"))
    elif _platform.find('Linux') >= 0:
        _tool = str(Path(_tool, 'linux', 'amebad_image_tool'))
    elif _platform.find('Darwin') >= 0:
        _tool = str(Path(_tool, 'macos', 'amebad_image_tool'))
    elif _platform.find('macOS') >= 0:
        _tool = str(Path(_tool, 'macos', 'amebad_image_tool'))
    else:
        _tool = ""
        print(Fore.RED, "No support yet!")
        sys.exit(1)
    return _tool

def make_empty_img(length):
    _empty = struct.pack('B', 0xFF)
    with open("km0_boot_all.bin", "wb") as _km0_boot_all_bin:
        for i in range(8192):
            i
            _km0_boot_all_bin.write(_empty)
    _km0_boot_all_bin.close()

    with open("km4_boot_all.bin", "wb") as _km4_boot_all_bin:
        for i in range(4096):
            i
            _km4_boot_all_bin.write(_empty)
    _km4_boot_all_bin.close()

    with open("km0_km4_image2.bin", "wb") as _km0_km4_image2_bin:
        for i in range(length - 12):
            i
            for j in range(1024):
                j
                _km0_km4_image2_bin.write(_empty)
    _km0_km4_image2_bin.close()

def copy_img(dir):
    _local_dir = str(Path(os.path.split(os.path.realpath(__file__))[0]))
    _km0_boot_all_bin = str(Path(dir, "km0_boot_all.bin"))
    _km4_boot_all_bin = str(Path(dir, "km4_boot_all.bin"))
    _km0_km4_image2_bin = str(Path(dir, "km0_km4_image2.bin"))
    if not os.path.exists(_km0_boot_all_bin):
        print(Fore.RED + _km0_boot_all_bin + " not exists!")
        sys.exit(1)
    if not os.path.exists(_km4_boot_all_bin):
        print(Fore.RED + _km4_boot_all_bin + " not exists!")
        sys.exit(1)
    if not os.path.exists(_km0_km4_image2_bin):
        print(Fore.RED + _km0_km4_image2_bin + " not exists!")
        sys.exit(1)
    print(Fore.GREEN + "copy img to workspace...")
    shutil.copyfile(_km0_boot_all_bin, str(Path(_local_dir, "km0_boot_all.bin")))
    shutil.copyfile(_km4_boot_all_bin, str(Path(_local_dir, "km4_boot_all.bin")))
    shutil.copyfile(_km0_km4_image2_bin, str(Path(_local_dir, "km0_km4_image2.bin")))

    
    
@click.group()
@click.version_option(version='0.2.0')
def cli():
    """RTL872XD Flash tool

    This tool is used to burn rtl8720d firmware.
    """
    init(autoreset=True)
    pass

@cli.command()
@click.option(
    "--length",
    "-l",
    default=2048,
    type=click.INT,
    help="Length(kB) (default 2048kB).",
    metavar="DELAY",
)
@click.option(
    "--port",
    "-p",
    required=False,
    type=click.STRING,
    help="Name of serial port for connected board.",
    metavar="PORT",
)
def erase(length, port):
    getAvailableBoard()
    _tool = get_flash_tool()
   
    if port == None:
        _port = getAvailableBoard()
        if _port == None:
            print(Fore.RED + "Sorry, the device you should have is not plugged in.")
            sys.exit(1)
            
    _port = normalized_port(_port)
    _cmd = _tool + " " + _port 
    make_empty_img(length)
    print(Fore.GREEN + "Erasing...")
    obj = os.popen(_cmd)
    ret = obj.read()
    if ret.find('successfully') >= 0:
        print(ret)
        print(Fore.GREEN + "Success!")
    else:
        print(Fore.RED + "Error!")

@cli.command()
@click.option(
    "--port",
    "-p",
    required=False,
    type=click.STRING,
    help="Name of serial port for connected board.",
    metavar="PORT",
)
@click.option(
    "--dir",
    "-d",
    required=False,
    type=click.STRING,
    help="Specifies the location of the directory where the firmware is located",
    metavar="DIR",
)
def flash(port, dir):
    if dir == None:
        dir = os.getcwd()
    else:
        copy_img(dir)

    _tool = get_flash_tool()
    
    if port == None:
        _port = getAvailableBoard()
        if _port == None:
            print(Fore.RED + "Sorry, the device you should have is not plugged in.")
            sys.exit(1)
    _cmd = _tool + " " + _port 
    
    _port = normalized_port(_port)
    print(Fore.GREEN + "Flashing...")
    obj = os.popen(_cmd)
    ret = obj.read()
    if ret.find('successfully') >= 0:
        print(ret)
        print(Fore.GREEN + "Success!")
    else:
        print(Fore.RED + "Error!")

if __name__ == "__main__":
    try:
        cli()
    except OSError:
        print("error")
   