from getpass import getpass
from decouple import config
from pytradfri.error import RequestTimeout
import sys
import bcrypt

from menu import CLIMenu, bcolors
from tradfri_connection.gateway_connector import TradfriGatewayConnector

from command.device import CmdDevice


use_pwd = getpass("Input the password to start using your lights: ")

if not bcrypt.checkpw(use_pwd.encode('utf8'), config("SCRIPT_PWD").encode('utf8')):
    print(f"[{bcolors.FAIL}ERROR{bcolors.ENDC}]: Incorrect password to use lights.")
    sys.exit(0)

l_author = CLIMenu.log_author
CLIMenu.log("Welcome to Lights Manager.", 'log', l_author)
CLIMenu.log("Starting connection with Gateway...", 'log', l_author)

gateway_connector = TradfriGatewayConnector()
gateway_connector.connect_gateway()

gateway = gateway_connector.gateway
gateway_api = gateway_connector.gateway_api


def setup_commands():
    CLIMenu.log('Setting up commands...', 'log', "Commands")
    cmds = [
        CmdDevice(gateway_api, gateway).setup()
    ]
    CLIMenu.log('Setup completed.', 'log', "Commands")
    return cmds


def gather_devices():
    CLIMenu.log('Gathering device list...', 'log', "devices")

    def device_gatherer():
        devices = gateway_api(
            gateway_api(gateway.get_devices()))

        CLIMenu.log("Successfully collected devices from gateway.",
                    'log', 'devices')

        return devices

    try:
        return device_gatherer()
    except RequestTimeout:
        CLIMenu.log("Request timed out, trying again...",
                    'warn', "devices")
        try:
            return device_gatherer()
        except RequestTimeout:
            CLIMenu.log('Request timed out.', 'error', "devices")
            return None


CLIMenu.displayed = True
command_list = setup_commands()
device_list = gather_devices()
while CLIMenu.displayed:
    command = CLIMenu.prompt_cmd()

    if (command == 'exit'):
        CLIMenu.log('Shutting down.', 'warn', l_author)
        CLIMenu.displayed = False
        continue

    if (command == 'devices'):
        if device_list is None:
            device_list = gather_devices()
        if device_list is None:
            continue

        for i in range(len(device_list)):
            if device_list[i].has_light_control or device_list[i].has_blind_control:
                print(f"[{i+1}] {device_list[i].name}")
        continue

    for cmd in command_list:
        instruction = command.split(" ")
        if (cmd[0] == instruction[0]):
            instruction.pop(0)
            cmd[1](device_list, instruction)
            break
