import pandas as pd
import matplotlib.pyplot as plt

def get_insights(records):
    if not records:
        return "Нет данных."

    df = pd.DataFrame(records)

    avg_mood = df["mood"].mean()
    avg_work = df["work_hours"].mean()
    avg_sleep = df["sleep_hours"].mean()

    sleep_good = df[df["sleep_hours"] >= 7.5]["mood"].mean()
    sleep_bad = df[df["sleep_hours"] < 7.5]["mood"].mean()

    if sleep_good > sleep_bad:
        sleep_msg = "Сон > 7.5ч улучшает настрой."
    else:
        sleep_msg = "Сон не влияет."

    work_low = df[df["work_hours"] < 4]["mood"].mean()
    work_high = df[df["work_hours"] >= 4]["mood"].mean()

    if work_low > work_high:
        work_msg = "Работа > 4ч снижает настрой."
    else:
        work_msg = "Работа ок."

    text = "Среднее:\n"
    text += "Настроение: " + str(round(avg_mood, 1)) + "\n"
    text += "Работа: " + str(round(avg_work, 1)) + "ч\n"
    text += "Сон: " + str(round(avg_sleep, 1)) + "ч\n\n"
    text += sleep_msg + "\n"
    text += work_msg

    return text

def create_chart(records, filename):
    df = pd.DataFrame(records)

    if df.empty:
        return None

    plt.figure()
    plt.plot(df["date"], df["mood"], "o-", label="Настроение")
    plt.plot(df["date"], df["work_hours"], "s--", label="Работа")
    plt.plot(df["date"], df["sleep_hours"], "^-", label="Сон")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename
