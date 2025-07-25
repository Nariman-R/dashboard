import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег")

# Загрузка списка пользователей
try:
    with open("users.txt") as f:
        users = [line.strip() for line in f if line.strip()]
except Exception as e:
    st.error(f"Ошибка при чтении users.txt: {e}")
    users = []

if not users:
    st.warning("Список пользователей пуст. Добавьте логины в users.txt.")
else:
    st.subheader("📥 Сбор данных с Duolingo...")
    results = []

    for user in users:
        url = f"https://www.duolingo.com/api/1/users/show?username={user}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                j = r.json()
                results.append({
                    "username": user,
                    "streak": j.get("streak", 0),
                    "totalXp": j.get("totalXp", 0)
                })
                st.success(f"✅ {user} загружен")
            else:
                st.warning(f"⚠️ {user} — ошибка {r.status_code}")
        except Exception as e:
            st.error(f"❌ {user} — сбой запроса: {e}")

    # Преобразуем в DataFrame
    df = pd.DataFrame(results)

    if not df.empty and "totalXp" in df.columns:
        df = df.sort_values("totalXp", ascending=False)
        
        st.subheader("📋 Рейтинг участников")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Очки (XP)")
        st.bar_chart(df.set_index("username")["totalXp"])

        st.subheader("🔥 Стрик (дни подряд)")
        st.bar_chart(df.set_index("username")["streak"])

        st.caption("Данные обновляются при каждом открытии страницы.")
    else:
        st.warning("Не удалось получить данные ни по одному пользователю.")
