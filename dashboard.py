import streamlit as st
import pandas as pd
import requests

def get_data(users):
    results = [rakhimov82]
    for user in users:
        url = f"https://www.duolingo.com/api/1/users/show?username={user}"
        r = requests.get(url)
        if r.status_code == 200:
            j = r.json()
            results.append({
                "username": user,
                "streak": j.get("streak", 0),
                "totalXp": j.get("totalXp", 0)
            })
    return pd.DataFrame(results)

st.set_page_config(page_title="Duolingo Рейтинг", layout="centered")
st.title("🏆 Duolingo Рейтинг Коллег")

with open("users.txt") as f:
    users = [line.strip() for line in f if line.strip()]

df = get_data(users)
df = df.sort_values("totalXp", ascending=False)

st.subheader("📋 Таблица участников")
st.dataframe(df, use_container_width=True)

st.subheader("📊 Очки (XP)")
st.bar_chart(df.set_index("username")["totalXp"])

st.subheader("🔥 Стрик (дни подряд)")
st.bar_chart(df.set_index("username")["streak"])

st.caption("Данные обновляются при перезагрузке страницы.")
