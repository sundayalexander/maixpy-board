"""
This module contains mock for required pyboard modules.
"""
from unittest.mock import MagicMock

GPIO = MagicMock()
UART = MagicMock()
fm = MagicMock()
board_info = MagicMock()