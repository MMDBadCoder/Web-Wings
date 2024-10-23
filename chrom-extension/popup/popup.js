const server_domain = "http://localhost:8000"

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
        chrome.runtime.sendMessage({ action: 'getAllData'}, function (response) {
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

// Function to dynamically populate checkboxes
function populateCheckboxes() {
    const checkboxGroup = document.getElementById('checkboxGroup');
    getAllData(function (response) {
        // Example checkbox data
        const checkboxes = [];

        for (const service of response.services) {
            checkboxes.push(
                { id: service.service_id, name: service.name, disabled: service.status !== 'captured' }
            )
        }

        // Clear any existing checkboxes
        checkboxGroup.innerHTML = '';

        // Create checkboxes dynamically
        checkboxes.forEach(checkbox => {
            const checkboxElement = document.createElement('div');
            checkboxElement.className = 'ui checkbox checkbox-item';

            checkboxElement.innerHTML = `
            <input type="checkbox" id="checkbox-${checkbox.id}" ${checkbox.disabled ? 'disabled' : ''}>
            <label for="checkbox-${checkbox.id}">${checkbox.name}</label>
        `;
            checkboxGroup.appendChild(checkboxElement);
        });
    });
}

// Validation and Submission Logic on Button Click
document.getElementById('generateButton').addEventListener('click', function () {
    const startTime = parseInt(document.getElementById('startTime').value, 10);
    const endTime = parseInt(document.getElementById('endTime').value, 10);
    const validationError = document.getElementById('validationError');

    // Clear previous errors
    validationError.textContent = '';

    // Validate start time is greater than or equal to end time
    if (startTime < endTime) {
        validationError.textContent = 'Start time must be greater than or equal to end time.';
        return;
    }

    // Validate at least one checkbox is selected
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:not([disabled])');
    const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

    if (!isChecked) {
        validationError.textContent = 'Please select at least one checkbox.';
        return;
    }

    // Proceed with form submission if validation passes
    submitForm(startTime, endTime);
});

// Function to submit form data to the server
function submitForm(startTime, endTime) {
    const selectedServices = [];
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedServices.push(checkbox.id.replace('checkbox-', ''));
    });

    // Create the data object to be sent
    const formData = {
        start_time: startTime,
        end_time: endTime,
        services: selectedServices
    };

    // Send POST request to the server
    fetch(server_domain + '/request-for-report', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // You can display a success message to the user if needed
            alert('Report request was submitted successfully!');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to submit report request. Please try again.');
        });
}


// Initialize the status and checkboxes on popup load
document.addEventListener('DOMContentLoaded', function () {
    updateStatusDisplay();
    populateCheckboxes(); // Populate checkboxes on load
});