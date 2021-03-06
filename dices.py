import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback
import json
import requests
import http.cookiejar as cookielib
import urllib
import urllib.request as urllib2
CJ = cookielib.LWPCookieJar()
from requests.exceptions import HTTPError



client=MongoClient(os.environ['database'])
db=client.dices
users=db.users
chats = db.chats

OPENER = urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ))
bot = 'https://api.telegram.org/bot'+os.environ['dicebot']+'/'

for url in ['https://api.github.com', 'https://api.github.com/invalid']:
    try:
        response = requests.get(url)
        response.raise_for_status()
        
    except HTTPError as http_err:
        print('HTTP error occurred: '+str(http_err))
    except Exception as err:
        print('Other error occurred: '+str(err))  
    else:
        print('Success!')
        
u_id = 0
ems = ['🎲', '🏀', '🎯', '⚽️']

def createchat(chat):
    return {
        'id':chat['id'],
        'results':True
    }

def createuser(user):
    return {
        'id':user['id'],
        'name':user['first_name'],
        'results':{
            'ball':{
                'score_sum':0,
                'score_amount':0,
                '1':0,
                '2':0,
                '3':0,
                '4':0,
                '5':0
            },
            'darts':{
                'score_sum':0,
                'score_amount':0,
                '1':0,
                '2':0,
                '3':0,
                '4':0,
                '5':0,
                '6':0
            },
            'cube':{
                'score_sum':0,
                'score_amount':0,
                '1':0,
                '2':0,
                '3':0,
                '4':0,
                '5':0,
                '6':0
            },
            'football':{
                'score_sum':0,
                'score_amount':0,
                '1':0,
                '2':0,
                '3':0,
                '4':0,
                '5':0,
                '6':0
            }
        }
    }

try:
    users.find_one({'id':441399484})['results']['football']
except:
    users.update_many({},{'$set':{'results.football':{
                'score_sum':0,
                'score_amount':0,
                '1':0,
                '2':0,
                '3':0,
                '4':0,
                '5':0,
                '6':0
            }}})

#if users.find_one({'id':'bot'}) == None:
#    users.insert_one(createuser({'id':'bot', 'first_name': 'Dices'}))

def massreklama(message):
    i = 0
    for ids in chats.find({}):
        try:
            req = requests.get(bot+'forwardMessage?chat_id='+str(ids['id'])+'&message_id='+str(message['reply_to_message']['message_id'])+'&from_chat_id='+str(message['chat']['id']))
            i+=1
            if i%1000 == 0:
                try:
                    req = requests.get(bot+'sendMessage?chat_id='+str(441399484)+'&text=Сообщение получило '+str(i)+' чатов!')
                except:
                    pass
        except:
            pass
    req = requests.get(bot+'sendMessage?chat_id='+str(441399484)+'&text=Сообщение получило '+str(i)+' чатов!')
        
            
def testreklama(message):
    try:
        req = requests.get(bot+'forwardMessage?chat_id='+str(368543755)+'&message_id='+str(message['reply_to_message']['message_id'])+'&from_chat_id='+str(message['chat']['id']))
        req = requests.get(bot+'forwardMessage?chat_id='+str(441399484)+'&message_id='+str(message['reply_to_message']['message_id'])+'&from_chat_id='+str(message['chat']['id']))
   
    except:
        print(traceback.format_exc())
        print(message)
                        
