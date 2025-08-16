import logging
import traceback
from config.settings import MODE

class Logger:
    def __init__(self, log_file='app.log'):
        """Initializes the logger with console and file handlers."""
        self.logs = logging.getLogger(self.__class__.__name__)
        self.logs.setLevel(logging.INFO)  # Set logger to INFO level

        # Prevent duplicate handlers
        if not self.logs.hasHandlers():
            # Create a console handler for outputting logs to the console (INFO and higher)
            if MODE:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)  # Console will log INFO and above levels
                console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(console_formatter)
                self.logs.addHandler(console_handler)

            # Create a file handler for writing logs to a file (INFO and above)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)  # File will log INFO and above levels
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logs.addHandler(file_handler)

    def error(self, error_message):
        """Logs an error message and prints a notification if not in production mode."""
        self.logs.error(f"Exception occurred: {error_message}")
        self.logs.error("Traceback: %s", traceback.format_exc())

        if not MODE:
            print("An error occurred. Check the logs for details.")

    def info(self, info_message):
        """Logs an informational message and prints it if not in production mode."""
        self.logs.info(info_message)

        if not MODE:
            print(info_message)
