"""mrack library."""

import logging

logger = logging.getLogger(__name__)
# Default level used by file_handler
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
console_formatter = logging.Formatter("%(message)s")

file_handler = logging.FileHandler("mrack.log")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Default level for console can be overridden by passing --debug to the executable
console_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
