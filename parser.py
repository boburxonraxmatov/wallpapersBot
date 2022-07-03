from bs4 import BeautifulSoup
import requests
import os
import sqlite3
import re
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('URL')
HOST = os.getenv('HOST')

db = sqlite3.connect('wallpapers.db')
cursor = db.cursor()

# Обход с помощью эмуляции браузера
headers = {
   'Accept-Language': 'ru-RU,ru;q=0.9',
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}


class CategoryParser:
   def __init__(self, url, name, category_id, pages=3):
      self.url = url
      self.name = name
      self.category_id = category_id
      self.pages = pages


   def get_html(self, i):
      try:
         html = requests.get(self.url + f'/page{i}', headers=headers).text
         return html
      except:
         print('Не удалось получить страницу')


   def get_soup(self, i):
      html = self.get_html(i)
      soup = BeautifulSoup(html, 'html.parser')
      return soup


   def get_data(self):

      for i in range(1, self.pages + 1): # 1, 2, 3
         soup =self.get_soup(i)
         images_blocks = soup.find_all('a', class_='wallpapers__link')
         for block in images_blocks:
            image_link = block.find('img', class_='wallpapers__image').get('src')
            print(image_link)
            page_link = HOST + block['href']
            print(page_link)
            page_html = requests.get(page_link, headers=headers).text
            page_soup = BeautifulSoup(page_html, 'html.parser')
            resolution = page_soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
            print(resolution)
            image_link = image_link.replace('300x168', resolution)
            cursor.execute('''
            INSERT OR IGNORE INTO images(image_link, category_id) VALUES (?, ?);
            ''', (image_link, self.category_id))
            db.commit()


def parsing():
   html = requests.get(URL, headers=headers).text
   soup = BeautifulSoup(html, 'html.parser')
   filters = soup.find('ul', class_='filters__list')
   all_filters = filters.find_all('a', class_='filter__link')
   for f in all_filters:
      link = HOST + f.get('href')
      print(link)
      name = f.get_text(strip=True)
      print(name)

      true_name = re.findall(r'[3]*[A-Za-zА-Яа-я]+', name)[0] # название тэга
      print(true_name)

      pages = int(re.findall(r'[0-9][0-9]+', name)[0]) // 15 # выясняем кол-во страниц
      print(pages)

      # Сохранить в базе и вытащить id категории
      cursor.execute(
         '''
         INSERT OR IGNORE INTO categories(category_name) VALUES (?);
         ''', (true_name, )
      )
      db.commit()
      print(f'Парсим категорию: {true_name}')

      cursor.execute('''
      SELECT category_id FROM categories WHERE category_name = ?;
      ''', (true_name, )
      )
      category_id = cursor.fetchone()[0]
      print(category_id, true_name)
      parser = CategoryParser(url=link,
                              name=true_name,
                              category_id=category_id, pages=pages)
      parser.get_data()


parsing()