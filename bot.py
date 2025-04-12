import telebot
import requests


TOKEN = "8070205840:AAFCbPRMd6QjKbw9KQFqg7QnChtWwxwhQUY"
API_URL = "http://localhost:8000/api/1v/generate/"  # или твой прод адрес

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Введи своё полное имя:")
    user_data[message.chat.id] = {}

@bot.message_handler(func=lambda m: m.chat.id in user_data and "full_name" not in user_data[m.chat.id])
def get_full_name(message):
    user_data[message.chat.id]["full_name"] = message.text
    bot.send_message(message.chat.id, "Какую позицию ты ищешь?")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "desired_position" not in user_data[m.chat.id])
def get_position(message):
    user_data[message.chat.id]["desired_position"] = message.text
    bot.send_message(message.chat.id, "Перечисли свои навыки через запятую:")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "skills" not in user_data[m.chat.id])
def get_skills(message):
    user_data[message.chat.id]["skills"] = [s.strip() for s in message.text.split(",")]

    data = user_data[message.chat.id]

    bot.send_message(message.chat.id, "Генерирую резюме...")

    # Запрос к API
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        resume = response.json()
        pdf_url = resume.get("pdf")

        if pdf_url:
            # Отправляем PDF
            file = requests.get(pdf_url)
            bot.send_document(message.chat.id, file.content, visible_file_name="resume.pdf")
        else:
            bot.send_message(message.chat.id, "PDF не найден 😢")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при генерации: {e}")

    # Очищаем данные
    del user_data[message.chat.id]
if __name__ == "__main__":
    bot.polling(none_stop=True)