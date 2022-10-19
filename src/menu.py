from datetime import datetime
import time


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
            log_msg = f"[{type.upper()}] {log_timestamp} [{author}]: {msg}"

            if wants_message:
                return log_msg
            time.sleep(0.1)
            print(log_msg)
        else:
            raise CLIMenu.LogError("Especified logger type was not found.")

    @staticmethod
    def prompt_cmd():
        return input(CLIMenu.log('> ', 'cmd', 'Command', True))
