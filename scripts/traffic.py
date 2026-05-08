"""
Скрипт сбора статистики просмотров и клонов репозитория через GitHub API.
Запускается автоматически через GitHub Actions раз в день.
Сохраняет накопленную статистику в traffic.csv и создаёт отчёт report.md.
"""
import requests
import csv
import os
from datetime import date

USERNAME = "bugaevskiy"
REPO = "bugaevsky"
TOKEN = os.environ.get("GH_TOKEN")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

url_views = f"https://api.github.com/repos/{USERNAME}/{REPO}/traffic/views"
url_clones = f"https://api.github.com/repos/{USERNAME}/{REPO}/traffic/clones"
url_paths = f"https://api.github.com/repos/{USERNAME}/{REPO}/traffic/popular/paths"
url_referrers = f"https://api.github.com/repos/{USERNAME}/{REPO}/traffic/popular/referrers"

try:
    views_data = requests.get(url_views, headers=headers).json()
    clones_data = requests.get(url_clones, headers=headers).json()
    paths_data = requests.get(url_paths, headers=headers).json()
    referrers_data = requests.get(url_referrers, headers=headers).json()
except Exception as e:
    print(f"Ошибка при запросе к API: {e}")
    exit(1)

today = str(date.today())
total_views = views_data.get("count", 0)
unique_views = views_data.get("uniques", 0)
total_clones = clones_data.get("count", 0)
unique_clones = clones_data.get("uniques", 0)

# Сохраняем накопленную статистику в CSV
csv_file = "traffic.csv"
file_exists = os.path.exists(csv_file)

with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["date", "total_views", "unique_views", "total_clones", "unique_clones"])
    writer.writerow([today, total_views, unique_views, total_clones, unique_clones])

# Создаём отчёт report.md
report_lines = [
    f"📊 **Отчёт за {today}**\n",
    "\n## 👁 Просмотры за 14 дней",
    f"- Всего: **{total_views}**",
    f"- Уникальных: **{unique_views}**\n",
    "\n## 📥 Клоны за 14 дней",
    f"- Всего: **{total_clones}**",
    f"- Уникальных: **{unique_clones}**\n",
]

# Безопасная обработка popular paths
if isinstance(paths_data, list) and paths_data:
    report_lines.append("\n## 🔥 Популярные страницы\n")
    for p in paths_data[:5]:
        report_lines.append(f"- `{p.get('path', '?')}` — {p.get('count', 0)} просмотров")

# Безопасная обработка referrers
if isinstance(referrers_data, list) and referrers_data:
    report_lines.append("\n## 🔗 Откуда приходят\n")
    for r in referrers_data[:5]:
        report_lines.append(f"- {r.get('referrer', '?')} — {r.get('count', 0)} переходов")

report_lines.append(f"\n\n---\n*Данные собираются автоматически через GitHub Actions. Хранятся в traffic.csv*")

with open("report.md", "w", encoding="utf-8") as f:
    f.write("".join(report_lines))

print("Отчёт сохранён в report.md")
