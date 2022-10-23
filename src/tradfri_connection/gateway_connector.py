import uuid
from pytradfri import Gateway, PytradfriError
from pytradfri.device import Device
from pytradfri.util import load_json, save_json
from pytradfri.api.libcoap_api import APIFactory
from decouple import config

from src.menu import CLIMenu


class TradfriGatewayConnector:
    log_author = "GatewayConnector"

    def __init__(self):
        self.__CONFIG_FILE = "tradfri_standalone_psk.conf"
        self.gateway_api = None
        self.gateway: Gateway = None

    def connect_gateway(self):
        """Generates a file needed for a communication with the Gateway."""

        host_ip = config("GATEWAY_IP")
        key_code = config("GATEWAY_SC").strip()

        if not bool(load_json(self.__CONFIG_FILE)):
            CLIMenu.log("No standalone PSK found, gathering info to generate a new one...",
                        'warn', TradfriGatewayConnector.log_author)

            if len(key_code) != 16:
                raise PytradfriError("Invalid 'Security Code' provided.")

        conf = load_json(self.__CONFIG_FILE)
        try:
            CLIMenu.log('Gathering standalone PSK for connection...',
                        'log', TradfriGatewayConnector.log_author)

            identity = conf[host_ip].get("identity")
            psk = conf[host_ip].get("key")
            api_factory = APIFactory(host_ip, identity, psk)
        except KeyError:
            CLIMenu.log('Attempting to create a new standalone PSK for connection...',
                        'warn', TradfriGatewayConnector.log_author)

            identity = uuid.uuid4().hex
            api_factory = APIFactory(host_ip, identity)

            try:
                psk = api_factory.generate_psk(key_code)
                conf[host_ip] = {'identity': identity, 'key': psk}
                save_json(self.__CONFIG_FILE, conf)
            except AttributeError as err:
                raise PytradfriError(
                    "No security key was provided to attempt connection with Gateway.") from err

        self.gateway_api = api_factory.request
        self.gateway = Gateway()

        CLIMenu.log("Successfully gathered authentication for Gateway connection.",
                    'log', TradfriGatewayConnector.log_author)
