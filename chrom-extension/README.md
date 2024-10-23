# Network Request Capturer Extension

This is a simple Chrome extension that captures outgoing network requests (GET, POST, etc.) from web pages, retrieves the associated headers and cookies, and sends this data to a specified server for further processing.

## Features

- Captures network requests (e.g., GET, POST).
- Retrieves request headers and associated cookies.
- Sends the captured data to a server for further analysis.
- Optional popup interface to start and stop request capturing.

## Project Structure

```plaintext
/network-request-capturer-extension
│
├── /icons                    # Optional folder for icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
│
├── /popup                    # Optional folder for popup-related files
│   ├── popup.html            # Popup interface for the extension
│   └── popup.js              # Script to handle popup events
│
├── manifest.json             # The main configuration file for the extension
├── background.js             # Background script that captures network requests
└── README.md                 # Project documentation (this file)
