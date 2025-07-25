import requests
import time
import json
from bs4 import BeautifulSoup

# 🔗 Вопросы, которые отслеживаем
QUESTION_URLS = [
    "https://otvet.mail.ru/question/235202555",
    "https://otvet.mail.ru/question/239495038",
    "https://otvet.mail.ru/question/242195187",
    "https://otvet.mail.ru/question/242225874"
]

# ⏱ Интервал проверки — 10 минут (в секундах)
CHECK_INTERVAL = 600

# 🧾 Telegram-бот
BOT_TOKEN = "8001144863:AAGNrfE6r95DlfvSUgHFsiqlVyZUVFRcRO8"  # ← замени на свой
CHAT_ID = "2032893325"  # ← замени на свой

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
    "Cache-Control": "no-cache"
}

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"❌ Не удалось отправить в Telegram: {e}")

def get_answer_count(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        script_tags = soup.find_all("script", {"type": "application/ld+json"})
        for tag in script_tags:
            try:
                data = json.loads(tag.string)
                if "@graph" in data:
                    for obj in data["@graph"]:
                        if obj.get("@type") == "QAPage":
                            count = obj["mainEntity"].get("answerCount")
                            if count is not None:
                                return int(count)
            except Exception:
                continue
        return -1
    except Exception as e:
        print(f"❌ Ошибка при получении {url}: {e}")
        return -1

def send_notification(url, count):
    message = f"🆕 <b>Ответов стало: {count}</b>\n<a href=\"{url}\">Открыть вопрос</a>"
    send_to_telegram(message)

def main():
    print("📡 Бот запущен. Следим за вопросами...")
    answer_counts = {}

    for url in QUESTION_URLS:
        count = get_answer_count(url)
        if count == -1:
            print(f"⚠️ Не удалось получить ответы: {url}")
        else:
            print(f"✅ {url} — старт: {count} ответ(ов)")
            answer_counts[url] = count

    while True:
        time.sleep(CHECK_INTERVAL)
        for url in QUESTION_URLS:
            new_count = get_answer_count(url)
            if new_count == -1:
                print(f"⚠️ Ошибка при повторной проверке: {url}")
                continue

            old_count = answer_counts.get(url, -1)
            if new_count != old_count:
                print(f"📢 {url}\nОтветов: {old_count} → {new_count}")
                send_notification(url, new_count)
                answer_counts[url] = new_count
            else:
                print(f"⏱️ Без изменений ({new_count}) — {url}")

if __name__ == "__main__":
    main()
