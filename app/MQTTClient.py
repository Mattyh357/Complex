import paho.mqtt.client as mqtt_client


class MQTTClient:

    broker: str
    port: int
    client: mqtt_client.Client

    # TODO default
    keep_alive: int
    qos: int
    retain: bool


    topics: []

    def __init__(self, broker, port, topics, keepalive=60, qos=0, retain=False, tls=None, auth=None):
        self.broker = broker
        self.port = port
        self.client = mqtt_client.Client()
        self.topics = topics
        self.keep_alive = keepalive
        self.qos = qos
        self.retain = retain

        #TODO retain
        #TODO tls
        #TODO auth

        # if tls:
        #     self.client.tls_set(tls)

        # if auth:
        #     self.client.username_pw_set(username, password)

        # Assign event callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected: {rc}")
        # Subscribe to all topics in the list
        for topic in self.topics:
            self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}' with QoS {msg.qos}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    # Publish a message to a topic
    def publish(self, topic, message, qos=None, retain=None):
        qos = self.qos if qos is None else qos
        retain = self.retain if retain is None else retain

        # send
        self.client.publish(topic, message, qos, retain)
