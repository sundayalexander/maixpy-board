"""
Boot load util module.
"""
from fpioa_manager import fm
from Maix import GPIO
import time
from utils import load_json_file
from board import board_info

# Load board configurations.
board_info.load(load_json_file("config/pins.json"))


def system_on_indicator() -> None:
    """
    Keep led blinking to indicate system is on and active with no errors.
    Returns:
        None
    """
    # register green led on fm.
    fm.register(board_info.LED_GREEN, fm.fpioa.GPIO0)
    led = GPIO(GPIO.GPIO0, GPIO.OUT)

    # Keep led blinking infinitely.
    led_on = 0
    while True:
        led.value(led_on)
        led_on = 0 if led_on else 1
        # sleep few seconds.
        time.sleep(.5)
