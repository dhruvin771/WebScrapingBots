import json
import os
import re
from dotenv import load_dotenv
import telebot
import validators
from selenium import webdriver

load_dotenv()

BOT_TOKEN = os.getenv("AMAZON_BOT_SCRAPER")
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
            hiRes_values = get_hiRes_values(user_input)
            if(len(hiRes_values) == 0):
                bot.reply_to(message,"No Image Found.")
                return
            media = []
            for image_url in hiRes_values:
                media.append(telebot.types.InputMediaPhoto(image_url))
            bot.send_media_group(message.chat.id, media)
        except Exception as e:
            bot.reply_to(message, f"Error fetching the URL: {e}")
    else:
        bot.reply_to(message, "Please enter a valid link.")

def get_hiRes_values(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 

    driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
      "userAgent": "",
    })

    driver.get(url)

    html_content = driver.page_source

    pattern = r"'colorImages':(.*?)'colorToAsin'"
    match = re.search(pattern, html_content, re.DOTALL)

    hiRes_values = []

    if match:
        extracted_text = match.group(1)
        extracted_text = extracted_text.strip().replace("'", '"').rstrip(',')
        json_data = json.loads(extracted_text)
        
        initial_array = json_data.get('initial', [])
        hiRes_values = [item.get('hiRes', '') for item in initial_array]

    driver.quit()

    return hiRes_values

try:
    bot.infinity_polling()
except Exception as e:
    print(f"Error with bot polling: {e}")
