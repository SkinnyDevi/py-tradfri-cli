from getpass import getpass
from decouple import config
from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.error import RequestTimeout
import sys
import bcrypt

from .menu import CLIMenu, bcolors

from .tradfri_connection.gateway_connector import TradfriGatewayConnector

from .command.device import CmdDevice


def setup_commands(gateway_api, gateway: Gateway):
    """Register the available commands for use.º"""

    CLIMenu.log('Setting up commands...', 'log', "Commands")
    cmds = [
        CmdDevice(gateway_api, gateway).setup()
    ]
    CLIMenu.log('Setup completed.', 'log', "Commands")
    return cmds


def gather_devices(gateway_api, gateway: Gateway):
    """Gathers the devices from the Tradfri Gateway connection for further use."""

    CLIMenu.log('Gathering device list...', 'log', "devices")

    def device_gatherer():
        devices: list[Device] = gateway_api(
            gateway_api(gateway.get_devices()))

        final_devices = []
        for i in range(len(devices)):
            if not devices[i].has_air_purifier_control or not devices[i].has_signal_repeater_control:
                name = devices[i].name.lower()
                if name.find("remote") > 0 or name.find("control") > 0:
                    continue

                final_devices.append(devices[i])

        CLIMenu.log("Successfully collected devices from gateway.",
                    'log', 'devices')

        return final_devices

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


def main():
    use_pwd = getpass(CLIMenu.log(
        "Input the password to start using your lights: ", 'warn', 'Message', True))

    if not bcrypt.checkpw(use_pwd.encode('utf8'), config("SCRIPT_PWD").encode('utf8')):
        print(
            f"[{bcolors.FAIL}ERROR{bcolors.ENDC}]: Incorrect password to use lights.")
        sys.exit(0)

    l_author = CLIMenu.log_author
    CLIMenu.log("Welcome to Lights Manager.", 'log', l_author)
    CLIMenu.log("Starting connection with Gateway...", 'log', l_author)

    gateway_connector = TradfriGatewayConnector()
    gateway_connector.connect_gateway()

    gateway = gateway_connector.gateway
    gateway_api = gateway_connector.gateway_api

    CLIMenu.displayed = True
    devices_gather_retry = False
    command_list = setup_commands(gateway_api, gateway)
    device_list = gather_devices(gateway_api, gateway)

    while CLIMenu.displayed:
        command = CLIMenu.prompt_cmd()

        if (command == 'exit'):
            CLIMenu.log('Shutting down.', 'warn', l_author)
            CLIMenu.displayed = False
            continue

        if (command == 'devices'):
            if device_list is not None:
                for i in range(len(device_list)):
                    print(f"[{i+1}] {device_list[i].name}")
                continue

            if devices_gather_retry:
                CLIMenu.log("Coudln't gather devices at this time. Restart to try again.",
                            'error', "devices")
                continue

            if device_list is None:
                devices_gather_retry = True
                device_list = gather_devices(gateway_api, gateway)

            continue

        for cmd in command_list:
            instruction = command.split(" ")
            if (cmd[0] == instruction[0]):
                instruction.pop(0)
                cmd[1](device_list, instruction)
                break

    return 0
