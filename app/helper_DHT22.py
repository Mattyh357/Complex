# TODO MAKE SURE YOU FIX THIS!!! :) otherwise you're gonna be sitting there, crying and scratching your head wondering why it doesn't work......
# import board
# import adafruit_dht

from unittest.mock import MagicMock, PropertyMock
import random

board = MagicMock()
board.D18 = MagicMock()
adafruit_dht = MagicMock()
dht_device_mock = MagicMock()
type(dht_device_mock).temperature = PropertyMock(side_effect=lambda: random.randint(0, 100))
type(dht_device_mock).humidity = PropertyMock(side_effect=lambda: random.randint(0, 100))
adafruit_dht.DHT22.return_value = dht_device_mock
# TODO MOCK STOP


class Sensor_DHT22:

    dhtDevice: adafruit_dht.DHT22

    def __init__(self, pin_number):
        # using the BCM numbering scheme!!!!!!!

        # TODO MOCK
        pin_number = 18
        # TODO MOCK STOP

        self.dhtDevice = adafruit_dht.DHT22(self._get_pin_by_number(pin_number))

    def get_temperature(self):
        try:
            return self.dhtDevice.temperature
        except RuntimeError as error:
            return None

    def get_humidity(self):
        try:
            return self.dhtDevice.humidity
        except RuntimeError as error:
            return None

    def _get_pin_by_number(self, pin_number):
        pin_mapping = {
            2: board.D2,
            3: board.D3,
            4: board.D4,
            5: board.D5,
            6: board.D6,
            7: board.D7,
            8: board.D8,
            9: board.D9,
            10: board.D10,
            11: board.D11,
            12: board.D12,
            13: board.D13,
            14: board.D14,
            15: board.D15,
            16: board.D16,
            17: board.D17,
            18: board.D18,
            19: board.D19,
            20: board.D20,
            21: board.D21,
            22: board.D22,
            23: board.D23,
            24: board.D24,
            25: board.D25,
            26: board.D26,
            27: board.D27,
        }

        #TODO check
        return pin_mapping[pin_number]

