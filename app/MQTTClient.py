from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
from Logger import Logger
import sys


class MQTTClient:
    # AWS
    endpoint: str
    port: int
    path_ca: str
    path_cert: str
    path_key: str
    client_id: str
    topic: str
    clean_session = False
    keep_alive_secs = 30
    http_proxy_options = None

    on_connect_listener: callable = None
    on_disconnect_listener: callable = None
    on_messageSent_listener: callable = None

    is_connected: bool = False

    def __init__(self, endpoint, port, topic, ca_path, cert_path, key_path):
        """
        Creates MQTT connection

        :param endpoint: Endpoint
        :param port:  Port
        :param topic: Topic where data will be published
        :param ca_path:  Full path to the crt file
        :param cert_path: Full path to the certificate file
        :param key_path: Full path to the private key file
        """

        self.endpoint = endpoint
        self.port = port
        self.client_id = "complex"
        self.topic = topic

        self.path_ca = ca_path
        self.path_cert = cert_path
        self.path_key = key_path

        # Create a MQTT connection
        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            port=self.port,
            client_id=self.client_id,
            ca_filepath=self.path_ca,
            cert_filepath=self.path_cert,
            pri_key_filepath=self.path_key,

            clean_session=self.clean_session,
            keep_alive_secs=self.keep_alive_secs,
            http_proxy_options=self.http_proxy_options,

            on_connection_interrupted=self._on_connection_interrupted,
            on_connection_resumed=self._on_connection_resumed,
            on_connection_success=self._on_connection_success,
            on_connection_failure=self._on_connection_failure,
            on_connection_closed=self._on_connection_closed
            )

    def set_connect_listener(self, method: callable):
        """
        Setter for on connect listener that will be called when the MQTT client is connected
        :param method: on connect method
        """
        self.on_connect_listener = method

    def set_disconnect_listener(self, method):
        """
        Setter for on disconnect listener that will be called when the MQTT client is disconnected
        :param method: on disconnect method
        """
        self.on_disconnect_listener = method

    def set_message_sent_listener(self, method):
        """
        Setter for on message sent listener that will be called when the MQTT client receives back
        acknowledgement that message was sent
        :param method: on message sent method
        """
        self.on_messageSent_listener = method

    def connect(self):
        """
        Opens connection with the MQTT broker
        """
        Logger.info(f"MQTTClient - Connecting to {self.endpoint} with client ID '{self.client_id}'...")

        connect_future = self.mqtt_connection.connect()
        self._subscribe()
        connect_future.result()

    def disconnect(self):
        """
        Closes connection with the MQTT broker
        """
        Logger.info("MQTTClient - Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        self.is_connected = False

    def publish_json(self, message_json):
        """
        Publishes message in JSON format to the MQTT broker
        :param message_json: message to be published
        """
        self.mqtt_connection.publish(
            topic=self.topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

    def _subscribe(self):
        """
        Subscribes to the topic set in the constructor to be able to receive acknowledgements
        """
        Logger.info("MQTTClient - Subscribing to topic '{}'...".format(self.topic))
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=self.topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_message_received)

        subscribe_result = subscribe_future.result()
        Logger.info("MQTTClient - Subscribed with {}".format(str(subscribe_result['qos'])))

    def _on_connection_success(self, connection, callback_data):
        """
        Called when connection was established. If on connect listener was set, calls it.

        :param connection:
        :param callback_data:
        """

        assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
        Logger.info("MQTTClient - Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))
        self.is_connected = True
        if self.on_connect_listener is not None:
            self.on_connect_listener(callback_data)

    def _on_connection_closed(self, connection, callback_data):
        """
        Called when connection was closed. If on disconnect listener was set, calls it.

        :param connection:
        :param callback_data:
        """

        Logger.info("MQTTClient - Connection closed")
        self.is_connected = False
        if self.on_disconnect_listener is not None:
            self.on_disconnect_listener(callback_data)

    def _on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """
        Called when MQTT client received a message from the broker. If on message listener was set, calls it.

        :param topic:
        :param payload:
        :param dup:
        :param qos:
        :param retain:
        :param kwargs:
        """

        Logger.info("MQTTClient - Received message from topic '{}': {}".format(topic, payload))
        if self.on_messageSent_listener is not None:
            self.on_messageSent_listener(payload)

    def _on_connection_interrupted(self, connection, error, **kwargs):
        """
        Called when connection is accidentally lost.

        :param connection:
        :param error:
        :param kwargs:
        """
        Logger.info("MQTTClient - Connection interrupted. error: {}".format(error))

    def _on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """
        Called when an interrupted connection is re-established.
        :param connection:
        :param return_code:
        :param session_present:
        :param kwargs:
        """

        Logger.info("MQTTClient - Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            Logger.info("MQTTClient - Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

    def _on_resubscribe_complete(self, resubscribe_future):
        """
        Called when resubscribing is completed.

        :param resubscribe_future:
        """
        resubscribe_results = resubscribe_future.result()
        Logger.info("MQTTClient - Resubscribe results: {}".format(resubscribe_results))

        for top, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("MQTTClient - Server rejected resubscribe to topic: {}".format(top))

    def _on_connection_failure(self, connection, callback_data):
        """
        Called when a connection attempt fails.
        :param connection:
        :param callback_data:
        """

        assert isinstance(callback_data, mqtt.OnConnectionFailureData)
        Logger.error("MQTTClient - Connection failed with error code: {}".format(callback_data.error))