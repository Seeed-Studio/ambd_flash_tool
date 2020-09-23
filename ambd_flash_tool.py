import os
import sys
import click
import platform
import shutil
import struct
import re
from colorama import init, Fore, Back, Style
from pathlib import Path


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
    elif _platform.find('Drawin') >= 0:
         _tool = str(Path(_tool, 'macos', 'amebad_image_tool'))
    else:
        _tool = ""
        print(Fore.RED, "No support yet!")
        exit(0)
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
        sys.exit(0)
    if not os.path.exists(_km4_boot_all_bin):
        print(Fore.RED + _km4_boot_all_bin + " not exists!")
        sys.exit(0)
    if not os.path.exists(_km0_km4_image2_bin):
        print(Fore.RED + _km0_km4_image2_bin + " not exists!")
        sys.exit(0)
    print(Fore.GREEN + "copy img to workspace...")
    shutil.copyfile(_km0_boot_all_bin, str(Path(_local_dir, "km0_boot_all.bin")))
    shutil.copyfile(_km4_boot_all_bin, str(Path(_local_dir, "km4_boot_all.bin")))
    shutil.copyfile(_km0_km4_image2_bin, str(Path(_local_dir, "km0_km4_image2.bin")))

    
    
@click.group()
@click.version_option(version='0.1.1')
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
    required=True,
    type=click.STRING,
    help="Name of serial port for connected board.",
    metavar="PORT",
)
def erase(length, port):
    _tool = get_flash_tool()
    _port = normalized_port(port)
    _cmd = _tool + " " + _port 
    make_empty_img(length)
    print(Fore.GREEN + "Erasing...")
    obj = os.popen(_cmd)
    ret = obj.read()
    if ret.find('error') >= 0:
        print(ret)
        print(Fore.RED + "Error!")
    else:
        print(Fore.GREEN + "Success!")

@cli.command()
@click.option(
    "--port",
    "-p",
    required=True,
    type=click.STRING,
    help="Name of serial port for connected board.",
    metavar="PORT",
)
@click.option(
    "--dir",
    "-d",
    required=True,
    type=click.STRING,
    help="Specifies the location of the directory where the firmware is located",
    metavar="DIR",
)
def flash(port, dir):
    copy_img(dir)
    _tool = get_flash_tool()
    _port = normalized_port(port)
    _cmd = _tool + " " + _port 
    print(Fore.GREEN + "Flashing...")
    obj = os.popen(_cmd)
    ret = obj.read()
    if ret.find('error') >= 0:
        print(ret)
        print(Fore.RED + "Error!")
    else:
        print(Fore.GREEN + "Success!")



if __name__ == "__main__":
    cli()
   