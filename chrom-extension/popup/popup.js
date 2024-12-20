
function getStatusOfTab(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const domain = new URL(tabs[0].url).hostname; // Extract the domain from the current tab
        chrome.runtime.sendMessage({ action: 'getStatus', domain: domain }, function (response) {
            callback(response.status);
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

function getClientId(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.runtime.sendMessage({ action: 'getClientId' }, function (response) {
            callback(response.client_id);
        });
    });
}

function setButtonListener() {
    getClientId(function (client_id) {
        const openLinkButton = document.getElementById('openLinkButton');
        openLinkButton.addEventListener('click', function () {
            chrome.tabs.create({ url: 'http://localhost:8000/sessions/' + client_id });
        });
    });
}



document.addEventListener('DOMContentLoaded', function () {
    updateStatusDisplay();
    setButtonListener();
});