import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег (через user_id API)")

# Загрузка users.csv
try:
    df_users = pd.read_csv("users.csv")
    if "user_id" not in df_users.columns or "username" not in df_users.columns:
        st.error("CSV должен содержать столбцы: user_id, username")
        st.stop()
except Exception as e:
    st.error(f"Не удалось загрузить users.csv: {e}")
    st.stop()

results = []
st.subheader("🔍 Сбор данных с API...")
progress = st.progress(0)
step = 1 / len(df_users)

for i, row in df_users.iterrows():
    user_id = row["user_id"]
    username = row["username"]
    url = f"https://www.duolingo.com/users/{user_id}"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.warning(f"⚠️ {username}: HTTP {response.status_code}")
            continue

        data = response.json()

        result = {
            "username": username,
            "totalXp": data.get("totalXp", 0),
            "streak": data.get("site_streak", 0)
        }
        results.append(result)
        st.success(f"✅ {username}: {result['totalXp']} XP, 🔥 {result['streak']} дней")
    except Exception as e:
        st.warning(f"⚠️ {username}: ошибка {e}")
    
    progress.progress((i + 1) * step)

# Отображение результатов
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
    st.warning("Не удалось собрать данные ни по одному участнику.")
