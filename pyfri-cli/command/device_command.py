from pytradfri import Gateway
from pytradfri.error import RequestTimeout
from pytradfri.device import Device

from ..menu import CLIMenu


class DeviceCommand:
    """General command class used for making commands."""

    def __init__(self, identifier: str, gateway_api, gateway: Gateway, log_author: str, needs_devices=False):
        self.gateway_api = gateway_api
        self.gateway = gateway
        self.identifier = "command" if identifier is None else identifier
        self.log_author = "commandauthor" if log_author is None else log_author
        self.params = None
        self.devices: list[Device] = None
        self.needs_devices = needs_devices

    def run(self):
        """The code to run when the command is called."""
        pass

    def runner_check(self, devices, params=None):
        """Try any requests for the Gateway (if any) and checks for needed
                parameters before running the command.
        """

        try:
            self.params = params
            if self.needs_devices and devices is None:
                return CLIMenu.log('Unable to run command without a list of devices.', 'error', self.log_author)

            self.devices = devices
            self.run()
        except RequestTimeout:
            CLIMenu.log("Request timed out, trying again...",
                        'warn', self.log_author)
            try:
                self.run()
            except RequestTimeout:
                CLIMenu.log('Request timed out.', 'error', self.log_author)

    def setup(self):
        """Used for setting up and registering the command."""
        return [self.identifier, self.runner_check]
