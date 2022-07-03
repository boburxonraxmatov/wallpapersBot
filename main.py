from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import os
import sqlite3
import random
from keyboards import *
import re

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
   await message.answer('Здравствуйте, здесь вы найдёте обои на любой вкус!')
   await show_categories(message)


async def show_categories(message: Message):
   database = sqlite3.connect('wallpapers.db')
   cursor = database.cursor()
   cursor.execute('''
   SELECT category_name FROM categories;
   ''')
   categories = cursor.fetchall()
   database.close()
   print(categories)
   await message.answer('Выберите категории: ', reply_markup=generate_categories(categories))

@dp.message_handler(content_types=['text'])
async def get_image(message: Message):
   category = message.text
   database = sqlite3.connect('wallpapers.db')
   cursor = database.cursor()

   # 1 запрос с подзапросом
   cursor.execute('''
   SELECT image_link FROM images
   WHERE category_id = (
      SELECT category_id FROM categories WHERE category_name = ?
   );
   ''', (category, ))
   image_links = cursor.fetchall()
   random_index = random.randint(0, len(image_links) - 1)
   random_index_link = image_links[random_index][0] # Вытаскиваем из кортежа

   cursor.execute('''
   SELECT image_id FROM images WHERE image_link = ?
   ''', (random_index_link, ))
   image_id = cursor.fetchone()[0]

   resolution = re.search(r'[0-9]+x[0-9]+', random_index_link)[0]

   caption = f'''Разрешение: {resolution}
Лучшие обои здесь: @@my_wallpapers_PROWEB_bot'''



   # Отправить изображение вы можете не более 10 мб размера
   try:
      await bot.send_photo(chat_id=message.chat.id,
                           photo=random_index_link,
                           caption=caption,
                              reply_markup=generate_download(image_id))
   except Exception as e:

      resize_link = random_index_link.replace(resolution, '1920x1080')
      try:
         await bot.send_photo(chat_id=message.chat.id,
                              photo=resize_link,
                              caption=caption,
                                 reply_markup=generate_download(image_id))
      except:
         await message.answer('Что-то пошло не так, попробуйте снова!!!')



# Функция для реакции на нажатии кнопки
@dp.callback_query_handler(lambda call: 'download' in call.data)
async def download_photo(call: CallbackQuery):
   # 'download_123'
   _, image_id = call.data.split('_')
   image_id = int(image_id)

   database = sqlite3.connect('wallpapers.db')
   cursor = database.cursor()
   cursor.execute('''
   SELECT image_link FROM images WHERE image_id = ?
   ''', (image_id, ))
   image_link = cursor.fetchone()[0]


   database.close()
   try:
      await bot.send_document(chat_id=call.message.chat.id,
                              document=image_link)
   except:
      await bot.send_message(chat_id=call.message.chat.id,
                                text=str(image_link))


# библиотека Pillow
# скачать картинку - на картинку поставить водянной знак с текстом - название вашего бота




executor.start_polling(dp)

