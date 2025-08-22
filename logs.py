import logging
import traceback
import sys
import io
from config.settings import MODE


class Logger:
    def __init__(self, log_file='app.log'):
        """Initializes the logger with console and file handlers."""
        self.logs = logging.getLogger(self.__class__.__name__)
        self.logs.setLevel(logging.INFO)  # Set logger to INFO level

        # Prevent duplicate handlers
        if not self.logs.hasHandlers():
            # Console handler (only if MODE == True)
            if MODE:
                # Безопасный вывод UTF-8
                if hasattr(sys.stdout, "reconfigure"):  # Python 3.7+
                    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
                else:
                    sys.stdout = io.TextIOWrapper(
                        sys.stdout.buffer, encoding="utf-8", errors="replace"
                    )

                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(console_formatter)
                self.logs.addHandler(console_handler)

            # File handler (всегда в UTF-8)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
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
