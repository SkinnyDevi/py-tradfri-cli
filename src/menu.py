from datetime import datetime
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CLIMenu:
    """CLI menu to be interacted with."""
    displayed = False
    log_author = "Message"

    class LogError(Exception):
        pass

    @staticmethod
    def log(msg, type, author, wants_message=False):
        """
        msg - Message to log

        type - 'cmd', 'log', 'warn', 'error'

        author - which class logged this message
        """

        def format_time(timestamp):
            if int(timestamp) < 10:
                return f"0{timestamp}"
            return timestamp

        log_timestamp = datetime.now()
        log_timestamp = f"{format_time(log_timestamp.hour)}:{format_time(log_timestamp.minute)}:{format_time(log_timestamp.second)}"

        if type == 'log' or 'cmd' or 'warn' or 'error':
            if type == 'log':
                colour = bcolors.OKGREEN
            elif type == 'cmd':
                colour = bcolors.OKBLUE
            elif type == 'warn':
                colour = bcolors.WARNING
            else:
                colour = bcolors.FAIL

            log_msg = f"[{colour}{type.upper()}{bcolors.ENDC}] {log_timestamp} [{author}]: {msg}"

            if wants_message:
                return log_msg
            time.sleep(0.1)
            print(log_msg)
        else:
            raise CLIMenu.LogError("Especified logger type was not found.")

    @staticmethod
    def prompt_cmd():
        return input(CLIMenu.log('> ', 'cmd', 'Command', True))
