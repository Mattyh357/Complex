import json
from Logger import Logger


class Config:
    config_file: str

    # Config values with their defaults
    web_ip: str = "0.0.0.0"
    web_port: int = 8070

    mqtt_endpoint: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "complex/data"
    mqtt_path: str = ""

    user_id: str = "123"
    password: str = "$2b$12$OjQDE8ODCN/MjrfI72ljmeJdf2ExM8Nz8f0kmmM1WuXpz.qmNivo6"  # Hash for "admin"

    def __init__(self, file):
        """
        Sets config file and loads it
        :param file: full path to the config.json file
        """

        self.config_file = file
        self.load_config_file()

    def load_config_file(self):
        """
        Loads all config values. If the file hasn't been created yes, creates one with default values.
        If any value is missing in the config file, it is replaced with default one.
        Exits and logs Error when the config file is corrupted.
        """
        try:
            with open(self.config_file, 'r') as json_file:
                data = json.load(json_file)

                self.web_ip = data.get('web_ip', self.web_ip)
                self.web_port = data.get('web_port', self.web_port)

                self.mqtt_endpoint = data.get('mqtt_endpoint', self.mqtt_endpoint)
                self.mqtt_port = data.get('mqtt_port', self.mqtt_port)
                self.mqtt_topic = data.get('mqtt_topic', self.mqtt_topic)
                self.mqtt_path = data.get('mqtt_path', self.mqtt_path)

                self.user_id = data.get('user_id', self.user_id)
                self.password = data.get('password', self.password)

        except FileNotFoundError:
            Logger.info("File not found - gonna save default values into the file")
            self.save_config_file()

        except json.JSONDecodeError:
            Logger.error("Error decoding JSON from file")
            exit(1)


    def save_config_file(self):
        """
        Saves all value fields into the config file
        """

        Logger.info("Saving stuff :)")
        data = {
            'web_port': int(self.web_port)
            , 'web_ip': self.web_ip
            , 'mqtt_endpoint': self.mqtt_endpoint
            , 'mqtt_port': int(self.mqtt_port)
            , 'mqtt_topic': self.mqtt_topic
            , 'mqtt_path': self.mqtt_path
            , 'user_id': self.user_id
            , 'password': self.password
        }

        with open(self.config_file, 'w') as json_file:
            json.dump(data, json_file, indent=2)



