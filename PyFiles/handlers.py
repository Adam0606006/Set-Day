from datetime import date
from enum import Enum, auto

import db
import keyboards
import stats_logic

class State(Enum):
    MOOD = auto()
    WORK = auto()
    SLEEP = auto()
    COMMENT = auto()

fsm = {}

def set_state(uid, state):
    fsm[uid] = {"state": state}

def get_state(uid):
    return fsm.get(uid, {}).get("state")

def set_data(uid, key, value):
    fsm[uid][key] = value

def clear_state(uid):
    return fsm.pop(uid, {})

def send(bot, uid, text, kb=None):
    bot.send_message(uid, text, reply_markup=kb)

def to_float(text):
    try:
        return float(text.replace(",", "."))
    except:
        return None

def finish(bot, uid, comment=""):
    data = clear_state(uid)

    db.add_record(
        uid,
        date.today().isoformat(),
        data.get("mood"),
        data.get("work"),
        data.get("sleep"),
        comment
    )

    send(bot, uid, "Сохранено.", keyboards.main())

def register_handlers(bot):

    @bot.message_handler(commands=["start", "help"])
    def start(msg):
        send(bot, msg.chat.id, "Меню:", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "👩‍💻 Помощь")
    def help_handler(msg):
        send(
            bot,
            msg.chat.id,
            "/start - главное меню\n"
            "/help - помощь\n"
            "/record - записать день\n"
            "/stats - статистика\n"
            "/history - история\n"
            "/insights - инсайты\n"
            "/chart - график\n"
            "/clear - очистить данные\n\n"
        )

    @bot.message_handler(commands=["record"])
    @bot.message_handler(func=lambda m: m.text == "➕ Записать день")
    def record(msg):
        uid = msg.chat.id

        if db.has_today_record(uid):
            return send(bot, uid, "Уже есть запись.", keyboards.main())

        set_state(uid, State.MOOD)

        send(bot, uid, "Настроение (1-5):", keyboards.mood())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.MOOD)
    def mood(msg):
        uid = msg.chat.id

        if not msg.text:
            return

        value = msg.text[0]

        if not value.isdigit():
            return

        mood = int(value)

        if mood not in range(1, 6):
            return

        set_data(uid, "mood", mood)
        set_data(uid, "state", State.WORK)

        send(bot, uid, "Часов работы?", keyboards.work())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.WORK)
    def work(msg):
        uid = msg.chat.id

        value = to_float(msg.text)

        if value is None:
            return

        set_data(uid, "work", value)
        set_data(uid, "state", State.SLEEP)

        send(bot, uid, "Часов сна?", keyboards.sleep())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.SLEEP)
    def sleep(msg):
        uid = msg.chat.id

        value = to_float(msg.text)

        if value is None:
            return

        set_data(uid, "sleep", value)
        set_data(uid, "state", State.COMMENT)

        send(bot, uid, "Комментарий?", keyboards.comment())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.COMMENT)
    def comment(msg):
        text = "" if msg.text == "Пропустить" else msg.text
        finish(bot, msg.chat.id, text)

    @bot.message_handler(commands=["stats"])
    @bot.message_handler(func=lambda m: m.text == "📊 Статистика")
    def stats(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 3650)

        if not recs:
            return send(bot, uid, "Нет данных.", keyboards.main())

        n = len(recs)

        text = (
            "Среднее:\n"
            f"Настроение: {sum(r['mood'] for r in recs)/n:.1f}\n"
            f"Работа: {sum(r['work_hours'] for r in recs)/n:.1f}ч\n"
            f"Сон: {sum(r['sleep_hours'] for r in recs)/n:.1f}ч"
        )

        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["history"])
    @bot.message_handler(func=lambda m: m.text == "📜 История")
    def history(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)

        if not recs:
            return send(bot, uid, "История пуста.", keyboards.main())

        text = "📜 История:\n"

        for r in recs[-5:]:
            text += (
                f"{r['date']} | "
                f"{r['mood']} | "
                f"{r['work_hours']}ч | "
                f"{r['sleep_hours']}ч\n"
            )

        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["insights"])
    @bot.message_handler(func=lambda m: m.text == "🔍 Мои инсайты")
    def insights(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)

        text = "Мало данных!" if not recs else stats_logic.get_insights(recs)

        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["chart"])
    @bot.message_handler(func=lambda m: m.text == "📉 График")
    def chart(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)

        if not recs:
            return send(bot, uid, "Мало данных!", keyboards.main())

        filename = f"chart_{uid}.png"

        stats_logic.create_chart(recs, filename)

        with open(filename, "rb") as file:
            bot.send_photo(uid, file)

        send(bot, uid, "Готово.", keyboards.main())

    @bot.message_handler(commands=["clear"])
    @bot.message_handler(func=lambda m: m.text == "🧹 Очистить данные")
    def clear(msg):
        send(bot, msg.chat.id, "Удалить всё?", keyboards.clear())

    @bot.message_handler(func=lambda m: m.text == "Да")
    def clear_yes(msg):
        db.clear_data(msg.chat.id)
        send(bot, msg.chat.id, "Удалено.", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "Нет")
    def clear_no(msg):
        send(bot, msg.chat.id, "Отмена.", keyboards.main())
