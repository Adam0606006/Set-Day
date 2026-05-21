import pandas as pd
import matplotlib.pyplot as plt

def get_insights(records):
    if not records:
        return "Нет данных."

    df = pd.DataFrame(records)

    mood = round(df["mood"].mean(), 1)
    work = round(df["work_hours"].mean(), 1)
    sleep = round(df["sleep_hours"].mean(), 1)

    sleep_msg = (
        "Сон > 7.5ч улучшает настрой."
        if df[df["sleep_hours"] >= 7.5]["mood"].mean()
        > df[df["sleep_hours"] < 7.5]["mood"].mean()
        else "Сон не влияет."
    )

    work_msg = (
        "Работа > 4ч снижает настрой."
        if df[df["work_hours"] < 4]["mood"].mean()
        > df[df["work_hours"] >= 4]["mood"].mean()
        else "Работа ок."
    )

    return (
        "Среднее:\n"
        f"Настроение: {mood}\n"
        f"Работа: {work}ч\n"
        f"Сон: {sleep}ч\n\n"
        f"{sleep_msg}\n"
        f"{work_msg}"
    )

def create_chart(records, filename):
    if not records:
        return

    df = pd.DataFrame(records)

    plt.figure()

    plt.plot(df["date"], df["mood"], label="Настроение")
    plt.plot(df["date"], df["work_hours"], label="Работа")
    plt.plot(df["date"], df["sleep_hours"], label="Сон")

    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
