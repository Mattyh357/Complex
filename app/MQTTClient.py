import paho.mqtt.client as mqtt_client


class MQTTClient:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt_client.Client()

        # Assign event callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected: {rc}")
        # Subscribing in on_connect() - if we lose the connection and reconnect then subscriptions will be renewed
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}' with QoS {msg.qos}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    # Publish a message to a topic
    def publish(self, message):
        self.client.publish(self.topic, message)