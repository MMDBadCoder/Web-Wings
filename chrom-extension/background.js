class ServiceManager {
    constructor() {
        this.server_domain = "http://mmd-net.ir:8000";
        this.services = [];
        this.blue_icon = {
            "19": "icons/blue.png",
            "38": "icons/blue.png"
        };
        this.green_icon = {
            "19": "icons/green.png",
            "38": "icons/green.png"
        };

        // Initialize the extension by fetching the domains
        console.log("Initializing extension...");
        this.fetchServices();
    }

    // Function to generate a UUID (simple version)
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Async function to get or generate the Client ID
    async getClientID() {
        console.log("Fetching Client ID...");
        return new Promise((resolve) => {
            chrome.storage.local.get('webWingsUniqueID', (data) => {
                let clientID;
                if (data.webWingsUniqueID) {
                    console.log("Client ID found in storage:", data.webWingsUniqueID);
                    clientID = data.webWingsUniqueID;
                } else {
                    clientID = this.generateUUID();
                    console.log("Generated new Client ID:", clientID);
                    chrome.storage.local.set({ webWingsUniqueID: clientID });
                }
                resolve(clientID);
            });
        });
    }

    // Find service from URL
    findServiceFromUrl(url) {
        console.log("Finding service for URL:", url);
        let domain;

        try {
            // Check if the URL has a protocol (http:// or https://)
            if (!/^https?:\/\//i.test(url)) {
                // If not, prepend "http://" to make it a valid URL
                url = 'http://' + url;
            }

            // Create a URL object
            const urlObj = new URL(url);
            domain = urlObj.hostname; // Extract the hostname (domain) from the URL
        } catch (error) {
            console.log('Invalid URL:', url); // Log the error
            return null; // Return null for invalid URLs
        }

        // Check the services array for the domain
        for (const service of this.services) {
            if (service.sniffing_domains.includes(domain)) {
                console.log("Service found for domain:", domain);
                return service; // Return the service if domain matches
            }
        }

        console.log("No service found for domain:", domain);
        return null;
    }


    // Fetch services and register listeners
    async fetchServices() {
        try {
            console.log("Fetching services...");
            const clientID = await this.getClientID();
            const response = await fetch(this.server_domain + "/services/?client_id=" + clientID);
            if (response.ok) {
                this.services = await response.json();
                console.log('Fetched services:', this.services);

                const all_sniffing_domains = this.services.flatMap(service =>
                    [...service.sniffing_domains]
                );
                console.log("Sniffing domains registered:", all_sniffing_domains);
                this.registerRequestListeners(all_sniffing_domains);
            } else {
                console.error('Failed to fetch services, status:', response.status);
            }
        } catch (error) {
            console.error('Error fetching services:', error);
        }
    }

    // Helper function to check if a request contains JSON
    isJsonRequest(headers) {
        const result = headers.some(header => header.value.toLowerCase().includes('application/json'));
        console.log("Is JSON request:", result);
        return result;
    }

    // Helper function to check if a response contains JSON
    isJsonResponse(headers) {
        const result = headers.some(header => header.name.toLowerCase() === 'content-type' && header.value.includes('application/json'));
        console.log("Is JSON response:", result);
        return result;
    }

    // Helper function to send sniffed data to the server and handle the response
    async sendSniffedData(url, method, headers, cookies, tabId) {
        console.log("Sending sniffed data for URL:", url);
        let service = this.findServiceFromUrl(url);
        if (service === null) {
            console.error("Unable to find service for this sniffing URL:", url);
            return;
        }

        if (service.status == "captured") {
            console.log("Sniffing data was not sent, because its captured: ", url);
            return;
        }

        const clientID = await this.getClientID();
        const data = {
            service_id: service.service_id,
            client_id: clientID,
            url: url,
            headers: headers,
            cookies: cookies
        };

        console.log("Sending data to the server:", data);

        fetch(this.server_domain + '/sniff/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                console.log('Server processed the request, result:', result);
                if (result.status !== undefined) {
                    service.status = result.status;
                }
                this.updateIcon(tabId, service.status);
            })
            .catch(error => {
                console.error('Error sending data to server:', error);
            });
    }

    // Register listeners for network requests only for listening domains
    registerRequestListeners(listeningDomains) {
        const urlPatterns = listeningDomains.map(domain => `*://${domain}/*`);
        console.log("Registering request listeners for url patterns:", urlPatterns);

        chrome.webRequest.onBeforeSendHeaders.addListener(
            (details) => this.requestListener(details),
            { urls: urlPatterns },
            ["requestHeaders"]
        );
    }

    // Request listener to check and process requests
    requestListener(details) {
        const url = details.url;
        console.log("Intercepted request to URL:", url);

        if (!this.isJsonRequest(details.requestHeaders)) {
            console.log(`Skipping non-JSON request: ${url}`);
            return;
        }

        const requestInfo = {
            url: details.url,
            method: details.method,
            headers: details.requestHeaders
        };

        chrome.cookies.getAll({ url: details.url }, (cookiesArray) => {
            const cookies = cookiesArray.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
            chrome.webRequest.onHeadersReceived.addListener(
                (responseDetails) => this.responseListener(responseDetails, requestInfo, cookies, details.tabId),
                { urls: [details.url] },
                ["responseHeaders"]
            );
        });
    }

    // Response listener to check if the response is JSON and then send data
    responseListener(responseDetails, requestInfo, cookies, tabId) {
        console.log("Intercepted response from URL:", requestInfo.url);

        if (!this.isJsonResponse(responseDetails.responseHeaders)) {
            console.log(`Skipping non-JSON response: ${responseDetails.url}`);
            return;
        }

        console.log(`Captured request with URL: ${requestInfo.url}`);
        this.sendSniffedData(requestInfo.url, requestInfo.method, requestInfo.headers, cookies, tabId);
    }

    // Function to change the icon based on the tab's URL
    updateIcon(tabId, status) {
        console.log(`Updating icon for tab ${tabId}, status: ${status}`);
        let icon = this.blue_icon;
        if (status === 'captured') {
            icon = this.green_icon;
        }
        chrome.action.setIcon({
            path: icon,
            tabId: tabId
        }, () => {
            console.log(`Set icon for tab ${tabId} to:`, icon);
        });
    }

    // Get the status of a tab
    getStatusOfTab(tab) {
        console.log(`Getting status for tab: ${tab.url}`);
        let service = this.findServiceFromUrl(tab.url);
        if (service === null) {
            console.log(`Status for tab: ignored`);
            return 'ignored';
        } else {
            console.log(`Status for tab: ${service.status}`);
            return service.status;
        }
    }

    // Start listening for tab updates
    listenForTabUpdates() {
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            console.log(`Tab updated: ${tabId}, URL: ${tab.url}`);
            this.updateIcon(tabId, this.getStatusOfTab(tab));
        });

        chrome.tabs.onActivated.addListener((activeInfo) => {
            chrome.tabs.get(activeInfo.tabId, (tab) => {
                console.log(`Tab activated: ${activeInfo.tabId}, URL: ${tab.url}`);
                this.updateIcon(activeInfo.tabId, this.getStatusOfTab(tab));
            });
        });
    }

    // Listen for messages from the popup
    listenForMessagesFromPopup() {
        this.getClientID().then(clientID => {
            chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
                console.log("Received message from popup:", message);

                if (message.action === 'getStatus') {
                    let service = serviceManager.findServiceFromUrl(message.domain);
                    if (service === null) {
                        sendResponse({ status: "ignored" });
                    } else {
                        sendResponse({ status: service.status });
                    }
                } else if (message.action === 'getAllData') {
                    sendResponse({ services: serviceManager.services, client_id: clientID });
                }
            });
        });
    }
}

// Initialize the ServiceManager instance
const serviceManager = new ServiceManager();
serviceManager.listenForTabUpdates();
serviceManager.listenForMessagesFromPopup();
