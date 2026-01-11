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
                <td>${device.name}</td>
                <td class="${statusClass}">${statusText}</td>
                <td>${lastSeenText}</td>
            </tr>`
        })

        tableHTML += '</table>';

        //Find the devices card and update its content
        const devicesCard = document.querySelector('.card');
        devicesCard.innerHTML = '<h2>Registered Devices</h2>' + tableHTML

        //Update dropdown select in command center
        updateDeviceDropdown(data.devices);
    } catch (error) {
        console.error("Error loading devices: ", error)
        alert('Error: Could not connect to server. Is it running?')
    }


}

/**
 * Updates the device dropdown with real devices in Command center
 */
function updateDeviceDropdown(devices){
    const select = document.getElementById('device-select')

    //Clear existing options except the first one
    select.innerHTML = '<option value="">Select device...</option>'

    //Add an option for each device
    devices.forEach( dev => {
        const option = document.createElement("option")
        option.value = dev.device_id;
        option.textContent = `${dev.device_id} (${dev.name})`
        select.appendChild(option)
    })
}

/**
 * Run a command
 */
async function runCommand() {
    const deviceId = document.getElementById('device-select').value;
    const testType = document.getElementById('test-type').value;
    const target = document.getElementById('target').value;
    
    //validate inputs
    if(!deviceId){
        alert("Please select a device!")
        return
    }
    if(!target){
        alert("Please enter a target!")
        return
    }
    
    try {
        //Create the parameters object
        const parameters = JSON.stringify({
            target: target,
            count: 4
        })

        //Build the URL with query parameters
        const url = `${API_URL}/commands/create?device_id=${deviceId}&command_type=${testType}&parameters=${encodeURIComponent(parameters)}`
        
        console.log('Sending command: ' + url)
    
        //send the POST request
        const response = await fetch(url, {
            method: 'POST'
        })

        if (response.ok) {
            alert('Command sent to ' + deviceId + '!\nThe agent will run the test in 10-20 seconds.\nRefresh the page to see the results')
        } else {
            alert('Failed to send the command. Status: ' + response.status)
        }
    }
    catch (error) {
        console.error("Error sending command:", error)
        alert('Error sending command. Is the server running?')
    }


}

/**
 * Get test results
 */
async function loadTestResults() {
    try {
        // Fetch data from server
        const response = await fetch(`${API_URL}/tests/results`);
        
        // Convert response to JSON
        const data = await response.json();
        
        const results = data.results;
        const resultCount = data.count;
        
        // Log data
        console.log('test-results:', data);
        
        // Build table
        let htmlTable = `
        <table>
            <tr>
                <th>Test ID</th>
                <th>Device ID</th>
                <th>Test Type</th>
                <th>Timestamp</th>
                <th>Target</th>
                <th>Result</th>
            </tr>`;
        
        results.forEach(result => {
            // Parse the result_data JSON string
            const resultData = JSON.parse(result.result_data);
            const success = resultData.success;
            
            // Choose color based on success
            const resultClass = success ? 'status-online' : 'status-offline';
            const resultText = success ? 'Success' : 'Failed';
            
            // Format timestamp to be more readable
            const date = new Date(result.timestamp);
            const timeAgo = getTimeAgo(date);
            
            // Add row for each result
            htmlTable += `
            <tr>
                <td><strong>${result.id}</strong></td>
                <td>${result.device_id}</td>
                <td>${result.test_type}</td>
                <td>${timeAgo}</td>
                <td>${result.target}</td>
                <td class="${resultClass}">${resultText}</td>
            </tr>`;
        });
        
        htmlTable += "</table>";
        
        // Inject to correct card
        const resultCard = document.getElementById("test-results");
        resultCard.innerHTML = "<h2>📊 Recent Test Results</h2>" + htmlTable;
        
    } catch (error) {
        console.error('Error loading test results:', error);
    }
}

// Helper function to format timestamps
function getTimeAgo(date) {
    const now = new Date();
    const secondsAgo = Math.floor((now - date) / 1000);
    
    if (secondsAgo < 60) {
        return `${secondsAgo} seconds ago`;
    } else if (secondsAgo < 3600) {
        const mins = Math.floor(secondsAgo / 60);
        return `${mins} minute${mins > 1 ? 's' : ''} ago`;
    } else if (secondsAgo < 86400) {
        const hours = Math.floor(secondsAgo / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleString();
    }
}


// Load devices when page loads
function main() {
    loadDevices()
    loadTestResults()
}
main()

//refresh every 10 seconds
setInterval(main, 10000)