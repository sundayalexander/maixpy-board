import _thread
from utils.boot import system_on_indicator
from logger.basic_log import log

log.info("Initializing device")

#Start new thread to show light indication.
_thread.start_new_thread(system_on_indicator, ())
log.info("Device initialized.")
