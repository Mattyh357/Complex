import signal
import threading
import time
import random

from Config import Config
from MQTTClient import MQTTClient
from helper_DHT22 import Sensor_DHT22
from helper_Button import MyButton
from helper_LED import MyLED
from WebApp import WebApp
from Logger import Logger
import json
import subprocess

PIDIR = "/home/pi/matt/Complex/"

# DHT22 PIN
DHT22_PIN = 23

# LED PINs
LED_PIN_RED = 16
LED_PIN_YELLOW = 20
LED_PIN_GREEN = 21

# Button
BTN_DEV = "/dev/sbtn"


# Loop brake for CPU rest
CPU_SLEEP = 0.1

Logger(log_file=PIDIR + "my_app.log")

class App:

    web: WebApp
    config: Config
    mqtt: MQTTClient

    # Hardware
    sensor: Sensor_DHT22
    led: MyLED
    button: MyButton

    # Timers
    start_time: float
    timer_web: float
    timer_web_interval: float = 1

    running: bool

    def __init__(self):
        """
        Initialize timers, Config, Button and LED helpers
        """
        self.config = Config(PIDIR + "config.json")

        self.start_time = time.time()
        self.timer_web = time.time()

        self.button = MyButton(BTN_DEV)
        self.led = MyLED(LED_PIN_RED, LED_PIN_YELLOW, LED_PIN_GREEN)

    def start(self):
        """
        Start the application. Mainly starts the webserver and initializes the MQTT Client.
        Also turns on the RED LED indicating that the system is in its starting phase.
        Lastly, stars the main loop.
        """

        Logger.info("Starting C.O.M.P.L.E.X")
        self.led.turn_on_red()

        # Sensor
        # TODO check if all ok
        self.sensor = Sensor_DHT22(DHT22_PIN)

        # Start web
        # TODO do some check if the IP fails or something
        Logger.info(f"Web server - STARTING - {self.config.web_ip}: {self.config.web_port}")
        self.web = WebApp(self.config.web_ip, self.config.web_port, self.config)
        web_thread = threading.Thread(target=self.web.start)
        web_thread.start()

        # START
        self.mqtt = MQTTClient(
            self.config.mqtt_endpoint
            , self.config.mqtt_port
            , self.config.mqtt_topic
            , self.config.mqtt_path + "root-CA.crt"
            , self.config.mqtt_path + "Complex_device.cert.pem"
            , self.config.mqtt_path + "Complex_device.private.key"
        )

        self.mqtt.set_connect_listener(self.mqtt_connected)
        self.mqtt.set_disconnect_listener(self.mqtt_disconnected)
        self.mqtt.set_message_sent_listener(self.mqtt_message_sent)

        mqtt_thread = threading.Thread(target=self.mqtt.connect)
        mqtt_thread.start()

        # Start MainLoop after a short delay
        time.sleep(1)  # Give some time for stuff to start before running anything else
        Logger.info(f"App initialized on: {self.config.web_ip}:{self.config.web_port}")

        self.running = True
        self.main_loop()

    def stop(self):
        """
        Stops the Application by setting self.running field to False to ensure proper shutdown of all services.
        """
        print("Closing C.O.M.P.L.E.X")
        self.running = False

    def get_uptime(self):
        """
        Constructs a string with current uptime of the application
        :return: Returns uptime of the application in format day:hour:minute:second
        """
        uptime_seconds = time.time() - self.start_time

        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_string = f"{int(days)}d:{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

        return uptime_string

    def get_payload(self):
        """
        Generates payload containing user_id, uptime, temperature and humidity
        :return: JSON string with payload
        """

        temp = self.sensor.get_temperature()
        humidity = self.sensor.get_humidity()
        uptime = self.get_uptime()

        data = {
            'user_id': self.config.user_id,
            'uptime': uptime,
        }

        if temp is not None:
            data["temperature"] = temp

        if humidity is not None:
            data["humidity"] = humidity

        return data

    def mqtt_connected(self, data=None):
        """
        Called when MQTT is connected and turns the green LED on.
        :param data: optional data (not used)
        """
        self.led.turn_on_green()

    def mqtt_disconnected(self, data=None):
        """
        Called when MQTT is disconnected and turn the red LED on.
        :param data: optional data (not used)
        """
        self.led.turn_on_red()

    def mqtt_message_sent(self, data=None):
        """
        Called when MQTT receives ack for a message sent and turns the green LED on.
        :param data: optional data (not used)
        """
        self.led.turn_on_green()



    def main_loop(self):
        """
        Main loop of the application. Starts with a small delay to save a CPU a bit.
        Firstly checks if the MQTT is connected,it now, turns on the yellow LED and tries to connect.
        Secondly, if it's time to push update to the web server, it does so.
        Next, check if the button is pressed, if so and if the MQTT client is connected, pushes the update to it.
        Lastly, when the loop ends (running == False) the app goes through proper shutdown.
        :return:
        """
        while self.running:
            time.sleep(CPU_SLEEP)  # Small delay prevent CPU going mental

            # # Check MQTT
            if not self.mqtt.is_connected:
                Logger.info("MQTT: trying to connect TODO some ip")
                self.mqtt.connect()
                self.led.turn_on_yellow()
                time.sleep(1)

                if not self.mqtt.is_connected:
                    continue
                else:
                    Logger.info("MQTT: connected")
                    self.led.turn_on_green()

            current_time = time.time()

            # WEB publish
            if self.timer_web < current_time:
                self.timer_web = self.timer_web_interval - CPU_SLEEP + time.time()
                data = self.get_payload()
                self.web.send_data(data)

            # MQTT publish
            if self.button.is_pressed():
                if self.mqtt.is_connected:
                    data = self.get_payload()
                    Logger.info("Sending data: " + json.dumps(data))
                    self.led.turn_on_yellow()
                    time.sleep(0.5)  # Give some time to stop holding the button and make the yellow up for a bit longer
                    self.mqtt.publish_json(json.dumps(data))
                else:
                    Logger.info("Button pressed, but MQTT not connected. Message not sent.")

        # End of While loop

        # Clean up
        time.sleep(1)
        Logger.info("Clean up")
        self.led.turn_off_all()
        self.web.stop()
        # self.mqtt.disconnect()

        Logger.info("Bye")



def close_app(signal_number, frame):
    """
    Initializes app closing procedure
    :param signal_number:
    :param frame:
    """
    app.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, close_app)
    signal.signal(signal.SIGINT, close_app)

    app = App()
    app.start()
