from pytradfri import Gateway
from pytradfri.device import Device
import threading
import time

from .device_command import DeviceCommand
from ..menu import CLIMenu


class CmdDevice(DeviceCommand):
    """Called with 'device'

    parameters: set, toggle

    set parameters: blind or light (deviceID) to level X(%)
    toggle parameters: deviceID

    Examples:

    device set light 1(device_id) level 100(%)

    device set light 41(device_id) colour #565656

    device set blind 12(device_id) 48(%)

    device toggle 4(device_id) [has to be a light or socket]
    """

    def __init__(self, gateway_api, gateway: Gateway):
        super().__init__("device", gateway_api, gateway, "device", True)

    def run(self):
        if self.params[0] == 'set':
            device = self.__get_device(2)
            if self.params[1] == 'light':
                self.set_light_level(device)
            else:
                self.set_blind_level(device)
        elif self.params[0] == 'toggle':
            device = self.__get_device(1)
            self.toggle_device(device)

    def set_light_level(self, device: Device):
        """Sets the the light to a specified level."""

        if not device.has_light_control:
            return CLIMenu.log(f"{device.name} is not a light.", 'error', self.log_author)
        self.observe(device, 5)

        CLIMenu.log('Changing light level...', 'log', self.log_author)

        if self.params[3] == 'level':
            new_level = int(254 * (int(self.params[-1])/100))
            change_level = device.light_control.set_dimmer(
                new_level, transition_time=7)
            self.gateway_api(change_level)
            time.sleep(5)
            CLIMenu.log("Light level changed successfully.",
                        'log', self.log_author)

    def set_blind_level(self, device: Device):
        """Sets the blind to a specified level."""

        if not device.has_blind_control:
            return CLIMenu.log(f"{device.name} is not a blind.", 'error', self.log_author)
        self.observe(device, 10)

        change_level = device.blind_control.set_state(int(self.params[-1]))
        self.gateway_api(change_level)

        time.sleep(11)
        CLIMenu.log("Blind level was changed successfully.",
                    'log', self.log_author)

    def toggle_device(self, device: Device):
        """Toggles the state of a light or socket."""

        if not device.has_light_control and not device.has_socket_control:
            return CLIMenu.log(f"{device.name} is not a light nor socket.", 'error', self.log_author)
        self.observe(device, 5)

        if device.has_light_control:
            CLIMenu.log('Toggling light state...', 'log', self.log_author)

            state_change = device.light_control.set_state(
                not device.light_control.lights[0].state)
            self.gateway_api(state_change)

            time.sleep(5)
            CLIMenu.log("Light was toggled correctly.",
                        'log', self.log_author)
        elif device.has_socket_control:
            CLIMenu.log('Toggling socket state...', 'log', self.log_author)

            state_change = device.socket_control.set_state(
                not device.socket_control.sockets[0].state)
            self.gateway_api(state_change)

            time.sleep(5)
            CLIMenu.log("Socket was toggled correctly.",
                        'log', self.log_author)

    def __get_device(self, cmd_index):
        """Gets the wanted device from the list."""
        return self.devices[int(self.params[cmd_index]) - 1]

    def observe(self, device: Device, timeout: int):
        """Observes a device's changes."""

        def callback(updated_device):
            assert isinstance(updated_device, Device)
            if updated_device.has_light_control:
                light = updated_device.light_control.lights[0]
                updated_level = int(
                    (int(light.dimmer if light.dimmer is not None else 0) / 254) * 100)

            elif updated_device.has_blind_control:
                blind = updated_device.blind_control.blinds[0]
                updated_level = int(
                    (int(blind.current_cover_position if blind.current_cover_position is not None else 0) / 100) * 100)

            elif updated_device.has_socket_control:
                socket = updated_device.socket_control.sockets[0]
                updated_level = 0 if socket.state is False else 100

            CLIMenu.log(
                f"Received update for: {updated_device.name} at {updated_level}%", 'log', self.log_author+"_observer")

        def err_callback(err):
            print(err)

        def worker():
            self.gateway_api(device.observe(
                callback, err_callback, duration=timeout))
        threading.Thread(target=worker, daemon=True).start()

        CLIMenu.log("Sleeping to start observation task.",
                    'log', self.log_author)
        time.sleep(1)

    def runner_check(self, devices, params):
        if len(params) < 1:
            return CLIMenu.log("device command takes various arguments.", 'error', self.log_author)
        super().runner_check(devices, params)
