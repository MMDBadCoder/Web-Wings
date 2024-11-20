document.getElementById("session-form").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent page reload

    const sessionId = document.getElementById("session-id").value;

    if (!sessionId) {
        alert("Please enter a session ID.");
        return;
    }

    // Get the currently active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
        alert("Could not get the active tab.");
        return;
    }

    // Extract the domain from the active tab's URL
    const tabUrl = new URL(tab.url); // Create a URL object from the tab's URL
    const originDomain = tabUrl.origin; // This gives the full origin (protocol + domain + port)

    console.log(`Tab Origin Domain: ${originDomain}`);

    // Execute script to log the session ID in the tab's console
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: logSessionId,
        args: [sessionId],
    });

    // Reload the tab after logging
    chrome.tabs.reload(tab.id);
    window.close();
});



// Function to log the session ID to the console of the tab
function logSessionId(sessionId) {
    console.log(`Session ID: ${sessionId}`);
}

async function retrieveSession(sessionId) {
    const result = {};
    const headers = {
        'Accept': 'application/json',
    };
    const params = new URLSearchParams({ session_id: sessionId });

    try {
        const response = await fetch(`http://web-wings.ir/get-shared-session/?${params}`, { headers });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const servicesData = await response.json();

        servicesData.forEach(s => {
            const serviceId = s.service_id;
            const headers = s.headers;
            const cookies = s.cookies;
            result[serviceId] = { headers, cookies }; // Assuming RetrievedSession just stores headers and cookies
        });
    } catch (error) {
        console.error('Error fetching session:', error);
    }

    return result;
}
