from datetime import date
import db
import keyboards
import stats_logic

users = {}

def register_handlers(bot):

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        chat_id = message.chat.id
        text = message.text
        
        if text == '/start' or text == 'Назад':
            bot.send_message(chat_id, 'Меню:', reply_markup=keyboards.main())

        elif text == '➕ Записать день':
            if db.has_today_record(chat_id):
                bot.send_message(chat_id, 'Уже есть.', reply_markup=keyboards.main())
                return
            users[chat_id] = {'step': 'mood'}
            bot.send_message(chat_id, 'Настроение (1-5):', reply_markup=keyboards.mood())

        elif text == '📊 Статистика':
            bot.send_message(chat_id, 'Выбери:', reply_markup=keyboards.stats())

        elif text == '📜 История':
            recs = db.get_records(chat_id, 365)
            if not recs:
                bot.send_message(chat_id, 'Пусто.', reply_markup=keyboards.main())
                return
            msg = 'История:\n'
            for r in recs[-5:]:
                msg += f"{r['date']} | {r['mood']} | {r['work_hours']}ч | {r['sleep_hours']}ч\n"
            bot.send_message(chat_id, msg, reply_markup=keyboards.main())

        elif text == '🧹 Очистить данные':
            kb = keyboards.clear()
            bot.send_message(chat_id, 'Удалить всё?', reply_markup=kb)

        elif text == '👩‍💻 Помощь':
            msg = '/start - меню\n'
            msg += 'Записать день - ввод\n'
            msg += 'Статистика - отчет\n'
            msg += 'История - записи\n'
            msg += 'Очистить - удалить'
            bot.send_message(chat_id, msg)


        elif chat_id in users:
            step = users[chat_id]['step']

            if step == 'mood':
                try:
                    val = int(text[0])
                    if 1 <= val <= 5:
                        users[chat_id]['mood'] = val
                        users[chat_id]['step'] = 'work'
                        bot.send_message(chat_id, 'Часов работы:', reply_markup=keyboards.work())
                except:
                    pass

            elif step == 'work' or step == 'work_in':
                try:
                    hours = float(text.replace(',', '.'))
                    users[chat_id]['work'] = hours
                    users[chat_id]['step'] = 'sleep'
                    bot.send_message(chat_id, 'Часов сна:', reply_markup=keyboards.sleep())
                except:
                    pass

            elif step == 'sleep' or step == 'sleep_in':
                try:
                    hours = float(text.replace(',', '.'))
                    users[chat_id]['sleep'] = hours
                    users[chat_id]['step'] = 'comment'
                    bot.send_message(chat_id, 'Комментарий?', reply_markup=keyboards.comment())
                except:
                    pass

            elif step == 'comment':
                data = users[chat_id]
                db.add_record(chat_id, date.today().isoformat(), data['mood'], data['work'], data['sleep'], text)
                del users[chat_id]
                bot.send_message(chat_id, 'Сохранено.', reply_markup=keyboards.main())

        elif text == 'Другое':
            if chat_id in users:
                if users[chat_id]['step'] == 'work':
                    users[chat_id]['step'] = 'work_in'
                elif users[chat_id]['step'] == 'sleep':
                    users[chat_id]['step'] = 'sleep_in'
                bot.send_message(chat_id, 'Пиши число:')

        elif text == 'Пропустить':
            if chat_id in users and users[chat_id]['step'] == 'comment':
                data = users[chat_id]
                db.add_record(chat_id, date.today().isoformat(), data['mood'], data['work'], data['sleep'], '')
                del users[chat_id]
                bot.send_message(chat_id, 'Сохранено.', reply_markup=keyboards.main())

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        chat_id = call.message.chat.id
        data = call.data

        if data == 'st_7':
            recs = db.get_records(chat_id, 7)
            if not recs:
                bot.answer_callback_query(call.id, 'Нет')
                return
            cnt = len(recs)
            m = sum(r['mood'] for r in recs) / cnt
            w = sum(r['work_hours'] for r in recs) / cnt
            s = sum(r['sleep_hours'] for r in recs) / cnt
            msg = f'За неделю:\nНастр: {m:.1f}\nРаб: {w:.1f}ч\nСон: {s:.1f}ч'
            bot.send_message(chat_id, msg, reply_markup=keyboards.stats())

        elif data == 'st_30':
            recs = db.get_records(chat_id, 30)
            if not recs:
                bot.answer_callback_query(call.id, 'Нет')
                return
            cnt = len(recs)
            m = sum(r['mood'] for r in recs) / cnt
            w = sum(r['work_hours'] for r in recs) / cnt
            s = sum(r['sleep_hours'] for r in recs) / cnt
            msg = f'За месяц:\nНастр: {m:.1f}\nРаб: {w:.1f}ч\nСон: {s:.1f}ч'
            bot.send_message(chat_id, msg, reply_markup=keyboards.stats())

        elif data == 'st_ins':
            recs = db.get_records(chat_id, 365)
            if not recs:
                bot.answer_callback_query(call.id, 'Нет')
                return
            bot.send_message(chat_id, stats_logic.get_insights(recs), reply_markup=keyboards.stats())

        elif data == 'st_chart':
            recs = db.get_records(chat_id, 365)
            if not recs:
                bot.answer_callback_query(call.id, 'Нет')
                return
            fname = 'chart.png'
            stats_logic.create_chart(recs, fname)
            with open(fname, 'rb') as f:
                bot.send_photo(chat_id, f, caption='График')
            bot.send_message(chat_id, 'Выбери:', reply_markup=keyboards.stats())

        elif data == 'cl_y':
            db.clear_data(chat_id)
            bot.send_message(chat_id, 'Удалено.', reply_markup=keyboards.main())

        elif data == 'cl_n':
            bot.send_message(chat_id, 'Отмена', reply_markup=keyboards.main())

        bot.answer_callback_query(call.id)
