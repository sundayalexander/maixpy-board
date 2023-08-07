"""
This is network utility module that contains Wifi and other network related class.
"""

import time, network
from typing import List, Dict, Any, Tuple

from Maix import GPIO
from machine import UART
from fpioa_manager import fm
from board import board_info

from logger.basic_log import log
from utils import load_json_file, re

# Load board configurations.
board_info.load(load_json_file("config/pins.json"))


class WiFi(object):
    """
    Wireless fidelity connection class.
    Example:
      to connect to wifi network
      wifi = Wifi()
      wifi.reset()
      wifi.at_cmd()
      wifi.scan_networks() #Optional to scan for available networks.
      wifi.connect(ssid, password)
    """

    __is_m1w__: bool = True
    uart = None
    eb = None
    nic = None

    def __init__(self):
        """
        Initialize network interface card connection if connection do not already exists.
        Returns:
            None
        """
        if not self.is_connected():
            self.init()
        super().__init__()

    def init(self):
        """
        Initialize network interface card connection and register network module pins.
        Returns:
           None
       """
        if self.__is_m1w__:
            fm.register(0, fm.fpioa.GPIOHS1, force=True)
            M1wPower = GPIO(GPIO.GPIOHS1, GPIO.OUT)
            M1wPower.value(0)

        # board_info.WIFI_EN == IO 8
        fm.register(board_info.WIFI_EN, fm.fpioa.GPIOHS0)
        self.en = GPIO(GPIO.GPIOHS0, GPIO.OUT)

        # board_info.WIFI_RX == IO 7
        fm.register(board_info.WIFI_RX, fm.fpioa.UART2_TX)
        # board_info.WIFI_TX == IO 6
        fm.register(board_info.WIFI_TX, fm.fpioa.UART2_RX)
        self.uart = UART(UART.UART2, 115200, timeout=1000, read_buf_len=8192)

    def enable(self, value: bool):
        """
        Enable network card interface communication.
        Args:
            value (bool): wifi network module GPIO connection enable value.
        Returns:
            None
        """
        self.en.value(value)

    def __check_network_state(self, command: str = "AT\r\n", response: str = "OK\r\n", wait_time: int = 20) -> bool:
        """
        Check network communication current condition state.
        Args:
            command (str): UART network command.
            response (str): UART network response.
            wait_time (int): UART write wait time before reading data from UART channel.

        Returns:
            bool
        """
        # write command to UART IO channel.
        self.uart.write(command)
        # Wait few milliseconds before reading.
        time.sleep_ms(wait_time)
        # read response message on UART channel
        tmp = self.uart.read()

        if tmp and tmp.endswith(response):
            return True
        return False

    def write_command(self, command: str, wait_time: int = 20) -> bytes:
        """
        Write command machine UART channel and wait to read response.
        Args:
            command (str): AT command.
            wait_time (int): waiting time before reading response.

        Returns:
            bytes
        """
        self.uart.write(command)
        time.sleep_ms(wait_time)
        tmp = self.uart.read()
        return tmp

    def scan_networks(self) -> List[Dict[str, Any]]:
        """
        Scan for available wifi networks.

        Returns:
            List[Dict[str, Any]]
        """
        _response = self.write_command("AT+CWLAP\r\n")

        # Find network meta data in read bytes.
        _available_networks = re.findall(r"\([0-9A-Za-z,\"\-:\s]+\)", _response.decode("utf-8"))
        _networks = []

        # Construct network dictionary list.
        for _network in _available_networks:
            _network = _network.replace("(", "").replace(")", "").replace('"', "")
            _network_details = [detail.strip() for detail in _network.split(",")]
            _networks.append({
                "ssid": _network_details[1],
                "mac": _network_details[3],
                "meta": _network_details
            })

        return _networks

    def reset(self, force: bool = False, reply_count: int = 5) -> bool:
        """
        Reset network connection and re-init network card.
        Args:
            force (bool): False network restart.
            reply_count (int): network reply loop count before backoff.

        Returns:
            bool
        """
        if not force and self.is_connected():
            return True
        self.init()
        # Loop through network reply count and keep trying reset until backoff.
        for i in range(reply_count):
            log.debug('reset...')
            self.enable(False)
            time.sleep_ms(50)
            self.enable(True)
            # Sleep 500 milliseconds before checking network state.
            time.sleep_ms(500)
            if self.__check_network_state(wait_time=500):
                break
        self.__check_network_state()
        self.__check_network_state('AT+UART_CUR=921600,8,1,0,0\r\n', "OK\r\n")
        self.uart = UART(UART.UART2, 921600, timeout=1000, read_buf_len=10240)

        # Initialize network instance with UART channel.
        try:
            self.nic = network.ESP8285(self.uart)
            # wait at ready to connect
            time.sleep_ms(500)
        except Exception as e:
            log.error(e)
            return False
        return True

    def connect(self, ssid: str, password: str) -> None:
        """
        Connect to existing WiFi network using ssid and password.
        Args:
            ssid (str): network ssid.
            password (str): network password.

        Returns:
            None
        """
        if self.nic:
            self.nic.connect(ssid, password)

    def ifconfig(self) -> tuple:
        """
        Retrieve ip configuration of the connect network.
        Examples:
            wifi = Wifi()
            wifi.connect(ssid, password)
            wifi.ifconfig()
            output => ('192.168.0.132', '255.255.255.0', '192.168.0.1', '0', '0', '98:a9:42:30:99:d2', 'Ubuntu-4G')
        Returns:
            tuple
        """
        if self.nic:
            return self.nic.ifconfig()

    def is_connected(self) -> bool:
        """
        Check if the network interface card is connected to a network.
        Returns:
            bool
        """
        if self.nic:
            return self.nic.isconnected()
        return False
