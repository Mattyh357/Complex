import sys

from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
import eventlet
import bcrypt

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from Config import Config
from Logger import Logger


class ConfigForm(FlaskForm):
    """
    Configuration for the Config form.

    Contains names and validation data that will be used to dynamically build the form.
    """

    web_ip = StringField('Web IP address', default="0", validators=[DataRequired()])
    web_port = StringField('Web interface port', default="0", validators=[DataRequired()])

    mqtt_endpoint = StringField('MQTT Endpoint', default="0")
    mqtt_port = StringField('MQTT port', default="0", validators=[DataRequired()])
    mqtt_topic = StringField('MQTT topic', default="0", validators=[DataRequired()])
    mqtt_path = StringField('MQTT Files path', default='0', validators=[DataRequired()])

    user_id = StringField('User ID', default='0', validators=[DataRequired()])

    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    """
    Configuration for the Login form.

    Contains password field and its validation.
    """
    password = StringField("Password", default='', validators=[DataRequired()])
    submit = SubmitField("Login")


class WebApp:

    flask: Flask
    socketio: SocketIO

    config: Config
    ip_address: str
    port: int
    is_running: bool
    authorized: bool = False

    def __init__(self, ip, port, config):
        """
        Create a Flask-SocketIO server

        Due to the simplicity of the web server, all routing handled by this class.
        Overrides default directories for templates and statics to ensure all web files can be in the web directory.

        :param ip:      IP address of the server.
        :param port:    Port number for the server to listen on.
        :param config:  Config object.
        """
        self.ip_address = ip
        self.port = port
        self.config = config

        eventlet.monkey_patch()
        self.flask = Flask(__name__, static_folder='web', template_folder='web')
        self.flask.config['SECRET_KEY'] = 'your_secret_key'  # TODO :)

        self.socketio = SocketIO(self.flask, cors_allowed_origins="*")


        # TODO don't be lazy and write some comments ;)

        @self.flask.route('/')
        def index():
            return render_template('index.html', ip_address=self.ip_address, port=self.port)

        @self.flask.route('/config', methods=['GET', 'POST'])
        def config():
            if self.authorized:
                return self.get_config_page()
            else:
                return self.get_login_page()


        @self.flask.route('/config-done')
        def config_done():
            link = "http://" + self.config.web_ip + ":" + str(self.config.web_port)
            # TODO fix config done - reboot
            return "config changed.... wait a sec for restart and then press this: <a href='"+link+"'>here</a>"

    def get_config_page(self):
        form = ConfigForm()

        if form.validate_on_submit():
            # SAVE DATA
            self.config.web_ip = form.web_ip.data
            self.config.web_port = form.web_port.data

            self.config.mqtt_endpoint = form.mqtt_endpoint.data
            self.config.mqtt_port = form.mqtt_port.data
            self.config.mqtt_topic = form.mqtt_topic.data
            self.config.mqtt_path = form.mqtt_path.data

            self.config.user_id = form.user_id.data

            self.config.save_config_file()

            return redirect(url_for('config_done'))

        # Display page
        form.web_ip.data = self.config.web_ip
        form.web_port.data = self.config.web_port

        form.mqtt_endpoint.data = self.config.mqtt_endpoint
        form.mqtt_port.data = self.config.mqtt_port
        form.mqtt_topic.data = self.config.mqtt_topic
        form.mqtt_path.data = self.config.mqtt_path

        form.user_id.data = self.config.user_id

        return render_template('config.html', form=form)

    def get_login_page(self):
        form = LoginForm()
        if form.validate_on_submit():
            # debug :)
            #print("hash of entered password: ", bcrypt.hashpw(form.password.data.encode(), bcrypt.gensalt()).decode())

            if bcrypt.checkpw(form.password.data.encode(), self.config.password.encode()):
                self.authorized = True
                Logger.info("Login successful")
                return redirect(url_for('config'))
            else:
                Logger.critical("Invalid password entered")
                form.password.errors.append("Invalid password")

        return render_template("login.html", form=form)

    def send_data(self, payload, event="data"):
        """Emit a server generated SocketIO event.

        This function emits a SocketIO event to one or more connected clients.
        Payload can contain simple text or JSON blob.

        :param payload: Payload that will be sent.
        :param event:   (optional) The name of the user event to emit.
        """

        self.socketio.emit(event, payload)

    def start(self):
        """
        Attempts to start a Flask-SocketIO server.
        Using previously configured flask application instance, IP address, and port tries to start a server.
        If server starts successfully sets is_running flag to True.
        :return: Was server started
        """
        try:
            self.socketio.run(self.flask, host=self.ip_address, port=self.port, debug=False)
        except Exception as e:
            Logger.critical(f"WebApp: {e}")


    def stop(self):
        """
        Print a smiley face ....... Yeah.. I know :D
        """
        # TODO :)
        print(":)")