def new_msg(result):
  try:
    try:
        user = users.find_one({'id':result['message']['from']['id']})
        message = result['message']
    except:
        user = users.find_one({'id':result['result']['from']['id']})
        #result = result['result']
        message = result['result']
    chat = chats.find_one({'id':message['chat']['id']})
    if chat == None:
        chats.insert_one(createchat(message['chat']))
        chat = chats.find_one({'id':message['chat']['id']})
    if 'reply_to_message' in message and 'text' in message and message['from']['id'] == 441399484 and message['text'].lower()[:8] == '/reklama':
            massreklama(message)
    if 'reply_to_message' in message and 'text' in message and message['from']['id'] == 441399484 and message['text'].lower()[:12] == '/testreklama':
            testreklama(message)
    if message['from']['id'] == 441399484 and 'text' in message:
            text = message['text']
            if text.lower()[:8] == '/reklama':
                users.update_one({'id':message['from']['id']},{'$set':{'reklama':True}})
                req = requests.get(bot+'sendMessage?chat_id='+str(441399484)+'&text=Режим рекламы активирован! Отправьте форвард.')
                return
    if message['from']['id'] == 1255836783:
        user = users.find_one({'id':'bot'})
    if user == None:
        users.insert_one(createuser(message['from']))
        user = users.find_one({'id':message['from']['id']})
        amount = 0
        for ids in users.find({}):
            amount += 1
        req = requests.get(bot+'sendMessage?chat_id='+str(441399484)+'&text=Новый юзер: '+user['name']+'. ID: '+str(user['id'])+'. Всего юзеров: '+str(amount))
    #print('MESSAGE!')        
    #print(message)
    if 'dice' in message:
        if 'forward_from' in message:
            return
        try:
            print('DICE!')
            print(message)
            number = message['dice']['value']
            em = message['dice']['emoji']
            if em == '🎯':
                x = 2.5
                rs = 'darts'
                doptxt = 'дротик'
            elif em == '🎲':
                x = 3.3
                rs = 'cube'
                doptxt = 'кубик'
            elif em == '🏀':
                x = 4
                rs = 'ball'
                doptxt = 'мяч'
            elif em == '⚽️':
                x = 4
                rs = 'football'
                doptxt = 'футбольный мяч'
                
            #req = urllib2.Request(bot+'sendMessage?chat_id='+str(result['message']['chat']['id'])+'&text="Брошен кубик!"')
            time.sleep(x)
            if user['id'] != 'bot':
                if chat['results'] == True:
                    req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text=Брошен '+doptxt+'! Результат: '+str(number)+'&reply_to_message_id='+str(message['message_id']))
            users.update_one({'id':user['id']},{'$inc':{'results.'+rs+'.score_sum':number, 'results.'+rs+'.score_amount':1, str(number):number}}) 

        except:
            pass
            
    else:
        if 'text' in message:
            text = message['text']
            if text.lower()[:5] == '/dice' or text.lower()[:20] == '/dice@dice_saver_bot':
                try:
                    em = text.split(' ')[1]
                except:
                    em = random.choice(ems)
                try:
                    item = text.split(' ')[1]
                    if item.lower() in ['darts', 'дартс', 'дротик']:
                        em = '🎯'
                    if item.lower() in ['basketball', 'баскетбол', 'мяч', 'мячик', 'корзина']:
                        em = '🏀'
                    if item.lower() in ['cube', 'куб', 'кубик', 'кости']:
                        em = '🎲'
                    if item.lower() in ['футбол', 'football', '⚽️']:
                        em = '⚽️'
                except:
                    pass
                if em not in ems:
                    em = random.choice(ems)
                try:
                    req = requests.get(bot+'sendDice?chat_id='+str(message['chat']['id'])+'&emoji='+em+'&reply_to_message_id='+str(message['message_id']))
                    #content = OPENER.open(req).read()
                    msg = json.loads(req.text)
                    print(msg)
                    new_msg(msg)
                except:
                    pass
                    
            elif text.lower()[:9] == '/my_dices' or text.lower()[:24] == '/my_dices@dice_saver_bot':
                txt = ''
                txt += 'Статистика бросков '+user['name']+':\n\n'
                txt += '🎲:\n'
                txt += '   Количество бросков: '+str(user['results']['cube']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['cube']['score_sum']/user['results']['cube']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                txt += '\n'
                txt += '🎯:\n'
                txt += '   Количество бросков: '+str(user['results']['darts']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['darts']['score_sum']/user['results']['darts']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                
                txt += '\n'
                txt += '🏀:\n'
                txt += '   Количество бросков: '+str(user['results']['ball']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['ball']['score_sum']/user['results']['ball']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                txt += '\n'
                txt += '⚽️:\n'
                txt += '   Количество бросков: '+str(user['results']['football']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['football']['score_sum']/user['results']['ball']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+txt+'&reply_to_message_id='+str(message['message_id']))
            
            elif text.lower()[:10] == '/bot_dices' or text.lower()[:25] == '/bot_dices@dice_saver_bot':
                user = users.find_one({'id':'bot'})
                txt = ''
                txt += 'Статистика бросков бота '+user['name']+':\n\n'
                txt += '🎲:\n'
                txt += '   Количество бросков: '+str(user['results']['cube']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['cube']['score_sum']/user['results']['cube']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                txt += '\n'
                txt += '🎯:\n'
                txt += '   Количество бросков: '+str(user['results']['darts']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['darts']['score_sum']/user['results']['darts']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                
                txt += '\n'
                txt += '🏀:\n'
                txt += '   Количество бросков: '+str(user['results']['ball']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['ball']['score_sum']/user['results']['ball']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                txt += '\n'
                txt += '⚽️:\n'
                txt += '   Количество бросков: '+str(user['results']['football']['score_amount'])+'\n'
                try:
                    txt += '   Средний балл: '+str(round(user['results']['football']['score_sum']/user['results']['ball']['score_amount'], 3))+'\n'
                except:
                    txt += '   Средний балл: 0\n'
                    
                req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+txt+'&reply_to_message_id='+str(message['message_id']))
            
            elif text.lower()[:6] == '/start' and message['chat']['type'] == 'private':
                req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+'Я могу сохранять результаты бросков кубика/дротика/мяча. Если добавить меня в группу, то я буду записывать статистику бросков и там.')
            
            elif text.lower()[:5] == '/help' or text.lower()[:20] == '/help@dice_saver_bot':
                tt = ''
                tt += 'Дополнительные функции бота:\n\n1. Имеется возможность после команды /dice написать, какой именно бросок сделать. Все возможные варианты:\n'+\
                '/dice куб/кубик/кости/cube/🎲\n'+\
                '/dice мяч/мячик/баскетбол/корзина/basketball/🏀\n'+\
                '/dice дротик/дартс/darts/🎯\n'+\
                '/dice футбол/football/⚽️'
                tt += '\n\n'
                tt += '2. Когда вы используете /dice, этот бросок засчитывается боту. Увидеть статистику можно по команде /bot_dices.'
                req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+tt)
            
            elif text.lower()[:11] == '/off_result' or text.lower()[:26] == '/off_result@dice_saver_bot':
                chatu = requests.get(bot+'getChatMember?chat_id='+str(message['chat']['id'])+'&user_id='+str(user['id']))
                msgg = json.loads(chatu.text)
                print(msgg)
                if message['chat']['type'] != 'private':
                    if msgg['result']['status'] not in ['creator', 'administrator']:
                        req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+'Только администратор чата может делать это!')
                        return
                    
                                     
                    
                if chat['results'] == True:
                    chats.update_one({'id':chat['id']},{'$set':{'results':False}})
                    req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+'Вывод результатов броска отключен!')
                    
                if chat['results'] == False:
                    chats.update_one({'id':chat['id']},{'$set':{'results':True}})
                    req = requests.get(bot+'sendMessage?chat_id='+str(message['chat']['id'])+'&text='+'Вывод результатов броска включен!')
  except:
    pass

        
def polling():
    global u_id
    while True:
        try:
            #rq = 'https://api.telegram.org/bot'+os.environ['TELEGRAM_TOKEN']+'/getUpdates'
            req = urllib2.Request(bot+'getUpdates?offset='+str(u_id))
            content = OPENER.open(req).read()
            for result in json.loads(content)['result']:
                u_id = result['update_id']+1
                #if(result['message']['text'] == 'привет'):
                #    url = BASE_URL + 'sendMessage'
                #    req = urllib2.Request(url)
                #    req.add_header("Accept","application/json")
                #    req.add_header('User-agent',USER_AGENT)
                #    req.add_data(urllib.urlencode({'chat_id':result['message']['chat']['id'],'text':'Эй Привет чувак!'}))
                #    OPENER.open(req).read()
                threading.Thread(target = new_msg, args = [result]).start()
        except:
            pass
            time.sleep(5)
        
    
    

    
              
def send_message():
    i = 'https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage?chatid=chatid'
