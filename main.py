import httpx
from bonbast.server import get_prices_from_api, get_token_from_main_page
from bs4 import BeautifulSoup
import os
import jdatetime

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
    currency_flags = {
        'usd': '🇺🇸', 'eur': '🇪🇺', 'gbp': '🇬🇧', 'jpy': '🇯🇵', 'cny': '🇨🇳',
        'aud': '🇦🇺', 'cad': '🇨🇦', 'chf': '🇨🇭', 'sek': '🇸🇪', 'nzd': '🇳🇿',
        'nok': '🇳🇴', 'rub': '🇷🇺', 'thb': '🇹🇭', 'sgd': '🇸🇬', 'hkd': '🇭🇰',
        'azn': '🇦🇿', 'amd': '🇦🇲', 'dkk': '🇩🇰', 'aed': '🇦🇪', 'try': '🇹🇷',
        'sar': '🇸🇦', 'inr': '🇮🇳', 'myr': '🇲🇾', 'afn': '🇦🇫', 'kwd': '🇰🇼',
        'iqd': '🇮🇶', 'bhd': '🇧🇭', 'omr': '🇴🇲', 'qar': '🇶🇦', 'emami1': '🏅',
        'azadi1g': '🏅', 'azadi1': '🏅', 'azadi1_2': '🏅', 'azadi1_4': '🏅',
        'mithqal': '🏅', 'gol18': '🏅', 'ounce': '🏅', 'bitcoin': '₿'
        # Add more currencies and their flags as needed
    }
    
    currency_names_persian = {
        'usd': 'دلار آمریکا', 'eur': 'یورو', 'gbp': 'پوند انگلیس', 'jpy': 'ین ژاپن', 'cny': 'یوان چین',
        'aud': 'دلار استرالیا', 'cad': 'دلار کانادا', 'chf': 'فرانک سوئیس', 'sek': 'کرون سوئد', 'nzd': 'دلار نیوزیلند',
        'nok': 'کرون نروژ', 'rub': 'روبل روسیه', 'thb': 'بات تایلند', 'sgd': 'دلار سنگاپور', 'hkd': 'دلار هنگ کنگ',
        'azn': 'منات آذربایجان', 'amd': 'درام ارمنستان', 'dkk': 'کرون دانمارک', 'aed': 'درهم امارات', 'try': 'لیر ترکیه',
        'sar': 'ریال عربستان', 'inr': 'روپیه هند', 'myr': 'رینگیت مالزی', 'afn': 'افغانی افغانستان', 'kwd': 'دینار کویت',
        'iqd': 'دینار عراق', 'bhd': 'دینار بحرین', 'omr': 'ریال عمان', 'qar': 'ریال قطر', 'emami1': 'سکه امامی',
        'azadi1g': 'سکه آزادی گرمی', 'azadi1': 'سکه بهار آزادی', 'azadi1_2': 'نیم سکه آزادی', 'azadi1_4': 'ربع سکه آزادی',
        'mithqal': 'مثقال طلا', 'gol18': 'طلای ۱۸ عیار', 'ounce': 'اونس طلا', 'bitcoin': 'بیت‌کوین'
        # Add more currencies and their Persian names as needed
    }
    
    formatted_lines = []
    
    for key, values in data.items():
        flag = currency_flags.get(key.lower(), '')
        name_persian = currency_names_persian.get(key.lower(), key.upper())
        
        if key.lower() not in ['bitcoin', 'ounce']:
            sell_price = f"{int(values['sell']):,} تومن"
            buy_price = f"{int(values['buy']):,} تومن"
        else:
            sell_price = f"{values['sell']} دلار"
            buy_price = f"{values['buy']} دلار"
        
        formatted_lines.append(f"{flag} • {name_persian}: \n  - فروش: {sell_price} \n  - خرید: {buy_price}")

    jalali_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
    formatted_message = f"تاریخ: {jalali_date}\n\n{formatted_message}"

    formatted_message += "\n\n@bonbast2tg"
    
    return formatted_message


def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"\u200F{message}", "parse_mode": "Markdown"}
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
