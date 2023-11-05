import socket

import paho.mqtt.client as mqtt_client

class MQTTClient:

    broker: str
    port: int
    keep_alive: int
    qos: int
    retain: bool
    is_connected: bool

    client: mqtt_client.Client
    topics: []

    def __init__(self, broker, port, topics, keepalive=60, qos=0, retain=False, tls=None, auth=None):
        """
        Sets up all the fields and create instance of mqtt_client.Client().
        Additionally handles optional params and sets up event callbacks
        :param broker:      Address to the MQTT broker.
        :param port:        Port of the MQTT broker.
        :param topics:      List of topics that the client will use.
        :param keepalive:   (optional) How often to send keep-alive packet.
        :param qos:         (optional) Quality of Service: 0 - at most once, 1 - at least once, 2 - exactly once
        :param retain:      (optional) Retain message by the MQTT broker.
        :param tls:         (optional) TODO :)
        :param auth:        (optional) TODO :(
        """
        self.broker = broker
        self.port = port
        self.keep_alive = keepalive
        self.qos = qos
        self.retain = retain
        self.is_connected = False

        self.client = mqtt_client.Client()
        self.topics = topics

        #TODO tls
        # if tls:
        #     self.client.tls_set(tls)

        #TODO auth
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
        """
        Connect to MQTT broker and start a non-block loop.

        :return: Connection successful bool
        """
        self.is_connected = False

        try:
            self.client.connect(self.broker, self.port, self.keep_alive)
            self.client.loop_start()
        except socket.error as err:
            print(f"Connection failed: {err}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # TODO Handle
            return False

        self.is_connected = True
        return True

    def stop(self):
        """
        Disconnect the MQTT client and stop the non-blocking loop.
        """

        if self.is_connected is False:
            return False

        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, message, qos=None, retain=None):
        """
        Publish method to a topic with optional QoS and Retain flags.
        Will not attempt to publish anything if not connected.

        :param topic:   The topic where the message will be send to.
        :param message: Content of the message.
        :param qos:     (optional) Overrides the 'qos' flag set in the init.
        :param retain:  (optional) Overrides the 'retain' flag set in the init.
        """

        if self.is_connected is False:
            return False

        qos = self.qos if qos is None else qos
        retain = self.retain if retain is None else retain

        # send
        self.client.publish(topic, message, qos, retain)
