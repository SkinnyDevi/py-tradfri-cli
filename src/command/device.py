from pytradfri import Gateway
from pytradfri.device import Device
import threading
import time

from .device_command import DeviceCommand
from src.menu import CLIMenu


class CmdDevice(DeviceCommand):
    def __init__(self, gateway_api, gateway: Gateway):
        super().__init__("device", gateway_api, gateway, "device", True)

    # Examples:
    # device set light 1(device_id) level 100(%)
    # device set light 41(device_id) colour 48(%)
    # device set blind 12(device_id) 48(%)
    # device toggle 4(device_id) [has to be a light]
    def _run(self):
        device = self._get_device()

        if self.params[0] == 'set':
            if self.params[1] == 'light':
                self.set_light_state(device)
            else:
                self.set_blind_state(device)
        elif self.params[0] == 'toggle':
            self.toggle_light(device)

    def set_light_state(self, device: Device):
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

    def set_blind_state(self, device: Device):
        if not device.has_blind_control:
            return CLIMenu.log(f"{device.name} is not a blind.", 'error', self.log_author)
        self.observe(device, 5)

        change_level = device.blind_control.set_state(int(self.params[-1]))
        self.gateway_api(change_level)

        time.sleep(5)
        CLIMenu.log("Blind level was changed successfully.",
                    'log', self.log_author)

    def toggle_light(self, device: Device):
        if not device.has_light_control:
            return CLIMenu.log(f"{device.name} is not a light.", 'error', self.log_author)
        self.observe(device, 5)

        CLIMenu.log('Toggling light state...', 'log', self.log_author)

        colour_change = device.light_control.set_state(
            not device.light_control.lights[0].state)
        self.gateway_api(colour_change)

        time.sleep(5)
        CLIMenu.log("Light was toggled correctly.", 'log', self.log_author)

    def _get_device(self):
        return self.devices[int(self.params[2]) - 1]

    def observe(self, device: Device, timeout: int):
        """Observes a device."""

        def callback(updated_device):
            assert isinstance(updated_device, Device)
            assert updated_device.light_control is not None
            light = updated_device.light_control.lights[0]
            updated_level = int(
                (int(light.dimmer if light.dimmer is not None else 0) / 254) * 100)

            CLIMenu.log(
                f"Received message for: {updated_device.name} at {updated_level}%", 'log', self.log_author+"_observer")

        def err_callback(err):
            print(err)

        def worker():
            self.gateway_api(device.observe(
                callback, err_callback, duration=timeout))
        threading.Thread(target=worker, daemon=True).start()

        CLIMenu.log("Sleeping to start observation task.",
                    'log', self.log_author)
        time.sleep(1)

    def _runner_check(self, devices, params):
        if len(params) < 1:
            return CLIMenu.log("device command takes various arguments.", 'error', self.log_author)
        super()._runner_check(devices, params)
