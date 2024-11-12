from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)

# add colorful logs
logging.addLevelName(logging.DEBUG, "\033[95mDEBUG\033[0m")
logging.addLevelName(logging.INFO, "\033[92mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[93mWARNING\033[0m")
logging.addLevelName(logging.ERROR, "\033[91mERROR\033[0m")

class LogManager:
    def __init__(self):
        self.logs = deque(maxlen=1000)  # Store last 1000 logs
        self.log_types = {
            'SYSTEM': 'white',
            'TASK': 'cyan',
            'ACTION': 'blue',
            'GOAL': 'green',
            'TREND': 'yellow',
            'ERROR': 'red'
        }

    def add_log(self, log_type: str, message: str):
        """Add a new log entry"""
        log_entry = {
            'timestamp': datetime.now(),
            'type': log_type,
            'message': message
        }
        self.logs.append(log_entry)
        # Also print to console for debugging
        logger.info(f"{log_entry['timestamp'].strftime('%H:%M:%S')} [{log_type}] {message}")

    def get_recent_logs(self, minutes: int = 5):
        """Get logs from the last specified minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [log for log in self.logs if log['timestamp'] > cutoff_time]