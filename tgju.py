import requests
from bs4 import BeautifulSoup
import jdatetime
import os

def fetch_prices():
    url = "https://www.tgju.org/"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')

        dollar_price_element = soup.find(id="l-price_dollar_rl")
        geram18_price_element = soup.find(id="l-geram18")
        
        dollar_price_element_info = dollar_price_element.find(class_="info-price") if dollar_price_element else None
        dollar_price = dollar_price_element_info.text.strip() if dollar_price_element_info else "Geram18 price element not found."

        geram18_price_element_info = geram18_price_element.find(class_="info-price") if geram18_price_element else None
        geram18_price = geram18_price_element_info.text.strip() if geram18_price_element_info else "Geram18 price element not found."

        return dollar_price, geram18_price

    except requests.RequestException as e:
        return f"An error occurred while fetching data: {e}", None

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

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
    
    dollar_price, geram18_price = fetch_prices()

    print(f"Fetched Dollar Price: {dollar_price}")
    print(f"Fetched Geram18 Price: {geram18_price}")

    if geram18_price:
        current_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        message = (
            f"*\u062a\u0627\u0631\u06cc\u062e:* {current_date}\n\n"
            f"\ud83c\uddfa\ud83c\uddf8 *\u062f\u0644\u0627\u0631 \u0622\u0645\u0631\u06cc\u06a9\u0627*\n"
            f"  #\u0642\u06cc\u0645\u062a: `{dollar_price}`\n"
            f"\ud83c\udf1f *\u06af\u0631\u0645 \u0637\u0644\u0627\u06cc 18*\n"
            f"  #\u0642\u06cc\u0645\u062a: `{geram18_price}`"
        )
        result = send_to_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
        print(result)
    else:
        print(dollar_price)
