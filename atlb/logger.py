# AT PROJECT nEXT Reemerged; nXRE-v3.7
import os
import sys
import logging

import colorama
from dotenv import load_dotenv

load_dotenv()

LOGLEVEL = os.environ.get('LOGLEVEL')

colorama.init(autoreset=True)
class ColoredFormatter(logging.Formatter):
    COLOR_MAP = {
        'DEBUG': colorama.Fore.BLUE,
        'INFO': colorama.Fore.GREEN,
        'WARN': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRIT': colorama.Fore.MAGENTA,
    }

    def format(self, record):
        if record.levelname == 'WARNING':
            record.levelname = 'WARN'

        if record.levelname == 'CRITICAL':
            record.levelname = 'CRIT'

        log_message = super().format(record)
        log_level_color = self.COLOR_MAP.get(record.levelname, colorama.Fore.WHITE)
        log_message = f"[{record.created:.1f}s] {log_level_color}[{record.levelname}]"\
                      f"{colorama.Style.RESET_ALL}\t- {log_message}"
        return log_message

output_handler = logging.StreamHandler(sys.stdout)
output_handler.setFormatter(ColoredFormatter())

logger = logging.getLogger('discord')
logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
logger.addHandler(output_handler)

mafic_logger = logging.getLogger('mafic')
logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
logger.addHandler(output_handler)