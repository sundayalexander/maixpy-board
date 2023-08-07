import sys
from unittest.mock import MagicMock
import tests.mocked_pyboard_modules

# Load required pyboard modules
sys.modules["network"] = MagicMock()
sys.modules["Maix"] = tests.mocked_pyboard_modules
sys.modules["machine"] = tests.mocked_pyboard_modules
sys.modules["fpioa_manager"] = tests.mocked_pyboard_modules
sys.modules["board"] = tests.mocked_pyboard_modules
sys.modules["time"] = MagicMock()