import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег (по user_id из users.txt)")

# Загрузка списка ID
try:
    with open("users.txt", "r") as f:
        user_ids = [line.strip() for line in f if line.strip()]
    if not user_ids:
        st.error("Файл users.txt пустой.")
        st.stop()
except Exception as e:
    st.error(f"Ошибка при чтении users.txt: {e}")
    st.stop()

results = []
st.subheader("🔍 Сбор данных с Duolingo API...")
progress = st.progress(0)
step = 1 / len(user_ids)

for i, user_id in enumerate(user_ids):
    url = f"https://www.duolingo.com/users/{user_id}"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.warning(f"⚠️ ID {user_id}: HTTP {response.status_code}")
            continue

        data = response.json()
        username = data.get("username", f"user_{user_id}")
        total_xp = data.get("totalXp", 0)
        streak = data.get("site_streak", 0)

        results.append({
            "user_id": user_id,
            "username": username,
            "totalXp": total_xp,
            "streak": streak
        })
        st.success(f"✅ {username}: {total_xp} XP, 🔥 {streak} дней")
    except Exception as e:
        st.warning(f"❌ ID {user_id}: ошибка {e}")
    
    progress.progress((i + 1) * step)

# Отображение результатов
if results:
    df = pd.DataFrame(results)
    df = df.sort_values("totalXp", ascending=False)

    st.subheader("📋 Рейтинг участников")
    st.dataframe(df[["username", "totalXp", "streak"]], use_container_width=True)

    st.subheader("📊 Очки (XP)")
    st.bar_chart(df.set_index("username")["totalXp"])

    st.subheader("🔥 Стрик (дни подряд)")
    st.bar_chart(df.set_index("username")["streak"])
else:
    st.warning("Не удалось собрать данные ни по одному user_id.")
