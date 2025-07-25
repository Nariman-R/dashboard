import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег (парсинг открытых профилей)")

# Загрузка usernames из users.txt
try:
    with open("users.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]
    if not usernames:
        st.error("Файл users.txt пустой.")
        st.stop()
except Exception as e:
    st.error(f"Ошибка при чтении users.txt: {e}")
    st.stop()

results = []
st.subheader("🔍 Сбор данных с профилей...")
progress = st.progress(0)
step = 1 / len(usernames)

def extract_json_from_html(html_text):
    # Ищем JSON внутри тега <script id="__NEXT_DATA__">
    soup = BeautifulSoup(html_text, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        try:
            return json.loads(script_tag.string)
        except Exception:
            return None
    return None

for i, username in enumerate(usernames):
    url = f"https://www.duolingo.com/profile/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            st.warning(f"⚠️ {username}: HTTP {res.status_code}")
            continue

        json_data = extract_json_from_html(res.text)
        if not json_data:
            st.warning(f"⚠️ {username}: не удалось извлечь JSON")
            continue

        # Путь к XP и стрику внутри JSON
        user_data = json_data["props"]["pageProps"]["userData"]

        total_xp = user_data.get("totalXp", 0)
        streak = user_data.get("streak", 0)

        results.append({
            "username": username,
            "totalXp": total_xp,
            "streak": streak
        })
        st.success(f"✅ {username}: {total_xp} XP, 🔥 {streak} дней")
    except Exception as e:
        st.warning(f"❌ {username}: ошибка {e}")

    progress.progress((i + 1) * step)

# Отображение рейтинга
if results:
    df = pd.DataFrame(results)
    df = df.sort_values("totalXp", ascending=False)

    st.subheader("📋 Рейтинг участников")
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Очки (XP)")
    st.bar_chart(df.set_index("username")["totalXp"])

    st.subheader("🔥 Стрик (дни подряд)")
    st.bar_chart(df.set_index("username")["streak"])
else:
    st.warning("Не удалось получить данные ни по одному пользователю.")
