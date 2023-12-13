import sys
import os

sys.path.append(os.path.abspath('./Complex'))
import led_module

class MyLED:

    def __init__(self, pin_red, pin_yellow, pin_green):
        """
        Sets up led module and required PIN for individual LEDs.

        :param pin_red: Pin for red LED
        :param pin_yellow: Pin for yellow LED
        :param pin_green: Pin for green LED
        """
        #led_module.init_led(str(pin_red), str(pin_yellow), str(pin_green))
        led_module.init_led("16", "20", "21")


    def turn_on_red(self):
        """
        Turns ON red LED.
        """
        led_module.red_on()

    def turn_on_yellow(self):
        """
        Turns ON yellow LED.
        """
        led_module.yellow_on()

    def turn_on_green(self):
        """
        Turns ON green LED.
        """
        led_module.green_on()

    def turn_off_all(self):
        """
        Turns OFF all LEDs.
        """
        led_module.green_off()
        led_module.yellow_off()
        led_module.red_off()
