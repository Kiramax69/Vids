import os
import telebot
from moviepy.editor import ImageSequenceClip
from datetime import datetime

# Инициализация бота
API_TOKEN = '6332761306:AAHfCNJirktYQjb15p4TzjprXfB_VZ-d5PY'
bot = telebot.TeleBot(API_TOKEN)

# Папка для хранения изображений
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Словарь для временного хранения изображений пользователей
user_images = {}

# Функция, которая объединяет фотографии в видео
def create_video(images, user_id):
    # Создание видео
    video_path = os.path.join(IMAGES_DIR, f'{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
    clip = ImageSequenceClip(images, fps=1)  # 1 кадр в секунду
    clip.write_videofile(video_path, codec='libx264')
    return video_path

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне несколько фотографий, и я сделаю из них видео.")

# Обработчик для фотографий
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    # Скачивание фотографии
    file_info = bot.get_file(message.photo[-1].file_id)
    file = bot.download_file(file_info.file_path)

    # Сохранение фотографии
    image_path = os.path.join(IMAGES_DIR, f'{user_id}_{len(user_images[user_id])}.jpg')
    with open(image_path, 'wb') as f:
        f.write(file)

    user_images[user_id].append(image_path)
    bot.send_message(message.chat.id, "Фото добавлено! Отправь ещё фото или введи команду /create_video для создания видео.")

# Команда для создания видео
@bot.message_handler(commands=['create_video'])
def create_video_command(message):
    user_id = message.from_user.id

    if user_id not in user_images or len(user_images[user_id]) < 2:
        bot.send_message(message.chat.id, "Недостаточно фотографий для создания видео. Пожалуйста, отправь как минимум 2 фотографии.")
        return

    try:
        # Создание видео
        video_path = create_video(user_images[user_id], user_id)

        # Отправка видео пользователю
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video)

        # Очистка изображений пользователя после создания видео
        user_images[user_id].clear()
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

# Запуск бота
bot.polling(none_stop=True)
