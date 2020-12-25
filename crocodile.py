
import json
import random
import time
import traceback
import threading
import config



import os
from pymongo import MongoClient
import requests
from telebot import types, TeleBot

url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97'
lang = 'ru-en'

bot = TeleBot(os.environ['crocodile'])
client = MongoClient(os.environ['database'])
db = client.crocodile
users = db.users
chats = db.chats
words = db.words
blocked = db.blocked
if words.find_one({}) == None:
    words.insert_one({'words': []})
   
resetlist = []
    
banned = [787340171]
cache = []
cache_old = []
ws = words.find_one({})['words']
i = 0
for ids in ws:
    try:
        a = cache[i]
    except:
        cache.append([])
    cache[i].append(ids)
    if len(cache[i]) >= 1000:
        i += 1
        
i = 0
for ids in ws:
    if i <= 3300:
        cache_old.append(ids)
    i+=1

adm = [441399484]

#chats.update_many({},{'$set':{'words':[]}})


@bot.message_handler(func = lambda m: time.time() - m.date >= 120)
def skippp(m):
    pass

#@bot.callback_query_handler(func = lambda call: time.time() - star)
#def skp(call):
#    pass

@bot.message_handler(commands=['select_chat'])
def selectchatt(m):
    #config.about(m, bot)
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    users.update_one({'id':user['id']},{'$set':{'curchat':m.chat.id}})
    bot.send_message(m.chat.id, 'Вы выбрали чат для добавления слов: "'+str(m.chat.title)+'". Теперь переключайтесь '+
                     'ко мне в ЛС и присылайте слова (просто слова, без каких-либо команд!), которые '+
                     'хотите добавить в список. Для отмены напишите команду /deselect_chat.')
    
@bot.message_handler(commands=['deselect_chat'])
def deselectchatt(m):
    #config.about(m, bot)
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    users.update_one({'id':user['id']},{'$set':{'curchat':None}})
    bot.send_message(m.chat.id, 'Успешно выключен режим добавления новых слов.')
    
@bot.message_handler(commands=['manage_words'])
def manageworrds(m):
    #config.about(m, bot)
    text = '/select_chat - выбрать чат, над которым будете проводить нижеописанные операции.\n'+\
    '/deselect_chat - отменить операции над чатом.\n'+\
    '/del_words - включить/отключить режим удаления слов из чата.\n'
    bot.send_message(m.chat.id, text)
    
    
@bot.message_handler(commands=['del_words'])
def delwordss(m):
    #config.about(m, bot)
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    if user['delwords']:
        users.update_one({'id':user['id']},{'$set':{'delwords':False}})
        bot.send_message(m.chat.id, 'Отключено удаление слов из списка чата!')
    else:
        users.update_one({'id':user['id']},{'$set':{'delwords':True}})
        bot.send_message(m.chat.id, 'Включено удаление слов из списка чата! Теперь присылайте мне в ЛС слова '+
                         '(без команд и прочего, просто текстом), которые хотите удалить. Для отмены снова напишите эту команду.')
    

@bot.message_handler(commands=['ping'])
def ping(m):
    #config.about(m, bot)
    bot.send_message(m.chat.id, 'Pong!', reply_to_message_id=m.message_id)


