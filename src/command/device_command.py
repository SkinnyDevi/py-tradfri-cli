from pytradfri import Gateway
from pytradfri.error import RequestTimeout
from pytradfri.device import Device

from src.menu import CLIMenu


class DeviceCommand:
    def __init__(self, identifier: str, gateway_api, gateway: Gateway, log_author):
        self.gateway_api = gateway_api
        self.gateway = gateway
        self.identifier = "command" if identifier is None else identifier
        self.log_author = "commandauthor" if log_author is None else log_author
        self.params = None
        self.devices: list[Device] = None

    def _run(self):
        pass

    def _runner_check(self, devices, params=None):
        try:
            self.params = params
            self.devices = devices
            self._run()
        except RequestTimeout:
            CLIMenu.log("Request timed out, trying again...",
                        'warn', self.log_author)
            try:
                self._run()
            except RequestTimeout:
                CLIMenu.log('Request timed out.', 'error', self.log_author)

    def setup(self):
        return [self.identifier, self._runner_check]
