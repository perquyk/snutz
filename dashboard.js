function runCommand() {
    // Get the values from the command form
    const deviceId = document.querySelector("#device-select").value
    const testType = document.querySelector("#test-type").value
    const target = document.querySelector("#target").value

    alert('running test!\nDevice: ' + deviceId + '\nTest: ' + testType + '\nTarget: ' + target)
}