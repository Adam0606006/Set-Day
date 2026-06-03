import telebot
import config
import db
import handlers

db.init_db()
db.load_test_data()

bot = telebot.TeleBot(config.TOKEN)

handlers.register_handlers(bot)

if __name__ == "__main__":
    bot.polling()
