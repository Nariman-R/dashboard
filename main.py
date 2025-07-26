import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Засекаем время начала ---
start_time = time.time()

# --- Настройки браузера ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

def get_stat_value(label_text):
    """Ищет значение по текстовой метке (например, 'Очки опыта')."""
    try:
        label = wait.until(EC.presence_of_element_located((
            By.XPATH, f"//div[normalize-space()='{label_text}']"
        )))
        parent = label.find_element(By.XPATH, "./..")
        h4 = parent.find_element(By.XPATH, ".//h4")
        return h4.text.strip()
    except Exception:
        return ""

def parse_int(val):
    """Преобразует строку в целое число, убирая пробелы и запятые."""
    try:
        return int(val.replace(" ", "").replace(",", ""))
    except:
        return 0

# --- Чтение списка пользователей из файла ---
with open("users.txt", "r", encoding="utf-8") as file:
    usernames = [line.strip() for line in file if line.strip()]

results = []

# --- Сбор данных с профилей ---
for username in usernames:
    url = f"https://www.duolingo.com/profile/{username}"
    print(f"Обработка: {username}")
    try:
        driver.get(url)
        time.sleep(3)
        xp = get_stat_value("Очки опыта")
        streak = get_stat_value("Ударный режим")
        results.append([username, xp, streak])
    except Exception as e:
        print(f"Ошибка для {username}: {e}")
        results.append([username, "", ""])

driver.quit()

# --- Сортировка по "Очки опыта" в убывающем порядке ---
#results.sort(key=lambda row: parse_int(row[1]), reverse=True)

# --- Сохранение в CSV с корректной кодировкой для Excel ---
with open("duolingo_users.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Пользователь", "Очки опыта", "Ударный режим"])
    writer.writerows(results)

# --- Время окончания и вывод ---
end_time = time.time()
elapsed = end_time - start_time
elapsed_str = str(datetime.timedelta(seconds=int(elapsed)))

print(f"Готово. Отсортированные данные сохранены в duolingo_users.csv.")
print(f"Время выполнения скрипта: {elapsed_str}")
