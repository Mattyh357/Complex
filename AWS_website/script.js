var table = document.getElementById('dataTable');
var websocket;
let lastTimestamp = Date.now(); // Initial timestamp TODO remove
var currentSetName = "history"

function initAll() {
    initChart();
}
window.onload = initAll;



//////////////////////////////////////
//            DataManager           //
//////////////////////////////////////

const dataManager = (function() {
    let dataStores = {};

    return {
        add: function(setName, data) {
            if (!dataStores[setName]) {
                dataStores[setName] = [];
            }
            dataStores[setName].push(data);
        },
        getNewest: function(setName) {
            const dataStore = dataStores[setName];
            return dataStore.length > 0 ? dataStore[dataStore.length - 1] : null;
        },
        getAll: function(setName) {
            return dataStores[setName] || [];
        }
    };
})();


//////////////////////////////////////
//             Chart                //
//////////////////////////////////////

var chart = null;
var chartData = {
    labels: [], // For timestamps
    datasets: [
        {
            label: 'Value 1',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            data: []
        },
        {
            label: 'Value 2',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            data: []
        }
    ]
};


function initChart() {
    const ctx = document.getElementById('myChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: false,
            scales: {
                x: {
                    type: 'category'
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

//////////////////////////////////////
//              Utils               //
//////////////////////////////////////

function format_date(timestamp) {
    // Parse the timestamp into a Date object
    var date = new Date(timestamp);

    return date.toLocaleString('en-GB', { timeZone: 'UTC' });

    // // Function to add leading zero if necessary
    // function padTo2Digits(num) {
    //     return num.toString().padStart(2, '0');
    // }
    //
    // // Format the date
    // return padTo2Digits(date.getDate()) + '/' +
    //        padTo2Digits(date.getFullYear().toString().substr(-2)) + ' ' +
    //        padTo2Digits(date.getHours()) + ':' +
    //        padTo2Digits(date.getMinutes());
}


//////////////////////////////////////
//              Login               //
//////////////////////////////////////

function show_login(show) {
    document.getElementById("login").style.display = (show == false) ? "none" : "block";
    document.getElementById("menu").style.visibility = (show == true) ? "hidden" : "visible";
    document.getElementById("context").style.visibility = (show == true) ? "hidden" : "visible";
}

function login() {
    user_id = document.getElementById("txt_login").value;
    initWebSocket(user_id)
}

//////////////////////////////////////
//           WebSockets             //
//////////////////////////////////////

function initWebSocket(user_id) {

    let websocket = new WebSocket("wss://6hgbe1xt59.execute-api.us-east-1.amazonaws.com/production?userID=" + user_id);

    // Event handler when connection is opened
    websocket.onopen = function(event) {
        console.log("Connected to WebSocket");
        websocket.send(JSON.stringify({ action: 'GetData', user_id: user_id}));
        show_login(false);
    };

    // Event handler when receiving a message
    websocket.onmessage = function(event) {
        console.log("Message received: ", event.data);
        handle_data(event.data);
    };

    // Event handler for errors
    websocket.onerror = function(event) {
        console.error("WebSocket Error: ", event);
        document.getElementById("login_error").textContent = "Wrong!!! ";
    };

    // Event handler when connection is closed
    websocket.onclose = function(event) {
        console.log("WebSocket Connection Closed");
    };
}


function handle_data(message){

    try {
        // Parse the message as JSON
        const data = JSON.parse(message);

        // Check if the message is an array (multiple messages)
        if (Array.isArray(data)) {
            console.log("Received multiple messages:");

            data.forEach((item, index) => {
                console.log(`Message ${index + 1}:`, item);
                let newData = { timestamp: format_date(item.timestamp), temperature: item.temperature, humidity: item.humidity };
                dataManager.add('history', newData);
            });

            display_latest_values(dataManager.getNewest('history'));

            // TODO testing here - this line will probably be removed?
            switch_set_history();

        }
        // single message
        else if (data && typeof data === 'object' && 'message' in data) {
            console.log("Received a single message:", data.message);

            let newData = { timestamp: format_date(data.message.timestamp), temperature: data.message.temperature, humidity: data.message.humidity };
            dataManager.add('session', newData);

            if(currentSetName == 'session'){
                display_latest_values(newData);
                display_table_chart([newData]);
            }

        }
        // probably login or something :)
        else {
            console.log("Probably login data:", data);

            //TODO check if login is success...otherwise what's the point :)

            get_history_data();
        }
    } catch (e) {
        console.error("Error processing message:", e);
    }
}

function display_latest_values(data) {
    document.getElementById("data_temp").textContent = data.temperature;
    document.getElementById("data_time").textContent = data.timestamp;
    document.getElementById("data_humidity").textContent = data.humidity;
}

function display_table_chart(dataAarray) {
    dataAarray.forEach((data, index) => {
        // Add data to the table
        let row = table.insertRow(1);
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);

        cell1.innerHTML = data.timestamp;
        cell2.innerHTML = data.temperature + " °C";
        cell3.innerHTML = data.humidity + " %"

        //Add data to the chart
        chartData.labels.push(data.timestamp);
        chartData.datasets[0].data.push(data.temperature);
        chartData.datasets[1].data.push(data.humidity);
        chart.update();
    });
}


function switch_set_history() {
    currentSetName = 'history';
    clear_table_char();
    display_table_chart(dataManager.getAll("history"));
    display_latest_values(dataManager.getNewest("history"));
}

function switch_set_session() {
    currentSetName = 'session';
    clear_table_char();
    display_table_chart(dataManager.getAll("session"));
    display_latest_values(dataManager.getNewest("session"));
}

function clear_session() {
    clear_table_char();
    display_latest_values({ timestamp: 0, temperature: 0, humidity: 0 });
}

function clear_table_char() {

    chartData.labels = [];
    chartData.datasets[0].data = [];
    chartData.datasets[1].data = [];

    chart.update(); // Update the chart to reflect the changes


    let rowCount = table.rows.length;

    for (let i = rowCount - 1; i > 0; i--) {
        table.deleteRow(i);
    }

}




