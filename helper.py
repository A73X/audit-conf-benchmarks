import time

from colorama import Fore, Style

LOADING_REFRESH_INTERVAL_SECONDS = 0.1

class Helper:
    def __init__(self):
        self.name = "Helper"
        self.__loading_char = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.__loading_index = 0
        self.__last_loading_flush = 0.0

    # Logging functions
    def log_info(self, message, end="\n", flush=False):
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message}", end=end, flush=flush)

    def log_warning(self, message, end="\n", flush=False):
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}", end=end, flush=flush)

    def log_debug(self, message, end="\n", flush=False):
        print(f"{Fore.BLUE}[DEBUG]{Style.RESET_ALL} {message}", end=end, flush=flush)
    
    def log_loading(self, message, force=False):
        # Throttle: an unbuffered flush() per call is a real syscall cost when this
        # runs inside per-line/per-key hot loops (thousands+ calls/sec on large files).
        now = time.monotonic()
        if not force and (now - self.__last_loading_flush) < LOADING_REFRESH_INTERVAL_SECONDS:
            return
        self.__last_loading_flush = now
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message} {self.__loading_char[self.__loading_index]}", end="\r", flush=True)
        # Update loading index
        self.__loading_index = (self.__loading_index + 1) % 10