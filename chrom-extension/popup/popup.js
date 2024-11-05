
// Function to get the status of the current tab asynchronously
function getStatusOfTab(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const domain = new URL(tabs[0].url).hostname; // Extract the domain from the current tab
        chrome.runtime.sendMessage({ action: 'getStatus', domain: domain }, function (response) {
            callback(response.status);
        });
    });
}

function getAllData(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.runtime.sendMessage({ action: 'getAllData' }, function (response) {
            console.log("Received message response in popup:", response);
            callback(response);
        });
    });
}

// Function to update the UI based on the status
function updateStatusDisplay() {
    getStatusOfTab(function (status) {
        const statusDisplay = document.getElementById('statusText');
        const icon = statusDisplay.querySelector('.icon');
        const text = statusDisplay.querySelector('span');

        if (status === 'ignored') {
            statusDisplay.className = 'status-message ignored';
            icon.className = 'icon exclamation triangle';
            text.textContent = 'This website is ignored';
        } else if (status === 'captured') {
            statusDisplay.className = 'status-message captured';
            icon.className = 'icon check circle';
            text.textContent = 'Access point was captured';
        } else if (status === 'sniffing') {
            statusDisplay.className = 'status-message sniffing';
            icon.className = 'icon sync alternate';
            text.textContent = 'Try to sniffing access points';
        }
    });
}

// Initialize the status and checkboxes on popup load
document.addEventListener('DOMContentLoaded', function () {
    updateStatusDisplay();
});