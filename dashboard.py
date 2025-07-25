import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег (через парсинг профиля)")

# Загрузка списка пользователей
try:
    with open("users.txt") as f:
        users = [line.strip() for line in f if line.strip()]
except Exception as e:
    st.error(f"Ошибка при чтении users.txt: {e}")
    users = []

# Функция парсинга профиля
def get_duolingo_profile_data(username):
    url = f"https://www.duolingo.com/profile/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"username": username, "error": f"HTTP {r.status_code}"}

        soup = BeautifulSoup(r.text, "html.parser")

        # Найти XP
        xp = 0
        xp_block = soup.find("div", string=lambda s: s and "XP" in s)
        if xp_block:
            xp_text = xp_block.text.strip().replace(",", "")
            xp = int(xp_text.replace("XP", "").strip())

        # Найти streak
        streak = 0
        streak_block = soup.find("div", string=lambda s: s and "day streak" in s.lower())
        if not streak_block:
            streak_block = soup.find("div", string=lambda s: s and "🔥" in s)
        if streak_block:
            digits = ''.join(filter(str.isdigit, streak_block.text))
            streak = int(digits)

        return {
            "username": username,
            "totalXp": xp,
            "streak": streak
        }
    except Exception as e:
        return {"username": username, "error": str(e)}

# Основной блок
if not users:
    st.warning("Список пользователей пуст. Добавьте логины в users.txt.")
else:
    results = []
    st.subheader("🔍 Сбор данных с профилей...")
    progress = st.progress(0)
    step = 1 / len(users)

    for i, user in enumerate(users):
        data = get_duolingo_profile_data(user)
        if "error" in data:
            st.warning(f"⚠️ {user}: {data['error']}")
        else:
            st.success(f"✅ {user}: {data['totalXp']} XP, 🔥 {data['streak']} дней")
            results.append(data)
        progress.progress((i + 1) * step)
        time.sleep(0.5)  # анти-флуд защита

    df = pd.DataFrame(results)

    if not df.empty:
        df = df.sort_values("totalXp", ascending=False)

        st.subheader("📋 Рейтинг участников")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Очки (XP)")
        st.bar_chart(df.set_index("username")["totalXp"])

        st.subheader("🔥 Стрик (дни подряд)")
        st.bar_chart(df.set_index("username")["streak"])

        st.caption("Данные собраны без авторизации через парсинг публичных профилей.")
    else:
        st.warning("Не удалось собрать данные. Возможно, профили скрыты или структура сайта изменилась.")
