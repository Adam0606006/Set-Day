from datetime import date
import db
import keyboards
import stats_logic

state = {}

def is_step(uid, step_name):
    if uid not in state:
        return False
    return state[uid].get("step") == step_name

def register_handlers(bot):

    def get_stats_text(recs, days):
        if not recs:
            return "Мало данных!"
        cnt = len(recs)
        sm = 0
        sw = 0
        ss = 0
        for r in recs:
            sm += r.get("mood", 0)
            sw += r.get("work_hours", 0)
            ss += r.get("sleep_hours", 0)
        am = sm / cnt
        aw = sw / cnt
        a_s = ss / cnt
        out = "Среднее (" + str(days) + " дн):\n"
        out += "Настроение: " + str(round(am, 1)) + "\n"
        out += "Работа: " + str(round(aw, 1)) + "ч\n"
        out += "Сон: " + str(round(a_s, 1)) + "ч"
        return out

    def save_input(msg, key, next_step, prompt, kb):
        uid = msg.chat.id
        try:
            clean = msg.text.replace(",", ".")
            num = float(clean)
        except ValueError:
            return
        state[uid][key] = num
        state[uid]["step"] = next_step
        bot.send_message(uid, prompt, reply_markup=kb)

    def finish_record(msg, comment):
        uid = msg.chat.id
        d = state[uid]
        today = date.today().isoformat()
        m_val = d.get("mood")
        w_val = d.get("work")
        s_val = d.get("sleep")
        db.add_record(uid, today, m_val, w_val, s_val, comment)
        del state[uid]
        kb = keyboards.main()
        bot.send_message(uid, "Сохранено.", reply_markup=kb)

    @bot.message_handler(commands=["start"])
    def cmd_start(msg):
        kb = keyboards.main()
        bot.send_message(msg.chat.id, "Меню:", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "➕ Записать день")
    def cmd_record(msg):
        uid = msg.chat.id
        has = db.has_today_record(uid)
        if has:
            kb = keyboards.main()
            bot.send_message(uid, "Уже есть запись.", reply_markup=kb)
            return
        state[uid] = {"step": "mood"}
        kb = keyboards.mood()
        bot.send_message(uid, "Оцени свое настроение сегодня от 1 до 5, где 1 — ужасно, 5 — отлично.", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "📊 Статистика")
    def cmd_stats(msg):
        kb = keyboards.stats()
        bot.send_message(msg.chat.id, "Выбери:", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "Назад")
    def cmd_back(msg):
        kb = keyboards.main()
        bot.send_message(msg.chat.id, "Меню:", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "📜 История")
    def cmd_history(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)
        if not recs:
            kb = keyboards.main()
            bot.send_message(uid, "Пусто.", reply_markup=kb)
            return
        out = "📜 История:\n"
        for r in recs[-5:]:
            d = r.get("date")
            m_val = r.get("mood")
            w_val = r.get("work_hours")
            s_val = r.get("sleep_hours")
            out += str(d) + " | "
            out += str(m_val) + " | "
            out += str(w_val) + "ч | "
            out += str(s_val) + "ч\n"
        kb = keyboards.main()
        bot.send_message(uid, out, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "🧹 Очистить данные")
    def cmd_clear(msg):
        kb = keyboards.clear()
        bot.send_message(msg.chat.id, "Удалить всё?", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "👩‍💻 Помощь")
    def cmd_help(msg):
        txt = "➕ Записать день\n"
        txt += "📊 Статистика\n"
        txt += "📜 История\n"
        txt += "🧹 Очистить данные"
        bot.send_message(msg.chat.id, txt)

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "mood"))
    def step_mood(msg):
        first_char = msg.text[0]
        try:
            val = int(first_char)
        except ValueError:
            return
        
        if 1 <= val <= 5:
            uid = msg.chat.id
            state[uid]["mood"] = val
            state[uid]["step"] = "work"
            kb = keyboards.work()
            bot.send_message(uid, "Сколько часов ты потратил на полезную работу/учебу?", reply_markup=kb)

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "work"))
    def step_work(msg):
        save_input(msg, "work", "sleep", "Сколько часов ты спал?", keyboards.sleep())

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "work_in"))
    def step_work_in(msg):
        save_input(msg, "work", "sleep", "Сколько часов ты спал?", keyboards.sleep())

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "sleep"))
    def step_sleep(msg):
        save_input(msg, "sleep", "comment", "Хочешь добавить комментарий?", keyboards.comment())

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "sleep_in"))
    def step_sleep_in(msg):
        save_input(msg, "sleep", "comment", "Хочешь добавить комментарий?", keyboards.comment())

    @bot.message_handler(func=lambda m: is_step(m.chat.id, "comment"))
    def step_comment(msg):
        finish_record(msg, msg.text)

    @bot.message_handler(func=lambda m: m.text == "Пропустить")
    def step_skip(msg):
        uid = msg.chat.id
        if is_step(uid, "comment"):
            finish_record(msg, "")

    @bot.message_handler(func=lambda m: m.text == "Другое")
    def step_other(msg):
        uid = msg.chat.id
        if uid not in state:
            return
        cur = state[uid].get("step")
        if cur == "work":
            state[uid]["step"] = "work_in"
        elif cur == "sleep":
            state[uid]["step"] = "sleep_in"
        bot.send_message(uid, "Пиши число:")

    @bot.message_handler(func=lambda m: m.text == "За неделю")
    def stat_week(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 7)
        text = get_stats_text(recs, 7)
        kb = keyboards.stats()
        bot.send_message(uid, text, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "За месяц")
    def stat_month(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 30)
        text = get_stats_text(recs, 30)
        kb = keyboards.stats()
        bot.send_message(uid, text, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "Мои инсайты")
    def stat_insight(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)
        if not recs:
            kb = keyboards.stats()
            bot.send_message(uid, "Мало данных!", reply_markup=kb)
            return
        kb = keyboards.stats()
        txt = stats_logic.get_insights(recs)
        bot.send_message(uid, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "График")
    def stat_chart(msg):
        uid = msg.chat.id
        recs = db.get_records(uid, 365)
        if not recs:
            kb = keyboards.stats()
            bot.send_message(uid, "Мало данных!", reply_markup=kb)
            return
        fname = "chart.png"
        stats_logic.create_chart(recs, fname)
        with open(fname, "rb") as f:
            bot.send_photo(uid, f)
        kb = keyboards.stats()
        bot.send_message(uid, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "Да")
    def clear_yes(msg):
        uid = msg.chat.id
        db.clear_data(uid)
        kb = keyboards.main()
        bot.send_message(uid, "Удалено.", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "Нет")
    def clear_no(msg):
        kb = keyboards.main()
        bot.send_message(msg.chat.id, "Отмена", reply_markup=kb)