@bot.message_handler(commands=['sendm'])
def pinsendg(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        i = 0
        for ids in chats.find({}):
            try:
                bot.send_message(ids['id'], m.text.split('/sendm ')[1])
                i+=1
            except:
                pass
        bot.send_message(441399484, str(i)+' чатов получили сообщение!')
    
@bot.message_handler(commands=['resetstats_crocodile'])
def resetstats(m):
    #config.about(m, bot)
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status != 'creator':
        bot.send_message(m.chat.id, 'Только создатель чата может сбросить статистику!')
        return 
    if m.chat.id not in resetlist:
        resetlist.append(m.chat.id)
        bot.send_message(m.chat.id, 'Для подтверждения очистки статистики повторно отправьте команду в чат.')
        threading.Timer(60, rr, args = [m.chat.id]).start()
        return
    else:
        chats.update_one({'id':m.chat.id},{'$set':{'users':{}}})
        bot.send_message(m.chat.id, 'Статистика чата сброшена!')
        rr(m.chat.id)

def rr(id):
    try:
        resetlist.remove(id)
    except:
        pass

@bot.message_handler(commands=['upd_croco'])
def updccccc(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        chats.update_many({},{'$set':{'customusers':None}})
        
@bot.message_handler(commands=['set_list'])
def updccccclist(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        chats.update_one({'id':m.chat.id},{'$set':{'customusers':[]}})
        bot.send_message(m.chat.id, 'Список чата создан!')
        
@bot.message_handler(commands=['add_list'])
def updccccclistsss(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        try:
            if m.reply_to_message.from_user.id not in chats.find_one({'id':m.chat.id}):
                chats.update_one({'id':m.chat.id},{'$push':{'customusers':m.reply_to_message.from_user.id}})
                bot.send_message(m.chat.id, m.reply_to_message.from_user.first_name+' добавлен в список чата!')
            else:
                bot.send_message(m.chat.id, m.reply_to_message.from_user.first_name+' уже был в списке!')
        except:
            bot.send_message(m.chat.id, 'Ошибка!')
          
    
    
@bot.message_handler(commands=['massadd'])
def massadd(m):
    #config.about(m, bot)
    try:
        if m.from_user.id != 441399484:
            return
        x = []
        y = m.text.split('/massadd ')
        if len(y) > 1:
            y = y[1]
            print(y)
            y = y.replace('\xa0', ' ')
            y = y.split(', ')
            print(y)
            for ids in y:
                print(ids)
                x.append(ids.lower())

        for ids in x:
            if ids not in words.find_one({})['words']:
                words.update_one({}, {'$push': {'words': ids}})
            else:
                bot.send_message(m.chat.id, 'Слово "`' + ids + '`" уже существует!', parse_mode='markdown')
    except:
        bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['unblock'])
def unblock(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        try:
            blocked.remove({'id': m.text.split(' ')[1]})
            bot.send_message(m.chat.id, 'Разблокирован пользователь: "' + m.text.split(' ')[1] + '"!')
        except:
            bot.send_message(m.chat.id, 'Ошибка!')


@bot.message_handler(commands=['offer'])
def offer(m):
  #config.about(m, bot)
  bot.send_message(m.chat.id, 'Функция временно отключена!')
  return
  try:
    if blocked.find_one({'id': str(m.from_user.id)}) != None:
        return
    x = m.text.split('/offer ')
    if len(x) > 1:
        word = x[1].lower()
        if word in words.find_one({})['words']:
            bot.send_message(m.chat.id, 'Предложенное вами слово уже существует!')
            return
        else:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(text='Принять слово',
                                              callback_data='allow_word ' + word + ' ' + str(m.from_user.id)))
            kb.add(types.InlineKeyboardButton(text='Отклонить слово', callback_data='disallow_word ' + word))
            kb.add(types.InlineKeyboardButton(text='ᅠ', callback_data='qwerty'))
            kb.add(types.InlineKeyboardButton(text='Заблокировать пользователя',
                                              callback_data='block ' + str(m.from_user.id)))
            name = m.from_user.first_name.replace('*', '\*').replace('_', '\_').replace('`', '\`').replace('[',
                                                                                                           '').replace(
                ']', '').replace('(', '').replace(')', '')
            bot.send_message(441399484, 'Новое слово: "' + word + '"! Автор: [' + name + '](tg://user?id=' + str(
                m.from_user.id) + '). Принять?', reply_markup=kb, parse_mode='markdown')
            bot.send_message(m.chat.id,
                             'Вы успешно предложили слово. Если его одобрят, вы получите уведомление в ЛС (не забудьте открыть его со мной).')

    else:
        bot.send_message(m.chat.id, 'Предложите слово в следующем формате:\n/offer *слово*', parse_mode='markdown')
  except:
    pass


#@bot.message_handler(commands=['lang'])
#def lang(m):
#    chat = chats.find_one({'id': m.chat.id})
#    if chat['lang'] == 'ru':
#        chats.update_one({'id': chat['id']}, {'$set': {'lang': 'eng'}})
#        bot.send_message(m.chat.id, 'The language has been changed to English!')
#    else:
#        chats.update_one({'id': chat['id']}, {'$set': {'lang': 'ru'}})
#        bot.send_message(m.chat.id, 'Язык был изменён на русский!')


@bot.message_handler(commands=['add'])
def addd(m):
    #config.about(m, bot)
    if m.from_user.id in adm:
        x = m.text.split(' ')
        if len(x) > 1:
            word = x[1].lower()
            if word not in words.find_one({})['words']:
                words.update_one({}, {'$push': {'words': word}})
                bot.send_message(m.chat.id, 'Успешно добавлено слово "' + word + '"!')
            else:
                bot.send_message(m.chat.id, 'Это слово уже есть!')


@bot.message_handler(commands=['del'])
def addd(m):
    #config.about(m, bot)
    if m.from_user.id in adm:
        x = m.text.split('/del ')
        if len(x) > 1:
            word = x[1].lower()
            if word in words.find_one({})['words']:
                words.update_one({}, {'$pull': {'words': word}})
                bot.send_message(m.chat.id, 'Успешно удалено слово "' + word + '"!')
            else:
                bot.send_message(m.chat.id, 'Такого слова нет!')


@bot.message_handler(commands=['words'])
def wordssss(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        allw = len(words.find_one({})['words'])
        bot.send_message(m.chat.id, 'Всего я знаю ' + str(allw) + ' слов!')


@bot.message_handler(commands=['statistic'])
def stats(m):
    #config.about(m, bot)
    chat = chats.find_one({'id': m.chat.id})
    db_top = []
    text = 'Статистика чата:\n\n'
    if chat == None:
        return
    while len(db_top) < len(chat['users']) and len(db_top) <= 20:
        nowu = None
        nowsc = 0
        for ids in chat['users']:
            if chat['users'][ids]['score'] >= nowsc and chat['users'][ids] not in db_top:
                nowsc = chat['users'][ids]['score']
                nowu = chat['users'][ids]
        if nowu != None:
            db_top.append(nowu)
    i = 1
    for ids in db_top:
        text += str(i) + '. ' + ids['name'] + ' (' + str(ids['score']) + ' слов)\n'
        i += 1
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['start'])
def creategame(m):
    #config.about(m, bot)
    if m.from_user.id in banned:
        return
    if '@' in m.text:
        uname = m.text.split('@')[1]
        if uname.lower() != 'crocodilefreebot':
            return
    chat = chats.find_one({'id': m.chat.id})
    if chat == None:
        chats.insert_one(createchat(m))
        chat = chats.find_one({'id': m.chat.id})

    allow = True
    if chat['currentgame'] != None:
        game = chat['currentgame']
        if time.time() - game['starttime'] >= 120:
            chats.update_one({'id': m.chat.id}, {'$set': {'currentgame': None}})
        else:
            bot.send_message(m.chat.id, 'Ещё не прошло 2 минуты с начала предыдущей игры!')
            allow = False
            return
    if allow:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Я!', callback_data='start'))
        bot.send_message(m.chat.id, '🙈Кто желает быть ведущим?', reply_markup=kb)

@bot.message_handler(commands=['switch'])
def swwww(m):
    #config.about(m, bot)
    x = bot.get_chat_member(m.chat.id, m.from_user.id)
    if x.status == 'creator' or x.status == 'administrator':
        chat = chats.find_one({'id':m.chat.id})
        if chat != None:
            if chat['old'] == False:
                chats.update_one({'id':m.chat.id},{'$set':{'old':True}})
                bot.send_message(m.chat.id, 'Включён режим "старый словарь"!')
            else:
                chats.update_one({'id':m.chat.id},{'$set':{'old':False}})
                bot.send_message(m.chat.id, 'Включён режим "новый словарь"!')
        else:
            bot.send_message(m.chat.id, 'Сначала сыграйте хотя бы одну игру!')
    else:
        bot.send_message(m.chat.id, 'Только администратор может делать это!')
        
@bot.message_handler(content_types=['text'])
def allmsg(m):
    #config.about(m, bot)
    try:
        if m.from_user.id in banned:
            return
        chat = newchat(m)
        if m.chat.id == m.from_user.id:
            user = users.find_one({'id':m.chat.id})
            if user != None:
                if user['curchat'] != None:
                    if user['delwords'] == False:
                        u = bot.get_chat_member(user['curchat'], user['id'])
                        if u.status not in ['administrator', 'creator']:
                            bot.send_message(m.chat.id, 'Вы не администратор того чата, в который хотите добавить слово! '+
                                             'Для окончания добавления '+
                                        'напишите команду /deselect_chat.')
                            return
                        chats.update_one({'id':user['curchat']},{'$push':{'words':m.text.lower()}})
                        bot.send_message(m.chat.id, 'Добавлено новое слово в чат: "'+m.text.lower()+'"! Для окончания добавления '+
                                        'напишите команду /deselect_chat.')
                        
                    else:
                        u = bot.get_chat_member(user['curchat'], user['id'])
                        if u.status not in ['administrator', 'creator']:
                            bot.send_message(m.chat.id, 'Вы не администратор того чата, из которого хотите удалить слово! '+
                                             'Для окончания удаления '+
                                        'напишите команду /del_words.')
                            return
                        chats.update_one({'id':user['curchat']},{'$pull':{'words':m.text.lower()}})
                        bot.send_message(m.chat.id, 'Удалено слово: "'+m.text.lower()+'"! Для окончания удаления '+
                                        'напишите команду /del_words.')
                        
        if m.forward_from != None:
            if m.forward_from.id == 728114349 and m.from_user.id == 441399484:
                try:
                    word = m.text.split('слово ')[1].lower()
                    if word not in words.find_one({})['words']:
                        words.update_one({}, {'$push': {'words': word}})
                    else:
                        bot.send_message(m.chat.id, 'Это слово уже есть: ' + word + '!')
                    return
                except:
                    pass
        if chat['currentgame'] != None:
            game = chat['currentgame']
            if m.text.lower() == game['word'].lower() or m.text.lower() == game['word'].lower().replace('ё', 'e'):
                if m.from_user.id == game['master']:
                    bot.send_message(m.chat.id, 'Ведущему нельзя называть слово! Отменяю игру.')
                    chats.update_one({'id': chat['id']}, {'$set': {'currentgame': None}})
                    kb = types.InlineKeyboardMarkup()
                    kb.add(types.InlineKeyboardButton(text='Я!', callback_data='start'))
                    bot.send_message(m.chat.id, '🙈Кто желает быть ведущим?', reply_markup=kb)
                    return
                if str(m.from_user.id) not in chat['users']:
                    chats.update_one({'id': chat['id']},
                                     {'$set': {'users.' + str(m.from_user.id): createchatuser(m.from_user)}})

                chats.update_one({'id': chat['id']}, {'$inc': {'users.' + str(m.from_user.id) + '.score': 1}})
                chats.update_one({'id': chat['id']}, {'$set': {'currentgame': None}})
                name = m.from_user.first_name.replace('*', '\*').replace('_', '\_').replace('`', '\`').replace('[',
                                                                                                               '').replace(
                    ']', '').replace('(', '').replace(')', '')
                bot.send_message(m.chat.id, '🙈[' + name + '](tg://user?id=' + str(m.from_user.id) + ') ' +
                                 'угадал слово:\n*' + game['word'].title() + '*', parse_mode='markdown')
                chats.update_one({'id': chat['id']},
                                 {'$set': {'currentmaster': m.from_user.id, 'answer_time': time.time()}})
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(text='Я!', callback_data='start'))
                bot.send_message(m.chat.id, '🙈Кто желает быть ведущим?', reply_markup=kb)

    except:
        bot.send_message(441399484, traceback.format_exc())


def createchatuser(user):
    return {
        'name': user.first_name,
        'username': user.username,
        'id': user.id,
        'score': 0
    }


@bot.message_handler(content_types=['new_chat_member'])
def newc(m):
    #config.about(m, bot)
    newchat(m)


def newchat(m):
    chat = chats.find_one({'id': m.chat.id})
    if chat == None:
        chats.insert_one(createchat(m))
        chat = chats.find_one({'id': m.chat.id})
    return chat


@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    try:
        if call.from_user.id in banned:
            return
        chat = chats.find_one({'id': call.message.chat.id})
        if chat == None:
            return
        if call.data == 'start':
            allow = True
            if chat['currentgame'] != None:
                game = chat['currentgame']
                if time.time() - game['starttime'] >= 120:
                    chats.update_one({'id': chat['id']}, {'$set': {'currentgame': None}})
                else:
                    bot.answer_callback_query(call.id, 'Ещё не прошло 2 минуты с начала предыдущей игры!',
                                              show_alert=True)
                    allow = False
                    return
            try:
                if chat['currentmaster'] != None and time.time() - chat['answer_time'] <= 8 and call.from_user.id != \
                        chat['currentmaster']:
                    bot.answer_callback_query(call.id,
                                              'Только тот, кто отгадал, может нажать на эту кнопку! Ограничение будет снято через 8 секунд.',
                                              show_alert=True)
                    return
            except:
                pass
            if allow:
                try:
                    medit('Ведущий был выбран!', call.message.chat.id, call.message.message_id)
                except:
                    return
                chats.update_one({'id': chat['id']}, {'$set': {'currentgame': creategame(call)}})
                kb = types.InlineKeyboardMarkup(row_width=3)
                kb.add(types.InlineKeyboardButton(text='👁Посмотреть слово', callback_data='look_word'))
                kb.add(types.InlineKeyboardButton(text='🔁Сменить слово', callback_data='change_word'))
                name = call.from_user.first_name.replace('*', '\*').replace('_', '\_').replace('`', '\`').replace('[',
                                                                                                                  '').replace(
                    ']', '').replace('(', '').replace(')', '')
                bot.send_message(call.message.chat.id, '🙈[' + name + '](tg://user?id=' + str(
                    call.from_user.id) + ') должен объяснить слово.' +
                                 ' Сменить ведущего можно будет через 2 минуты.', reply_markup=kb,
                                 parse_mode='markdown')
                chats.update_one({'id': chat['id']}, {'$set': {'currentmaster': None, 'answer_time': None}})

        if call.data == 'look_word':
            game = chat['currentgame']
            if game == None:
                bot.answer_callback_query(call.id, 'Игра не запущена! Запустить можно по команде /start.',
                                          show_alert=True)
                return
            if game['master'] == call.from_user.id:
                bot.answer_callback_query(call.id, 'Нужно объяснить слово: ' + game['word'].title(), show_alert=True)
            else:
                bot.answer_callback_query(call.id, 'Не вы загадываете слово!', show_alert=True)

        if call.data == 'change_word':
            game = chat['currentgame']
            if game == None:
                bot.answer_callback_query(call.id, 'Игра не запущена! Запустить можно по команде /start.',
                                          show_alert=True)
                return
            if call.from_user.id != game['master']:
                bot.answer_callback_query(call.id, 'Не вы загадываете слово!', show_alert=True)
                return
            if chat['old'] == False:
                word = random.choice(random.choice(cache))
            else:
                allcache = cache_old.copy()
                for ids in chat['words']:
                    allcache.append(ids)
                word = random.choice(allcache)
            word = word.replace('ё', 'е').replace('Ё', 'Е')
            global url
            global key
            global lang
            text = word
            try:
                #r = requests.post(url, data={'key': key, 'text': text, 'lang': lang})
                #print(r.text)
                #if chats.find_one({'id': call.message.chat.id})['lang'] == 'eng':
                #    word = r.text
                #    print(word)
                pass
            except:
                print(traceback.format_exc())
            chats.update_one({'id': call.message.chat.id}, {'$set': {'currentgame.word': word}})
            bot.answer_callback_query(call.id, 'Нужно объяснить слово: ' + word.title(), show_alert=True)

        if 'disallow_word' in call.data:
            medit('Слово "' + call.data.split('disallow_word ')[1] + '" отменено.', call.message.chat.id,
                  call.message.message_id)

        elif 'allow_word' in call.data:
            word = call.data.split(' ')[1]
            if word not in words.find_one({})['words']:
                words.update_one({}, {'$push': {'words': word}})
                try:
                    bot.send_message(call.data.split(' ')[2], 'Ваше слово "' + word + '" было добавлено в игру!')
                except:
                    pass
                medit('Добавлено слово: "' + word + '".', call.message.chat.id, call.message.message_id)
            else:
                bot.send_message(call.message.chat.id, 'Это слово уже есть!')

        elif 'block' in call.data:
            blocked.insert_one({'id': call.data.split(' ')[1]})
            medit('Пользователь заблокирован: "`' + call.data.split(' ')[1] + '`".', call.message.chat.id,
                  call.message.message_id, parse_mode='markdown')
            bot.send_message(call.data.split(' ')[1], 'Вам было запрещено предлагать слова!')

    except:
        bot.send_message(441399484, traceback.format_exc())


def medit(message_text, chat_id, message_id, reply_markup=None, parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text,
                                 reply_markup=reply_markup,
                                 parse_mode=parse_mode)


def createuser(user):
    return {
        'id':user.id,
        'name':user.first_name,
        'curchat':None,
        'delwords':False
    }

def creategame(call):
    global url
    global key
    global lang
    chat = chats.find_one({'id':call.message.chat.id})
    if chat['old'] == False:
        word = random.choice(random.choice(cache))
    else:
        allcache = cache_old.copy()
        for ids in chat['words']:
            allcache.append(ids)
        word = random.choice(allcache)    
    word = word.replace('ё', 'е').replace('Ё', 'Е')
    text = word
    return {
        'master': call.from_user.id,
        'starttime': time.time(),
        'word': word
    }


def createchat(m):
    return {
        'id': m.chat.id,
        'users': {},
        'currentgame': None,
        'currentmaster': None,
        'answer_time': None,
        'lang': 'ru',
        'old':True,
        'customusers':None,
        'words':[]
    }
