# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback
import config

token = os.environ['dickfind']
bot = telebot.TeleBot(token)

mongo_client = MongoClient(os.environ['database'])
db = mongo_client.dickfind
users = db.users
chats = db.chats

polls={}
number=0

symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'g', 'k', 'l', 'm', '1', '0', '9', '8', '6', '5', '4', '3', 'u', 'o', 'x', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z']

dickcodes = []
emptycodes = []
golddickcodes = []

def randomgen():
    l = 10
    text = ''
    while len(text) < l:
        x = random.choice(symbols)
        if random.randint(1, 2) == 1:
            x = x.upper()
        text += x
    
    while text in dickcodes or text in emptycodes or text in golddickcodes:
        text = ''
        while len(text) < l:
            x = random.choice(symbols)
            if random.randint(1, 2) == 1:
                x = x.upper()
            text += x
    return text

while len(dickcodes) < 100:
    key = randomgen()
    dickcodes.append(key)
    
while len(emptycodes) < 100:
    key = randomgen()
    emptycodes.append(key)
    
while len(golddickcodes) < 100:
    key = randomgen()
    golddickcodes.append(key)


try:
    pass

except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
    bot.send_message(441399484, traceback.format_exc())

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)   
    
@bot.message_handler(commands=['dick'])
def dd(m):
    #config.about(m, bot)
    if m.chat.id < 0:
        if chats.find_one({'id':m.chat.id}) == None:
            t = 1594395747
            chats.insert_one({
                'id':m.chat.id,
                'title':m.chat.title
            }
            )
            if time.time() - t <= 250400:
                bot.send_message(m.chat.id, 'У бота теперь есть статистика найденных членов - найти её можно по команде /dickstat!')
    global number
    text='Угадайте, в какой коробке хуй.'
    kb=types.InlineKeyboardMarkup(3)
    buttons1=[]
    buttons2=[]
    buttons3=[]
    amount=random.randint(1,8)
    i=0
    dicks=[]
    golddicks=[]
    while i<amount:
        x=random.randint(1,9)
        while x in dicks:
            x=random.randint(1,9)
        dicks.append(x)
        i+=1
    i=1
    while i<=9:
        randoms=random.randint(1,10000000)
        if i in dicks:
            if random.randint(1,100)!=1:
                callb=random.choice(dickcodes)
            else:
                callb=random.choice(golddickcodes)
                golddicks.append(i)
        else:
            callb=random.choice(emptycodes)
        
        if i<=3:
            buttons1.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        elif i<=6:
            buttons2.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        elif i<=9:
            buttons3.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        i+=1
    kb.add(*buttons1)
    kb.add(*buttons2)
    kb.add(*buttons3)
    kb.add(types.InlineKeyboardButton(text='Окончить игру', callback_data='endgame '+str(number)))
    polls.update({number:{
        'users':{},
        'dicks':dicks,
        'kb':kb,
        'golddicks':golddicks
        
    }}
                )
    bot.send_message(m.chat.id, text, reply_markup=kb)
    number+=1
 

@bot.message_handler(commands=['dickstat'])
def dickstats(m):
    user = createuser(m.from_user)
    alls = user['penis']+user['goldpenis']+user['null']
    if alls > 0:
        penis = round((user['penis']/alls)*100, 2)
        goldpenis = round((user['goldpenis']/alls)*100, 2)
        null = round((user['null']/alls)*100, 2)
    else:
        penis = 0
        goldpenis = 0
        null = 0
    text = 'Статистика пользователя '+user['name']+':\n\n'
    text += 'Найдено членов: '+str(user['penis'])+'🍆 ('+str(penis)+'%)\n'
    text += 'Найдено ЗОЛОТЫХ членов: '+str(user['goldpenis'])+'🍌 ('+str(goldpenis)+'%)\n'
    text += 'Открыто пустых коробок: '+str(user['null'])+'💨 ('+str(null)+'%)'
    bot.send_message(m.chat.id, text, reply_to_message_id = m.message_id)
    

@bot.callback_query_handler(func=lambda call:True)
def inline(call):
  try:
    user2 = createuser(call.from_user)
    user=call.from_user
    try:
        game=polls[int(call.data.split(' ')[1])]
    except:
        game=None
    if game!=None:
        if user.id not in game['users'] and call.data!='xyi':
            golddick=False
            if call.data.split()[0] in dickcodes:
                dick=True
                text='🍆|Ура! Вы выбрали ящик с членом!'
                users.update_one({'id':call.from_user.id},{'$inc':{'penis':1}})
                bot.answer_callback_query(call.id, text, show_alert=True)
            elif call.data.split()[0] in golddickcodes:
                dick = True
                golddick=True
                text='🍌|Ура! Вы нашли золотой пенис!'
                users.update_one({'id':call.from_user.id},{'$inc':{'goldpenis':1}})
            else:
                dick=False
                bot.answer_callback_query(call.id, '💨|О нет! Вы выбрали ящик без члена!', show_alert=True)
                users.update_one({'id':call.from_user.id},{'$inc':{'null':1}})
            
            game['users'].update({user.id:{'name':call.from_user.first_name,
                                          'dick':dick,
                                          'golddick':golddick}})
            kb=types.InlineKeyboardMarkup(3)
            
            medit(editmsg(game), call.message.chat.id, call.message.message_id, reply_markup=game['kb'])
        
        elif 'endgame' not in call.data:
            bot.answer_callback_query(call.id, 'Вы уже походили!')
        
    if 'endgame' in call.data:
        kb2=types.InlineKeyboardMarkup()
        buttons1=[]
        buttons2=[]
        buttons3=[]
        i=1
        while i<=9:
            if i in game['dicks']:
                emoj='🍆'
                if i in game['golddicks']:
                    emoj='🍌'
            else:
                emoj='💨'
            if i<=3:
                buttons1.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            elif i<=6:
                buttons2.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            elif i<=9:
                buttons3.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            i+=1
        kb2.add(*buttons1)
        kb2.add(*buttons2)
        kb2.add(*buttons3)
        result=editmsg(game, True)
        medit('Игра окончена юзером '+call.from_user.first_name+'! Результаты:\n'+result, call.message.chat.id, call.message.message_id, reply_markup=kb2)

  except Exception as e:
    bot.send_message(441399484, traceback.format_exc())
    
def editmsg(game, end=False):
    if end==False:
        text='Угадайте, в какой коробке хуй.\n\n'
    else:
        text=''
    for ids in game['users']:
        if game['users'][ids]['golddick']==True:
            text+=game['users'][ids]['name']+': 🍌нашёл(ла) ЗОЛОТОЙ член!\n'
        
        elif game['users'][ids]['dick']==True:
            text+=game['users'][ids]['name']+': 🍆нашёл(ла) член\n'
        else:
            text+=game['users'][ids]['name']+': 💨открыл(а) пустую коробку\n'
    return text

def createuser(user):
    user2 = users.find_one({'id':user.id})
    if user2 == None:
        users.insert_one({
            'id':user.id,
            'name':user.first_name,
            'penis':0,
            'goldpenis':0,
            'null':0
        })
        user2 = users.find_one({'id':user.id})
    return user2


@bot.message_handler()
def allmssss(m):
    if m.chat.id < 0:
        if chats.find_one({'id':m.chat.id}) == None:
            t = 1594395747
            chats.insert_one({
                'id':m.chat.id,
                'title':m.chat.title
            }
            )
            if time.time() - t <= 250400:
                bot.send_message(m.chat.id, 'У бота теперь есть статистика найденных членов - найти её можно по команде /dickstat!')
        
    #config.about(m, bot)
    
    
    
