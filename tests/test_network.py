from unittest import TestCase
from unittest.mock import patch, MagicMock
from utils.network import WiFi

_SAMPLE_NETWORK_SCAN_RESPONSE = b'+CWLAP:(3, "network name", -50, "fd:a5:b8:dd:ce", 2,4,5,65)\r\n'


class UARTClass(MagicMock):
    """
    MagicMock subclass for UART call during network scan.
    """

    def read(self):
        return _SAMPLE_NETWORK_SCAN_RESPONSE


class TestWiFi(TestCase):
    @patch("utils.network.UART")
    @patch("utils.network.fm.register")
    def test_nic_initializing(self, mocked_fm_register, mocked_uart):
        wifi = WiFi()
        self.assertTrue(mocked_fm_register.called)
        self.assertTrue(mocked_fm_register.call_args)
        wifi.init()
        self.assertTrue(mocked_uart.called)
        _kwargs = mocked_uart.call_args.kwargs
        self.assertEqual(_kwargs["timeout"], 1000)
        self.assertEqual(_kwargs["read_buf_len"], 8192)

    @patch("utils.network.UART", new=UARTClass())
    def test_network_scan(self):
        wifi = WiFi()
        _networks = wifi.scan_networks()
        expected_result = [{
            'ssid': 'network name',
            'mac': 'fd:a5:b8:dd:ce',
            'meta': ['3', 'network name', '-50', 'fd:a5:b8:dd:ce', '2', '4', '5', '65']
        }]

        self.assertEqual(_networks, expected_result)

    @patch("utils.network.UART")
    def test_network_reset(self, mocked_uart):
        wifi = WiFi()
        self.assertIsNone(wifi.nic)
        wifi.reset()
        self.assertIsNotNone(wifi.nic)
        _kwargs = mocked_uart.call_args.kwargs
        self.assertEqual(_kwargs,{'timeout': 1000, 'read_buf_len': 10240})

    def test_network_connect(self):
        wifi = WiFi()
        wifi.reset()
        wifi.connect("network name", "fake-password")
        self.assertIsNotNone(wifi.nic)
