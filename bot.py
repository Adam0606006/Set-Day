import telebot
import config
import db
import handles

bot = telebot.TeleBot(config.TOKEN)
handles.register_handlers(bot)

if __name__ == "__main__":
    db.init_db()
    bot.infinity_polling()