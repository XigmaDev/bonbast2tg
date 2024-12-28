import httpx
from bonbast.server import get_prices_from_api, get_token_from_main_page
from bs4 import BeautifulSoup
import os

BONBAST_URL = os.getenv("BONBAST_URL", "https://www.bonbast.com")
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

def merge_and_extract_tables(tables_soup):
    tables = []
    for table_soup in tables_soup:
        for tr in table_soup.find_all("tr")[1:]:
            table = [td.text for td in tr.find_all("td")]
            tables.append(table)
    return tables

def crawl_soup(url: str, post_data: dict) -> BeautifulSoup:
    response = httpx.post(url, data=post_data)
    if response.status_code != 200:
        raise Exception(f"Failed to crawl {url}")
    html = response.text
    return BeautifulSoup(html, 'html.parser')

def format_data_for_telegram(data):
    formatted_lines = []
    for key, values in data.items():
        formatted_lines.append(f"• {key.upper()}: \n  - Sell: {values['sell']} \n  - Buy: {values['buy']}")
    return "\n\n".join(formatted_lines)

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = httpx.post(telegram_url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to send message to Telegram: {response.text}")

def send_prices_to_telegram():
    token = get_token_from_main_page()
    currencies, coins, golds = get_prices_from_api(token)
    currencies_data = {c.code.lower(): {"sell": c.sell, "buy": c.buy} for c in currencies}
    coins_data = {c.code.lower(): {"sell": c.sell, "buy": c.buy} for c in coins}
    golds_data = {c.code.lower(): {"sell": c.price, "buy": c.price} for c in golds}

    merged_data = {**currencies_data, **coins_data, **golds_data}

    formatted_message = format_data_for_telegram(merged_data)
    send_to_telegram(formatted_message)

if __name__ == "__main__":
    send_prices_to_telegram()
