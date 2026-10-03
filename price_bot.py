import requests
import re
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

THRESHOLDS = {
    1050: "🟡",
    1000: "🔴",
    950: "🚨"
}

PRODUCT = "iPhone 17 512 Go"

URLS = [
    ("Amazon", "https://www.amazon.fr/s?k=iPhone+17+512+Go"),
    ("Fnac", "https://www.fnac.com/SearchResult/ResultList.aspx?Search=iPhone+17+512+Go"),
    ("Darty", "https://www.darty.com/nav/recherche?text=iPhone%2017%20512%20Go"),
    ("Boulanger", "https://www.boulanger.com/resultats?tr=iPhone%2017%20512%20Go"),
    ("Carrefour", "https://www.carrefour.fr/s?q=iPhone%2017%20512%20Go"),
    ("Cdiscount", "https://www.cdiscount.com/search/10/iphone+17+512+go.html"),
    ("E.Leclerc", "https://www.e.leclerc/recherche?q=iPhone%2017%20512%20Go"),
    ("Idealo", "https://www.idealo.fr/cat/19116F8899954/smartphones.html?q=iPhone+17+512+Go"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/128 Safari/537.36"
    )
}


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=20
    )


def extract_prices(text):
    prices = []

    patterns = [
        r'(\d{3,4})[,.](\d{2})\s*€',
        r'€\s*(\d{3,4})[,.](\d{2})',
        r'(\d{3,4})\s*€'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)

        for match in matches:
            if isinstance(match, tuple):
                number = match[0] + "." + match[1]
            else:
                number = match

            try:
                price = float(number)

                if 500 <= price <= 1600:
                    prices.append(price)

            except:
                pass

    return sorted(set(prices))


def check_store(store, url):

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        text = soup.get_text(" ", strip=True)

        prices = extract_prices(text)

        if not prices:
            return None

        return {
            "store": store,
            "price": prices[0],
            "url": url
        }

    except Exception as e:
        print(store, e)
        return None


def main():

    results = []

    for store, url in URLS:

        result = check_store(
            store,
            url
        )

        if result:
            results.append(result)

    print(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        )
    )

    for result in results:

        price = result["price"]

        threshold = None
        icon = None

        for limit, symbol in sorted(
            THRESHOLDS.items(),
            reverse=True
        ):

            if price <= limit:
                threshold = limit
                icon = symbol
                break

        if threshold is None:
            continue

        message = f"""
{icon} iPhone 17 512GB 价格警报

价格：{price:.2f}€
商家：{result["store"]}

触发线：≤ {threshold}€

⚠️ 请确认：
• 512GB
• 全新
• 无套餐
• 非翻新
• 卖家身份
• 最终含运费价格

{result["url"]}
"""

        send_telegram(message)


if __name__ == "__main__":
    main()