# Bonbast2TG

Bonbast2TG is a project that fetches exchange rates from Bonbast and sends updates to a Telegram channel.

## Features

- Fetches exchange rates from Bonbast with (https://github.com/SamadiPour/bonbast)
- Sends updates to a specified Telegram channel
- Configurable update intervals

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/bonbast2tg.git
    ```
2. Navigate to the project directory:
    ```sh
    cd bonbast2tg
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the project directory with the following content:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    ```

## Usage

Run the script to start fetching exchange rates and sending updates:
```sh
python main.py
```
