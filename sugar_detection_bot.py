import requests
import json
import io
from PIL import Image
import pytesseract
import re
import collections
from collections import Counter
import pandas as pd
import numpy as np
import telebot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


URL = 'https://api.telegram.org/<YOUR TOKEN>'

def get_updates(): 
	url = URL + 'getUpdates'
	r = requests.get(url)
	return r.json()

def get_file_path(file_id):
	file_path = URL + 'getFile?file_id=' + file_id
	r = requests.get(file_path)

	return r.json()

def get_url(path):
	url = 'https://api.telegram.org/file/<YOUR TOKEN>' + path
	return url


def upload_image(url):

	r = requests.get(url)
	aux_im = Image.open(io.BytesIO(r.content))

	text = pytesseract.image_to_string(aux_im)
	return text

def cleanString(string):

    cleanedString = []
    s = re.sub(r'[^a-zA-Z0-9\s]', '', string)
    s = re.sub('\s+',' ', s)
    s = s.lower()
    tokens = [token for token in s.split(" ") if token != ""]
    review = ' '.join(tokens)
    cleanedString.append(review)

    return cleanedString

def countWords(string):
    ngrams_all = []

    for word in string:
        tokens = word.split()
        #print(tokens)
    cnt_ngram = Counter()
    for word in tokens:
        cnt_ngram[word] += 1

    df = pd.DataFrame.from_dict(cnt_ngram, orient='index').reset_index()
    df = df.rename(columns={'index':'words', 0:'count'})
    #df = df.sort_values(by='count', ascending=False)
    return df

def printSugar(string):
    count = countWords(string)
    count = count.set_index('words').T.to_dict(orient='index')
    new_dict = count['count']
    for key in new_dict:

        if key in ['sugar', 'aspaprtame', '950', '951', '952', '953', '954', 'acesulfame', 'saccharin', 'cyclamate', 'starch', 'isolmat', 'artificial', 'syrup']:
            return True

TOKEN = 'YOUR TOKEN'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def text_handler(message):
	chat_id = message.chat.id
	bot.send_message(chat_id, "Waaiiiit, please... I'm thinking.")


	r = get_updates()
	file_id = message.photo[0].file_id
	# file_id = r['result'][-1]['message']['photo'][-1]['file_id']
	file_path = get_file_path(file_id)
	path = file_path['result']['file_path']
	url = get_url(path)
	txt = upload_image(url)
	clean_txt = cleanString(txt)
	result = printSugar(clean_txt)
	#chat_id = r['result'][-1]['message']['chat']['id']
	

	if result:
		bot.send_message(chat_id, "Sugar is here")
	else:
		bot.send_message(chat_id, "No sugar")

bot.polling()
