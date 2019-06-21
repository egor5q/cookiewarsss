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

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.chatpets
users=db.users
chats=db.chats
lost=db.lost

if lost.find_one({})==None:
    lost.insert_one({'amount':0})

botname='Chatpetsbot'

@bot.message_handler(commands=['growpet'])
def grow(m):
    animal=chats.find_one({'id':m.chat.id})
    if animal==None:
        chats.insert_one(createpet(m.chat.id))
        bot.send_message(m.chat.id, 'Поздравляю! Вы завели лошадь! О том, как за ней ухаживать, можно прочитать в /help.')


@bot.message_handler(commands=['help'])
def help(m):
    no=0
    if m.text[6]=='@' and m.text[6:len(botname)+6]!=botname:
        no=1
    if no==0:
        text=''
        text+='Чатовые питомцы питаются активностью юзеров. Чем больше вы общаетесь в чате, тем счастливее будет питомец! '
        text+='Если долго не общаться, питомец начинает голодать и терять жизни. Назвать питомца можно командой /help!'
        bot.send_message(m.chat.id, text)
     
    
@bot.message_handler(commands=['petstats'])
def petstats(m):
    animal=chats.find_one({'id':m.chat.id})
    if animal!=None:
        text=''
        text+='Имя: '+animal['name']+'\n'
        text+='Уровень: '+str(animal['lvl'])+'\n'
        text+='Опыт: '+str(animal['exp'])+'/'+str(nextlvl(animal))+'\n'
        text+='Здоровье: '+str(animal['hp'])+'/'+str(animal['maxhp'])+'\n'
        text+='Сытость: '+str(animal['hunger'])+'/'+str(animal['maxhunger'])+'\n'
        bot.send_message(m.chat.id, text)
    
      
        
@bot.message_handler({})
def messages(m):
    animal=chats.find_one({'id':m.chat.id})
    if animal!=None:
        if m.from_user.id not in animal['lastminutefeed']:
            chats.update_one({'id':m.chat.id},{'$push':{'lastminutefeed':m.from_user.id}})
            
        
        
def createpet(id, typee='horse', name='Без имени'):
    return {
        'id':id,
        'type':typee,
        'name':name,
        'lvl':1,
        'exp':0,
        'hp':100,
        'maxhp':100,
        'lastminutefeed':[],         # Список юзеров, которые проявляли актив в последнюю минуту
        'hunger':100,
        'maxhunger':100,
        'stats':{}                   # Статы игроков: кто сколько кормит лошадь итд
    }
        
        

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,                       
                                 parse_mode=parse_mode)   




def nextlvl(pet):
    needexp=int(20+pet['lvl']+(pet['lvl']*(pet['lvl']/3)))
    return needexp

def check1():
    for ids in chats.find({}):
        if len(ids['lastminutefeed'])>0:
            chats.update_one({'id':ids['id']},{'$inc':{'hunger':len(ids['lastminutefeed'])}})
            chat=chats.find_one({'id':ids['id']})
            if chat['hunger']>chat['maxhunger']:
                chats.update_one({'id':ids['id']},{'$set':{'hunger':ids['maxhunger']}})
            chats.update_one({'id':ids['id']},{'$set':{'lastminutefeed':[]}})
                
                
    for ids in chats.find({}):
        if ids['hunger']>=100:
            multipler=1+(random.randint(-100, 100)/100)
            exp=int(ids['lvl']+ids['lvl']*(multipler+random.randint(0,3)))
            chats.update_one({'id':ids['id']},{'$inc':{'exp':exp}})
            pet=chats.find_one({'id':ids['id']})
            if pet['exp']>=nextlvl(pet):
                chats.update_one({'id':ids['id']},{'$inc':{'lvl':1}})
                chats.update_one({'id':ids['id']},{'$inc':{'maxhunger':15}})
                bot.send_message(ids['id'], 'Уровень вашей лошади повышен! Максимальный запас сытости увеличен на 15!')
    
    
    t=threading.Timer(60, check1)
    t.start()
            
        

def check10():
    chats.update_many({},{'$inc':{'hunger':-random.randint(1,3)}})
    for ids in chats.find({}):
        if ids['hunger']<0:
            chats.update_one({'id':ids['id']},{'$set':{'hunger':0}})
    for ids in chats.find({}):
        if ids['hunger']<=0:
            bot.send_message(ids['id'], 'Ваша лошадь СИЛЬНО голодает! Осталось '+str(ids['hunger'])+' сытости! СРОЧНО нужен актив в чат!')
            chats.update_one({'id':ids['id']},{'$inc':{'hp':-random.randint(3,5)}})
        elif ids['hunger']<=30:
            bot.send_message(ids['id'], 'Ваша лошадь голодает! Осталось всего '+str(ids['hunger'])+' сытости! Срочно нужен актив в чат!')
            chats.update_one({'id':ids['id']},{'$inc':{'hp':-random.randint(1,2)}})
        elif ids['hunger']>=75:
            if ids['hp']<ids['maxhp']:
                chats.update_one({'id':ids['id']},{'$inc':{'hp':random.randint(1,3)}})
                chat=chats.find_one({'id':ids['id']})
                if chat['hp']>chat['maxhp']:
                    chats.update_one({'id':ids['id']},{'$set':{'hp':ids['maxhp']}})
     
    for ids in chats.find({}):
        if ids['hp']<=0:
            lost.update_one({},{'$inc':{'amount':1}})
            bot.send_message(ids['id'], 'Вашей лошади плохо в вашем чате, ей не хватает питания. Поэтому я забираю её, чтобы не откинула копыта.\n'+
                            'Количество лошадей, которых мне пришлось забрать (во всех чатах): '+str(lost.find_one({})['amount']))
            chats.remove({'id':ids['id']})
            
    t=threading.Timer(600, check10)
    t.start()
            


check10()


print('7777')
bot.polling(none_stop=True,timeout=600)

