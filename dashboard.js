const API_URL = "http://localhost:8000";

/**
 * Loads devices from the server and displays them
 */
async function loadDevices(){
    // Get data from server
    try {
        //fetch data from the /devices endpoint
        const response = await fetch(`${API_URL}/devices`);

        //convert response to JSON
        const data = await response.json();

        //log the data
        console.log('Devices: ', data);

        //build html table
        let tableHTML = `
            <table>
                <tr>
                    <th>Device ID</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Last Seen</th>
                </tr>`

        //Loop through each deviec and add a row
        data.devices.forEach(device =>{
            //Check if device is online (seen in last 60 seconds)
            const lastSeenDate = new Date(device.last_seen);
            const now = new Date();
            const secondsAgo = (now - lastSeenDate) / 1000;
            const isOnline = secondsAgo < 60;

            //Choose status color and text
            const statusClass = isOnline ? 'status-online' : 'status-offline'
            const statusText = isOnline ? 'ONLINE' : 'OFFLINE'

            //format timestamp
            const lastSeenText = secondsAgo < 60 ? Math.floor(secondsAgo) + 'seconds ago' : Math.floor(secondsAgo / 60) + ' minutes ago';

            //Add a row for this device
            tableHTML += `
            <tr>
                <td><strong>${device.device_id}</strong></td>
                <td>${device.device_name}</td>
                <td class="${statusClass}">${statusText}</td>
                <td>${lastSeenText}</td>
            </tr>`
        })

        tableHTML += '</table>';

        //Find the devices card and update its content
        const devicesCard = document.querySelector('.card');
        devicesCard.innerHTML = '<h2>Registered Devices</h2>' + tableHTML
    } catch (error) {
        console.error("Error loading devices: ", error)
        alert('Error: Could not connect to server. Is it running?')
    }


}



/**
 * Run a command
 */
function runCommand() {
    const deviceId = document.getElementById('device-select').value;
    const testType = document.getElementById('test-type').value;
    const target = document.getElementById('target').value;
    
    alert('Running test!\nDevice: ' + deviceId + '\nTest: ' + testType + '\nTarget: ' + target);
}

// Load devices when page loads
loadDevices();