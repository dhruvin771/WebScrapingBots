import os
import re
from dotenv import load_dotenv
import telebot
import validators
from selenium import webdriver
from bs4 import BeautifulSoup

load_dotenv()

BOT_TOKEN = os.getenv("THREAD_BOT_SCRAPER")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = str(message.from_user.id)
        bot.reply_to(message, f"Hello {message.from_user.first_name}!")
    except telebot.apihelper.ApiException as e:
        print(f"Error sending welcome message: {e}")

@bot.message_handler(func=lambda message: message.content_type == 'text' and not message.text.startswith('/'))
def process_message(message):
    user_input = message.text
    if (validators.url(user_input)):
        try:
            media = get_thread_video(user_input)
            if(media == None):
                bot.reply_to(message,"No Video Found.")
            else :
                bot.send_media_group(message.chat.id, media)
        except Exception as e:
            bot.reply_to(message, f"Error fetching the URL: {e}")
    else:
        bot.reply_to(message, "Please enter a valid link.")

def get_thread_video(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 

    driver = webdriver.Chrome(options=options)

    driver.get(url)

    html_content = driver.page_source

    driver.quit()

    return extract_video_link(html_content)

def extract_video_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    video_element = soup.find('video')

    if video_element:
        src = video_element['src']
        cleaned_src = re.sub(r'&amp;', '&', src)
        return cleaned_src if cleaned_src else None
    else:
        return None

try:
    bot.infinity_polling()
except Exception as e:
    print(f"Error with bot polling: {e}")
