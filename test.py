import requests
from bs4 import BeautifulSoup
import jdatetime
import os

url = "https://www.tgju.org/gold-chart"
nameslugs = ["geram18", "geram24", "silver_999", "gold_17_transfer"]
market_data = {}
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")


def fetch_market_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for nameslug in nameslugs:
            market_row = soup.select_one(f"tr[data-market-nameslug='{nameslug}']")
            if market_row:
                title = market_row.select_one('th').text.strip()
                tds = market_row.select('td')
                market_data[nameslug] = {
                    "Title": title,
                    "Current Price": tds[0].text.strip(),
                    "Price Change": tds[1].text.strip(),
                    "Previous Price": tds[2].text.strip(),
                    "Highest Price Today": tds[3].text.strip(),
                    "Last Updated": tds[4].text.strip(),
                }

        return market_data

    except Exception as e:
        print(f"Error fetching market data: {e}")
        return {}


def send_to_telegram(bot_token, chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(telegram_url, json=payload)
        response.raise_for_status() 
        return "Message sent successfully."
    except requests.RequestException as e:
        return f"An error occurred while sending the message: {e}"


def format_message(market_data):
    try:
        current_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        message = f"تاریخ: {current_date}\n\n"

        for slug, data in market_data.items():
            if slug == "geram18":
                icon = "🌟"
                title = "طلای 18 عیار"
            elif slug == "geram24":
                icon = "🌟"
                title = "طلای 24 عیار"
            elif slug == "gold_17_transfer":
                icon = "🌟"
                title = "حباب آبشده"
            elif slug == "silver_999":
                icon = "🥈"
                title = "نقره 999"
            else:
                icon = "💰"
                title = slug

            message += f"{icon} {title}  #قیمت: {data['Current Price']}\n"

        return message

    except Exception as e:
        print(f"Error formatting message: {e}")
        return "Error creating the message."


if __name__ == "__main__":
    market_data = fetch_market_data()
    if market_data:
        print("Market data fetched successfully.")
        for slug, data in market_data.items():
            print(f"Market: {slug}")
            for key, value in data.items():
                print(f"  {key}: {value}")
            print("-" * 40)

        telegram_message = format_message(market_data)
        send_to_telegram(TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID,telegram_message)
    else:
        print("No market data available.")
