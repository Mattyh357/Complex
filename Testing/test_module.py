#!/usr/bin/env python

import time

import sys
import os

sys.path.append(os.path.abspath('./Complex'))
import led_module


# Initialize the LED connected to GPIO pin 20 (or whichever GPIO pin you are using)
led_module.init_led("16","20","21")

# Blink the LED 5 times with 1-second intervals

led_module.red_on()
time.sleep(1)
led_module.red_off()
time.sleep(1)

led_module.yellow_on()
time.sleep(1)
led_module.yellow_off()
time.sleep(1)

led_module.green_on()
time.sleep(1)
led_module.green_off()
time.sleep(1)

# for _ in range(5):
#     led_module.turn_on()
#     time.sleep(1)  # Keep the LED on for 1 second
#
#     led_module.turn_off()
#     time.sleep(1)  # Keep the LED off for 1 second

print("Blinking completed!")
