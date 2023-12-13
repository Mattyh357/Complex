document.addEventListener('DOMContentLoaded', function() {
    console.log("Starting - http://" + SERVER_IP + ":" + SERVER_PORT)
    var socket = io.connect(SERVER_IP + ':' + SERVER_PORT);

    socket.on('connect', function() {
        console.log('Connected to server.');
    });

    socket.on('data', function(data) {
//        console.log("Received:", data);

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
