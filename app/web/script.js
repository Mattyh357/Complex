document.addEventListener('DOMContentLoaded', function() {
    console.log("Starting - http://192.168.1.106:1234")

    var socket = io.connect('localhost:1234');

    socket.on('connect', function() {
        console.log('Connected to server.');
    });

    socket.on('data', function(data) {
        console.log("Received:", data);

        temperature = data.temperature
        humidity = data.humidity
        uptime = data.uptime
        cloud = data.cloud

        document.getElementById("data_temp").textContent = temperature;
        document.getElementById("data_humidity").textContent = humidity;
        document.getElementById("data_uptime").textContent = uptime;
        document.getElementById("data_cloud").textContent = cloud;

    });
});
