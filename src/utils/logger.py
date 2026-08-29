"""
SteamDown Ultra AI - Logging & Event System
Thread-safe event logging with timestamped history and Qt signal integration.
"""

import sys
import logging
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class EventLogger(QObject):
    """Singleton event logger broadcasting events to GUI and console."""
    
    log_added = Signal(str, str, str)  # timestamp, level, message
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EventLogger, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self._initialized = True
        self.history = []
        self.max_history = 500
        
        # Setup standard Python logger
        self.logger = logging.getLogger("SteamDown")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def log(self, message: str, level: str = "INFO"):
        """Add a log entry and emit signal."""
        now = datetime.now().strftime("%H:%M:%S")
        entry = (now, level, message)
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)
            
        self.log_added.emit(now, level, message)

    def info(self, msg: str):
        self.log(msg, "INFO")
        
    def warning(self, msg: str):
        self.log(msg, "WARNING")
        
    def error(self, msg: str):
        self.log(msg, "ERROR")
        
    def success(self, msg: str):
        self.log(msg, "SUCCESS")


# Global accessor
logger = EventLogger()
