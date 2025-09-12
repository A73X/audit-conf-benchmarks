from colorama import Fore, Style, init

class Helper:
    def __init__(self):
        self.name = "Helper"
        self.__loading_char = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.__loading_index = 0

    # Logging functions
    def log_info(self, message, end="\n", flush=False):
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message}", end=end, flush=flush)

    def log_warning(self, message, end="\n", flush=False):
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}", end=end, flush=flush)

    def log_debug(self, message, end="\n", flush=False):
        print(f"{Fore.BLUE}[DEBUG]{Style.RESET_ALL} {message}", end=end, flush=flush)
    
    def log_loading(self, message):
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message} {self.__loading_char[self.__loading_index]}", end="\r", flush=True)
        # Update loading index
        self.__loading_index = (self.__loading_index + 1) % 10