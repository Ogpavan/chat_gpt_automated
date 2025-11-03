 
# ChatGPT CLI Automation (`chat.py`)

This script provides a command-line interface (CLI) to interact with ChatGPT (https://chatgpt.com) using Selenium WebDriver automation. It launches a browser, handles login modals, sends messages, and prints responses in the terminal.

## Features

- Fully automated browser session using Chrome and Selenium.
- Handles ChatGPT login modals (e.g., "Stay logged out").
- Detects and handles rate limits and session timeouts.
- Automatically restarts the browser session after a configurable number of messages.
- CLI interface for interactive chatting.

## Requirements

- Python 3.8+
- Google Chrome browser installed
- The following Python packages:
  - selenium
  - webdriver-manager

Install dependencies with:
```sh
pip install selenium webdriver-manager
```

## Usage

Run the script directly:
```sh
python chat.py
```
Type your message at the prompt and press Enter. Type `exit` or `quit` to stop.

## Configuration

- The script uses headless Chrome for performance.
- User agent is randomized to reduce detection.
- Session restarts after 50 messages to avoid rate limits (configurable in `max_messages_per_session`).

## File Structure

- `wait_for_stable_div`: Waits for ChatGPT's response to stabilize before reading.
- `handle_login_modal`: Handles login modals by clicking "Stay logged out".
- `check_for_rate_limit`: Detects rate limit messages.
- `create_driver`: Configures and launches the Chrome WebDriver.
- `initialize_chatgpt`: Loads ChatGPT and waits for readiness.
- `send_message`: Sends a message and retrieves the response.
- `main`: CLI loop for user interaction.

## Troubleshooting

- If you encounter errors related to ChromeDriver, ensure Chrome is installed and up to date.
- If rate limits are frequent, try increasing the delay or reducing message frequency.

## License

For personal and educational use only. Not affiliated with OpenAI or ChatGPT.
 
 
