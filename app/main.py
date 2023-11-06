import threading
import time
import random

from Config import Config
from MQTTClient import MQTTClient
from WebApp import WebApp
from utils import get_local_ip
from Logger import Logger


Logger(log_file="my_app.log")

class App:

    web: WebApp
    start_time: float
    config: Config
    mqtt: MQTTClient | None

    def __init__(self):
        self.config = Config()
        self.start_time = time.time()

    def run(self):
        ip_address = get_local_ip()
        self.mqtt = None

        Logger.info(f"App starting - ip: {ip_address}")

        # Start web
        # TODO do some check if the IP fails or something :)
        Logger.info(f"Web server - STARTING - port: {self.config.web_port}")

        self.web = WebApp(ip_address, self.config.web_port, self.config)
        web_thread = threading.Thread(target=self.web.start)
        web_thread.start()
        # TODO IF running
        # Logger.critical("Couldn't start web server - terminating app")

        # DEBUG
        # exit(1)
        # DEBUG

        # Start MQTT publisher

        if self.config.mqtt_broker != "":
            Logger.info(f"MQTT - Starting")
            topic = [self.config.mqtt_topic_temperature, self.config.mqtt_topic_humidity, self.config.mqtt_topic_uptime]
            self.mqtt = MQTTClient(self.config.mqtt_broker, self.config.mqtt_port, topic)
            self.mqtt.start()

        # Let's go ;)
        Logger.info(f"App initialized on: {ip_address}:{self.config.web_port}")

        time.sleep(2)  # Give some time for stuff to start before running anything else
        self.main_loop()


    def get_uptime(self):
        uptime_seconds = time.time() - self.start_time

        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_string = f"{int(days)}d:{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

        return uptime_string

    def main_loop(self):
        while True:
            time.sleep(1)

            temp = random.randint(0, 100)
            humidity = random.randint(0, 100)
            uptime = self.get_uptime()

            data = {
                'temperature': temp,
                'humidity': humidity,
                'uptime': uptime,
                'cloud': "banana"
            }

            # Web
            self.web.send_data(data)

            # MQTT
            # TODO if I don't have client don't do this :)
            if self.mqtt is not None:
                if self.mqtt.is_connected:
                    self.mqtt.publish(self.config.mqtt_topic_temperature, temp)
                    self.mqtt.publish(self.config.mqtt_topic_humidity, humidity)
                    self.mqtt.publish(self.config.mqtt_topic_uptime, uptime)
                else:
                    print("MQTT: trying to reconnect")
                    # self.mqtt.start()


if __name__ == '__main__':
    app = App()
    app.run()
