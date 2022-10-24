from pytradfri import Gateway
from pytradfri.device import Device

from .device_command import DeviceCommand

from ..menu import CLIMenu


class CmdInfo(DeviceCommand):
    """Get information of a device."""

    def __init__(self, gateway_api, gateway: Gateway):
        super().__init__("info", gateway_api, gateway, "device-info", True)

    def __get_device(self, cmd_index):
        """Gets the wanted device from the list."""
        return self.devices[int(self.params[cmd_index]) - 1]

    def light_info(self, device: Device):
        info = device.device_info
        technical = device.light_control.lights[0]

        msg = f"""

        -- {device.name}'s Information --

        Level: {int(technical.dimmer / 254) * 100}%
        State: {'On' if technical.state else 'Off'}
        Firmware version: {info.firmware_version}
        Model number: {info.model_number}

        """

        CLIMenu.log(msg, 'log', self.log_author)

    def blind_info(self, device: Device):
        info = device.device_info
        technical = device.blind_control.blinds[0]

        msg = f"""

        -- {device.name}'s Information --

        Rolled down: {technical.current_cover_position}%
        Battery: {info.battery_level}%
        Firmware version: {info.firmware_version}
        Model number: {info.model_number}

        """

        CLIMenu.log(msg, 'log', self.log_author)

    def socket_info(self, device: Device):
        info = device.device_info
        technical = device.socket_control.sockets[0]

        msg = f"""

        -- {device.name}'s Information --

        State: {'On' if technical.state else 'Off'}
        Firmware version: {info.firmware_version}
        Model number: {info.model_number}

        """

        CLIMenu.log(msg, 'log', self.log_author)

    def run(self):
        device: Device = self.__get_device(0)

        if device.has_light_control:
            return self.light_info(device)

        if device.has_blind_control:
            return self.blind_info(device)

        if device.has_socket_control:
            return self.socket_info(device)

    def runner_check(self, devices, params):
        if len(params) < 1:
            return CLIMenu.log("device command takes various arguments.", 'error', self.log_author)
        super().runner_check(devices, params)
