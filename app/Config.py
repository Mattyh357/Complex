import json


class Config:
    config_file = "./config.json" # TODO meh

    # Config values
    port: int = 80
    test: str = "banana1"

    def __init__(self):
        self.load_config()


    def load_config(self):
        print("Loading")

        try:
            with open(self.config_file, 'r') as json_file:
                data = json.load(json_file)
                self.port = data.get('port', self.port)


        except FileNotFoundError:
            print("File not found - gonna save default values into the file")
            self.save_config()

        except json.JSONDecodeError:
            print("Error decoding JSON from file")
            exit(1)

    def save_config(self):
        print("Saving stuff :)")
        data = {
            'port': self.port
            , 'test1': self.test
        }

        with open(self.config_file, 'w') as json_file:
            json.dump(data, json_file)
