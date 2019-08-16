# -*- coding: utf-8 -*-
import os
import random


import threading
import time
import traceback

import telebot
from pymongo import MongoClient

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

client = MongoClient(os.environ['database'])
db = client.chatpets
users = db.users
chats = db.chats
globalchats = db.globalchats
lost = db.lost
chat_admins=db.chat_admins

ban = [243153864, 866706209, ]
totalban = [243153864, 866706209, 598442962,765420407, 
 786508668, 633357981,   521075049,  788297567, 709394939, 
   638625062,  872696708,941085059,  958911815, 579555709, 725226227] 
block=[-1001365421933, 725226227]


if lost.find_one({'amount': {'$exists': True}}) is None:
    lost.insert_one({'amount': 0})

botname = 'Chatpetsbot'
admin_id = 441399484


#globalchats.update_many({},{'$push':{'avalaible_pets':'horse'}})

#users.update_many({},{'$set':{'now_elite':False}})
@bot.message_handler(commands=['send'])
def sendd(m):
    if is_from_admin(m):
        try:
            text = ''
            i = 2
            a = m.text.split(' ')
            while i < len(a):
                text += a[i] + ' '
                i += 1
            bot.send_message(m.text.split(' ')[1], text)
        except:
            pass

@bot.message_handler(commands=['switch_lvlup'])
def switch_lvlup(m):
  try:
    chat=chats.find_one({'id':m.chat.id})
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status == 'creator' or user.status=='administrator' or m.from_user.id==m.chat.id:
        if chat['send_lvlup']==True:
            chats.update_one({'id':m.chat.id},{'$set':{'send_lvlup':False}})
            bot.send_message(m.chat.id, 'Теперь питомец *НЕ* будет присылать вам уведомления о повышении уровня!', parse_mode='markdown')
        else:
            chats.update_one({'id':m.chat.id},{'$set':{'send_lvlup':True}})
            bot.send_message(m.chat.id, 'Теперь питомец будет присылать вам уведомления о повышении уровня!')
    else:
        bot.send_message(m.chat.id, 'Только администраторы чата могут делать это!')

  except:
    pass

@bot.message_handler(commands=['showlvl'])
def lvlvlvlvl(m):
    if is_from_admin(m):
        try:
            pet = {'lvl': int(m.text.split(' ')[1])}
            x = nextlvl(pet)
            bot.send_message(m.chat.id, str(x))
        except:
            pass

        
@bot.message_handler(commands=['donate'])
def donate(m):
    text='Для совершения добровольного пожертвования можно использовать Сбербанк. '+\
    'Номер карты: `5336 6900 5562 4037`\nЗаранее благодарю!'
    bot.send_message(m.chat.id, text, parse_mode='markdown')
        

@bot.message_handler(commands=['do'])
def do(m):
    if is_from_admin(m):
        try:
            x = m.text.split('/do ')[1]
            try:
                eval(x)
            except:
                bot.send_message(441399484, traceback.format_exc())
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['stop'])
def stopp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': int(m.text.split(' ')[1])}, {'$set': {'spying': None}})
            bot.send_message(m.chat.id, 'success')
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['showchat'])
def showchat(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': int(m.text.split(' ')[1])}, {'$set': {'spying': m.chat.id}})
            bot.send_message(m.chat.id, 'success')
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['growpet'])
def grow(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is not None:
        bot.send_message(m.chat.id, 'У вас уже есть лошадь!')
        return

    chats.insert_one(createpet(m.chat.id))
    bot.send_message(m.chat.id,
                     'Поздравляю! Вы завели питомца (лошадь)! О том, как за ней ухаживать, можно прочитать в /help.')


    
@bot.message_handler(commands=['set_admin'])
def set_admin(m):
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status == 'creator':
        if m.reply_to_message!=None:
            chatt=chat_admins.find_one({'id':m.chat.id})
            if chatt==None:
                chat_admins.insert_one(createchatadmins(m))
                chatt=chat_admins.find_one({'id':m.chat.id})
            if int(m.reply_to_message.from_user.id) not in chatt['admins']:
                chat_admins.update_one({'id':m.chat.id},{'$push':{'admins':int(m.reply_to_message.from_user.id)}})
                bot.send_message(m.chat.id, 'Успешно установлен админ лошади: '+m.reply_to_message.from_user.first_name)
            else:
                bot.send_message(m.chat.id, 'Этот юзер уже является администратором лошади!')
        else:
            bot.send_message(m.chat.id, 'Сделайте реплай на сообщение цели!')
    else:
        bot.send_message(m.chat.id, 'Только создатель чата может делать это!')
                    
    
@bot.message_handler(commands=['remove_admin'])
def remove_admin(m):
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status == 'creator':
        if m.reply_to_message!=None:
            chatt=chat_admins.find_one({'id':m.chat.id})
            if chatt==None:
                chat_admins.insert_one(createchatadmins(m))
                chatt=chat_admins.find_one({'id':m.chat.id})
            if int(m.reply_to_message.from_user.id) in chatt['admins']:
                chat_admins.update_one({'id':m.chat.id},{'$pull':{'admins':int(m.reply_to_message.from_user.id)}})
                bot.send_message(m.chat.id, 'Успешно удалён админ питомца: '+m.reply_to_message.from_user.first_name+'.')
            else:
                bot.send_message(m.chat.id, 'Этот юзер не является администратором питомца!')
        else:
            bot.send_message(m.chat.id, 'Сделайте реплай на сообщение цели!')
    else:
        bot.send_message(m.chat.id, 'Только создатель чата может делать это!')
    
    
    
def createchatadmins(m):
    return {
        'id':m.chat.id, 
        'admins':[]
    }
    
@bot.message_handler(commands=['getids'])
def idssssss(m):
    if is_from_admin(m):
        text = ''
        for h in lost.find({'id': {'$exists': True}}):
            text += str(h['id']) + ' ' + h['name'] + '\n'
        bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['feed'])
def feeed(m):
    if m.text.lower()=='/feed' or m.text.lower()=='/feed@chatpetsbot':
        x = chats.find_one({'id': m.chat.id})
        if x is None:
            bot.send_message(m.chat.id, 'А кормить некого:(')
            return
        if x['type']=='horse':
            spisok = ['яблоко', 'сено', 'хлеб', 'шоколадку', 'кукурузу', 'сахар', 'траву', 'рыбу', 'сосиску', 'макароны']
            s2 = ['немного металла', 'мышьяк', 'доску', 'хрен', 'сорняк', 'телефон', 'лошадь', 'автобус', 'компухтер', 'карман']
            petname='Лошадь'
        if x['type']=='cat':
            spisok=['рыбу', 'мышь', 'кошачий корм', 'колбасу']
            s2=['миску', 'одеяло', 'шерсть']
            petname='Кот'
        if x['type']=='parrot':
            spisok=['траву', 'корм для попугая', 'орех', 'банан']
            s2=['телефон', 'клетку']
            petname='Попугай'
        if x['type']=='dog':
            spisok=['кость', 'корм для собак', 'куриную ножку', 'голубя']
            s2=['столб', 'мусорный бак', 'тетрадь']
            petname='Собака'
        if x['type']=='bear':
            spisok=['мёд', 'оленя', 'шишку']
            s2=['берлогу', 'горящую машину, а медведь сел в неё и сгорел']
            petname='Медведь'
        if x['type']=='pig':
            spisok=['корм для свиней', 'яблоко', 'гриб', 'белку']
            s2=['грязь', 'бриллианты']
            petname='Свинка'
        if x['type']=='hedgehog':
            spisok=['гриб', 'яблоко', 'жука', 'муравья']
            s2=['змею', 'стул', 'мяч']
            petname='Ёж'
        if x['type']=='octopus':
            spisok=['моллюска', 'улитку', 'рака', 'ската']
            s2=['банку с планктоном', 'корабль', 'сокровища']
            petname='Осьминог'
        if x['type']=='turtle':
            spisok=['капусту', 'яблоко', 'арбуз', 'дыню', 'хлеб']
            s2=['попугая', 'осьминога', 'карман']
            petname='Черепаха'
        if x['type']=='crab':
            spisok=['рыбий корм', 'морковь', 'перец', 'креветку', 'таракана', 'огурец']
            s2=['камень', 'крабовые чипсы']
            petname='Краб'
        if x['type']=='spider':
            spisok=['муху', 'стрекозу', 'кузнечика', 'попугая', 'жука']
            s2=['дом', 'слона']
            petname='Паук'
        if x['type']=='bee':
            spisok=['немного нектара', 'немного пыльцы', 'кусочек сахара']
            s2=['муравья', 'кита', 'цветок']
            petname='Пчела'
        if x['type']=='owl':
            spisok=['мышь', 'пчелу', 'рыбу', 'таракана']
            s2=['сову', 'компьютерную мышь', 'волка']
            petname='Сова'
        if x['type']=='boar':
            spisok=['орех', 'жёлудь']
            s2=['дерево', 'землю']
            petname='Кабан'
        if x['type']=='panda':
            spisok=['бамбук', 'большой бамбук', 'маленький бамбук', 'средний бамбук', 'яблоко', 'морковь', 'сосиску']
            s2=['лопату', 'не бамбук']
            petname='Панда'
        if x['type']=='cock':
            spisok=['зерно', 'лягушку', 'муху', 'муравья']
            s2=['доту', 'аниме', 'футбол', 'качалку', 'лигу легенд', 'hearthstone']
            petname='Петух'
        if x['type']=='onehorn':
            spisok=['радугу', 'сено', 'овёс', 'картошку']
            s2=['автобус', 'телефон', 'того, кто не верит в единорогов']
            petname='Единорог'
        if random.randint(1, 100) <= 80:
            s = spisok
        else:
            s = s2
        word = random.choice(s)
        name = m.from_user.first_name
        name = name.replace('*', '').replace('_', '').replace("`", "")
        name2=x['name'].replace('*', '').replace('_', '').replace("`", "")
        text = name + ' достаёт из кармана *' + word + '* и кормит ' + name2 + '. '+petname+' с аппетитом съедает это!'
        bot.send_message(m.chat.id, text, parse_mode='markdown')


@bot.message_handler(commands=['commands'])
def commands(m):
  if m.text.lower()=='/commands' or m.text.lower()=='/commands@chatpetsbot':
    text = '/feed - покормить питомца (ни на что не влияет, просто прикол);\n'
    text += '/pogladit - погладить питомца\n'
    text+='/set_admin (только для создателя чата) - разрешить выбранному юзеру выгонять питомца из чата\n'
    text+='/remove_admin (только для создателя чата) - запретить юзеру выгонять питомца (только если ранее ему было это разрешено);\n'
    text+='/achievement_list - список ачивок, за которые можно получить кубы;\n'
    text+='/use_dice - попытка на получение нового типа питомцев;\n'
    text+='/select_pet pet - выбор типа питомца.\n'
    text+='@Chatpets - канал с обновлениями бота!'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['getpets'])
def getpet(m):
    if is_from_admin(m):
        db_pets = chats.find().sort('lvl', -1).limit(10)
        text = 'Топ-10 питомцев:\n\n'
        i = 1
        for doc in db_pets:
            text += str(i) + ' место: ' + doc['name'] + ' (' + str(doc['lvl']) + ' лвл) (`' + str(
                doc['id']) + '`)' + '\n'
            i += 1
        try:
            bot.send_message(m.chat.id, text, parse_mode='markdown')
        except:
            bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['rules'])
def rules(m):
  if m.text.lower()=='/rules' or m.text.lower()=='/rules@chatpetsbot':
    text = '1. Не использовать клиентских ботов для кормления питомца! За это будут наказания.\n2. Не давать рекламу в списке выброшенных питомцев.'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['remove'])
def removee(m):
    if is_from_admin(m):
        try:
            lost.delete_one({'id': int(m.text.split(' ')[1])})
            bot.send_message(m.chat.id, "success")
        except:
            pass


@bot.message_handler(commands=['start'], func=lambda message: is_actual(message))
def startt(m):
    if m.from_user.id == m.chat.id:
        bot.send_message(m.chat.id, 'Здравствуй! /help для информации.')


@bot.message_handler(commands=['info'])
def info(m):
    text = ''
    if not is_from_admin(m):
        return

    for ids in chats.find({}):
        text += str(ids) + '\n\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['top'], func=lambda message: is_actual(message))
def top(m):
  if m.text.lower()=='/top' or m.text.lower()=='/top@chatpetsbot':
    db_pets = chats.find().sort('lvl', -1).limit(10)
    text = 'Топ-10 питомцев:\n\n'
    i = 1
    for doc in db_pets:
        text += str(i) + ' место: ' + pettoemoji(doc['type'])+doc['name'] + ' (' + str(doc['lvl']) + ' лвл)\n'
        i += 1

    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['help'], func=lambda message: is_actual(message))
def help(m):
  if m.text.lower()=='/help' or m.text.lower()=='/help@chatpetsbot':
    text = ''
    text += 'Чатовые питомцы питаются активностью юзеров. Чем больше вы общаетесь в чате, тем счастливее будет питомец! '
    text += 'Если долго не общаться, питомец начинает голодать и терять жизни. Назвать питомца можно командой /name\n'
    text += 'Для получения опыта необходимо иметь 85% сытости. Для получения бонусного опыта - 90% и 99% (за каждую отметку дается x опыта. То есть если у вас 90% сытости, вы получите (базовый_опыт + х), а если 99%, то (базовый_опыт + 2х).'
    bot.send_message(m.chat.id, text)


@bot.message_handler(func=lambda message: message.migrate_from_chat_id is not None, content_types=None)
def migrate(m):
    old_chat_id = m.migrate_from_chat_id
    new_chat_id = m.chat.id
    if chats.find_one({'id': old_chat_id}) is not None:
        chats.update_one({'id': old_chat_id}, {'$set': {'id': new_chat_id}})


@bot.message_handler(commands=['pogladit'])
def gladit(m):
    try:
        x = chats.find_one({'id': m.chat.id})
        if x is not None:
            bot.send_message(m.chat.id, m.from_user.first_name + ' погладил(а) ' + pettoemoji(x['type'])+x['name'] + '!')
        else:
            bot.send_message(m.chat.id, 'А гладить некого!')
    except:
        bot.send_message(admin_id, traceback.format_exc())

bot.message_handler(commands=['achievement_list'])
def achlist(m):
    text=''
    text+='1. За каждые 100 уровней даётся по 1 кубику, и так до 10000го.\n'
    text+='2. За сообщение от Дмитрия Исаева в вашем чате даётся 3 кубика!\n'
    text+='3. За актив в чате (сообщения от 10ти пользователей за минуту) даётся 3 кубика!\n'
    text+='В будущем я добавлю секретные ачивки (но вам об этом не скажу)! Список ачивок будет пополняться.'
    bot.send_message(m.chat.id, text)
        
        
@bot.message_handler(commands=['addexp'])
def addexp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'exp': int(m.text.split(' ')[1])}})
        except:
            pass



@bot.message_handler(commands=['addhunger'])
def addexp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'maxhunger': int(m.text.split(' ')[1]), 'hunger':int(m.text.split(' ')[1])}})
        except:
            pass

@bot.message_handler(commands=['addlvl'])
def addlvl(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'lvl': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['reboot'])
def addlvl(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$set': {'hunger': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['petstats'], func=lambda message: is_actual(message))
def petstats(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        bot.send_message(m.chat.id, 'Сначала питомца нужно завести (или подобрать с улицы).')
        return
    emoj=pettoemoji(animal['type'])
    text = ''
    text += emoj+'Имя: ' + animal['name'] + '\n'
    text += '🏅Уровень: ' + str(animal['lvl']) + '\n'
    text += '🔥Опыт: ' + str(animal['exp']) + '/' + str(nextlvl(animal)) + '\n'
    text += '♥Здоровье: ' + str(animal['hp']) + '/' + str(animal['maxhp']) + '\n'
    p = int(animal['hunger'] / animal['maxhunger'] * 100)
    text += '🍔Сытость: ' + str(animal['hunger']) + '/' + str(animal['maxhunger']) + ' (' + str(p) + '%)' + '\n'
    text += 'Нужно сытости для постоянного получения опыта: ' + str(int(animal['maxhunger'] * 0.85))
    bot.send_message(m.chat.id, text)

    
    
@bot.message_handler(commands=['losthorses'], func=lambda message: is_actual(message))
def losthorses(m):
    if lost.count_documents({'id': {'$exists': True}}) == 0:
        bot.send_message(m.chat.id, "На улице питомцев нет!")
        return

    text = 'Чтобы забрать питомца, введите команду /takeh id\n\n'
    for pet in lost.find({'id': {'$exists': True}}):
        text += pettoemoji(pet['type'])+str(pet['id']) + ': ' + pet['name'] + " (" + str(pet['lvl']) + ' лвл)' + '\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['takeh'], func=lambda message: is_actual(message))
def takeh(m):
    try:
        horse_id = int(m.text.split(' ')[1])
        if lost.find_one({'id': horse_id}) is None:
            bot.send_message(m.chat.id, "Питомец не существует!")
            return

        if chats.find_one({'id': m.chat.id}) is not None:
            bot.send_message(m.chat.id, "У вас уже есть питомец!")
            return

        take_horse(horse_id, m.chat.id)
        chats.update_one({'id': horse_id}, {'$set': {'id': m.chat.id}})
        bot.send_message(m.chat.id,
                         "Поздравляем, вы спасли питомца от голода! Следите за ним, чтобы он рос и не голодал!")
    except:
        pass


def unban(id):
    try:
        ban.remove(id)
    except:
        pass


@bot.message_handler(commands=['throwh'], func=lambda message: is_actual(message))
def throwh(m):
  if m.text.lower()=='/throwh' or m.text.lower()=='/throwh@chatpetsbot':
    if m.chat.id not in ban:
        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        ch=chat_admins.find_one({'id':m.chat.id})
        if ch==None:
            if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                    m) and m.from_user.id != m.chat.id:
                bot.send_message(m.chat.id, 'Только админ может делать это!')
                return
        else:
            if m.from_user.id not in ch['admins']:
                bot.send_message(m.chat.id, 'Только админ лошади может делать это! Выставить админов может создатель чата по команде: /set_admin. Убрать админа можно командой /remove_admin.')
                return
    
        if chats.find_one({'id': m.chat.id}) is None:
            bot.send_message(m.chat.id, "У вас даже лошади нет, а вы ее выкидывать собрались!")
            return
    
        if lose_horse(m.chat.id):
            ban.append(m.chat.id)
            t = threading.Timer(3600, unban, args=[m.chat.id])
            t.start()
            bot.send_message(m.chat.id,
                             "Вы выбросили питомца на улицу... Если его никто не подберет, он умрет от голода!")
        else:
            bot.send_message(m.chat.id,
                                 "На улице гуляет слишком много лошадей, поэтому, как только вы ее выкинули, лошадь украли цыгане!")
    else:
        bot.send_message(m.chat.id, 'Можно выгонять только одного питомца в час!')


@bot.message_handler(commands=['ban'])
def bannn(m):
    if is_from_admin(m):
        try:
            totalban.append(int(m.text.split(' ')[1]))
            bot.send_message(m.chat.id, 'Success')
        except:
            pass


@bot.message_handler(commands=['name'], func=lambda message: is_actual(message))
def name(m):
    try:
        if m.chat.id in totalban or m.from_user.id in totalban:
            bot.send_message(m.chat.id,
                             'Вам было запрещено менять имя питомца! Разбан через рандомное время (1 минута - 24 часа).')
            return

        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                m) and m.from_user.id != m.chat.id:
            bot.send_message(m.chat.id, 'Только админ может делать это!')
            return

        name = m.text.split('/name ')[1]

        if chats.find_one({'id': m.chat.id}) is None:
            return

        if len(name) > 50:
            bot.send_message(m.chat.id, "Максимальная длина имени - 50 символов!")
            return
        if len(name) < 2:
            bot.send_message(m.chat.id, "Минимальная длина имени - 2 символа!")
            return
        chats.update_one({'id': m.chat.id}, {'$set': {'name': name}})
        try:
            bot.send_message(admin_id,
                             str(m.from_user.id) + ' ' + m.from_user.first_name + ' (имя: ' + name + ')')
        except:
            pass
        bot.send_message(m.chat.id, 'Вы успешно сменили имя питомца на ' + name + '!')
    except:
        pass


    
@bot.message_handler(commands=['use_dice'])
def use_dice(m):
    alltypes=['parrot', 'cat', 'dog', 'bear', 'pig', 'hedgehog', 'octopus', 'turtle', 'crab', 'spider', 'bee', 'owl', 'boar', 'panda', 'cock', 'onehorn']
    chat=globalchats.find_one({'id':m.chat.id})
    if chat==None:
        return
    if chat['pet_access']>0:
        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                m) and m.from_user.id != m.chat.id:
            bot.send_message(m.chat.id, 'Только администратор может делать это!')
            return
        tt=random.choice(alltypes)
        globalchats.update_one({'id':m.chat.id},{'$inc':{'pet_access':-1}})
        if tt not in chat['avalaible_pets']:
            globalchats.update_one({'id':m.chat.id},{'$push':{'avalaible_pets':tt}})
        bot.send_message(m.chat.id, 'Кручу-верчу, питомца выбрать хочу...\n...\n...\n...\n...\n...\nПоздравляю! Вам достался питомец "*'+pettype(tt)+'*"!', parse_mode='markdown')
    else:
        bot.send_message(m.chat.id, 'У вас нет кубов! Зарабатывайте достижения для их получения!')
    
    
@bot.message_handler(commands=['chat_stats'])
def chatstats(m):
    x=globalchats.find_one({'id':m.chat.id})
    if x==None:
        return
    pts=''
    i=1
    for ids in x['avalaible_pets']:
        if i!=len(x['avalaible_pets']):
            pts+=pettype(ids)+', '
        else:
            pts+=pettype(ids)+';'
        i+=1
    lastpets=''
    for ids in x['saved_pets']:
        hr=x['saved_pets'][ids]
        lastpets+=pettoemoji(hr['type'])+hr['name']+': '+str(hr['lvl'])+'\n'
    text=''
    text+='Питомцы из прошлых сезонов: '+lastpets+'\n'
    text+='🎖Максимальный уровень лошади в этом чате: '+str(x['pet_maxlvl'])+';\n'
    text+='🌏Доступные типы питомцев: '+pts+'\n'
    text+='🎲Количество попыток для увеличения доступных типов (кубы): '+str(x['pet_access'])+' (использовать: /use_dice).'
    bot.send_message(m.chat.id, text)
    

@bot.message_handler(commands=['allinfo'])
def allinfo(m):
    if is_from_admin(m):
        text = str(chats.find_one({'id': m.chat.id}))
        bot.send_message(admin_id, text)


@bot.message_handler(commands=['igogo'])
def announce(m):
    if not is_from_admin(m):
        return

    text = m.text.replace('/igogo ', '', 1)
    chats_ids = chats.find({})
    i = 0
    for doc in chats_ids:
        try:
            bot.send_message(doc['id'], text)
            i += 1
        except:
            pass
    bot.send_message(m.chat.id, 'success')#"Сообщение успешно получило " + str(i) + '/' + str(chats.count_documents()) + " чатиков")


@bot.message_handler(commands=['secret'])
def cubeee(m):
    chat=globalchats.find_one({'id':m.chat.id})
    if chat!=None:
        if 'so easy' not in chat['achievements']:
            x=chats.find_one({'id':m.chat.id})
            if x!=None:
                if x['lvl']>=15:
                    globalchats.update_one({'id':m.chat.id},{'$push':{'a'+'c'+'h'+'i'+'evem'+'ents':'so easy'}})
                    globalchats.update_one({'id':m.chat.id},{'$inc':{'pet_access':2}})
                    bot.send_message(m.chat.id, 'Открыто достижение "Так просто?"! Награда: 2 куба.')
                else:
                    bot.send_message(m.chat.id, 'Для открытия этого достижения нужен минимум 15й уровень питомца!')
            else:
                bot.send_message(m.chat.id, 'Для открытия этого достижения нужен минимум 15й уровень питомца!')



@bot.message_handler(func=lambda message: not is_actual(message))
def skip_message(m):
    print('old message skipped')

def is_actual(m):
    return m.date + 120 > int(round(time.time()))


def createuser(user):
    return {
        'id':user.id,
        'name':user.first_name,
        'username':user.username,
        'now_elite':False
    }

@bot.message_handler(commands=['select_pet'])
def selectpett(m):
    chat=globalchats.find_one({'id':m.chat.id})
    if chat==None:
        return
    x=m.text.split(' ')
    if len(x)==2:
        pet=x[1]
        newpet=change_pet(pet)
        if newpet!=None:
            if chats.find_one({'id':m.chat.id})!=None:
                user = bot.get_chat_member(m.chat.id, m.from_user.id)
                if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                    m) and m.from_user.id != m.chat.id:
                    bot.send_message(m.chat.id, 'Только админ может делать это!')
                    return
                if newpet in chat['avalaible_pets']:
                    chats.update_one({'id':m.chat.id},{'$set':{'type':newpet}})
                    bot.send_message(m.chat.id, 'Вы успешшно сменили тип питомца на "'+pet+'"!')
                else:
                    bot.send_message(m.chat.id, 'Вам сейчас не доступен этот тип питомцев (или его просто не существует)!')
    else:
        bot.send_message(m.chat.id, 'Ошибка! Используйте формат\n/select_pet pet\nГде pet - доступный вам тип питомцев (посмотреть их можно в /chat_stats).')
    

def change_pet(pet):
    x=None
    pet=pet.lower()
    if pet=='лошадь':
        x='horse'
    if pet=='попугай':
        x= 'parrot'
    if pet=='кот':
        x= 'cat'
    if pet=='собака':
        x= 'dog'
    if pet=='медведь':
        x= 'bear'
    if pet=='свинка':
        x= 'pig'
    if pet=='ёж':
        x= 'hedgehog'
    if pet=='осьминог':
        x= 'octopus'
    if pet=='черепаха':
        x= 'turtle'
    if pet=='краб':
        x= 'crab'
    if pet=='паук':
        x= 'spider'
    if pet=='пчела':
        x= 'bee'
    if pet=='сова':
        x= 'owl'
    if pet=='кабан':
        x= 'boar'
    if pet=='панда':
        x='panda'
    if pet=='петух':
        x='cock'
    if pet=='единорог':
        x='onehorn'
    return x
    
    
@bot.message_handler(commands=['new_season'])
def new_season(m):
    if m.from_user.id=='aab':
        for ids in chats.find({}):
            x=globalchats.find_one({'id':ids['id']})
            if x==None:
                globalchats.insert_one(createglobalchat(ids['id']))
            globalchats.update_one({'id':ids['id']},{'$set':{'saved_pets.'+str(ids['id'])+'season1':ids}})
            globalchats.update_one({'id':ids['id']},{'$set':{'pet_maxlvl':ids['lvl']}}) 
    
        for ids in globalchats.find({}):
            globalchats.update_one({'id':ids['id']},{'$set':{'achievements':[]}})
        db_pets = chats.find().sort('lvl', -1).limit(10)
        
        for doc in db_pets:
            globalchats.update_one({'id':doc['id']},{'$inc':{'pet_access':3}})
        for ids in chats.find({}):
            try:
                bot.send_message(ids['id'], 'Начинается новый сезон! Все ваши текущие лошади добавлены вам в конюшню, но кормить их больше не нужно, и уровень у них больше не поднимется. Она останется у вас как память. Все чаты из топа получают 3 куба в подарок!')
            except:
                pass
        chats.remove({})
    

@bot.message_handler(commands=['refresh_lvl'])
def rrrlll(m):
    if m.from_user.id==441399484:
        
        globalchats.update_many({},{'$set':{'avalaible_pets':['horse'], 'pet_access':2, 'achievements':[]}})


@bot.message_handler(content_types=['text'])
def messages(m):
  if m.chat.id not in block:
    if users.find_one({'id':m.from_user.id})==None:
        users.insert_one(createuser(m.from_user))
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        return
    if globalchats.find_one({'id':m.chat.id})==None:
        globalchats.insert_one(createglobalchat(m.chat.id))
    if m.from_user.id not in animal['lastminutefeed']:
        chats.update_one({'id': m.chat.id}, {'$push': {'lastminutefeed': m.from_user.id}})
    if m.from_user.id not in animal['lvlupers'] and users.find_one({'id':m.from_user.id})['now_elite']==True:
        chats.update_one({'id': m.chat.id}, {'$push': {'lvlupers': m.from_user.id}})
    if m.chat.title != animal['title']:
        chats.update_one({'id': m.chat.id}, {'$set': {'title': m.chat.title}})
    try:
        if animal['spying'] is not None:
            bot.send_message(animal['spying'], '(Name: ' + m.from_user.first_name + ') (id: ' + str(
                m.from_user.id) + ') (text: ' + m.text + ')')
    except:
        pass


    
def createglobalchat(id):
    return {
        'id':id,
        'avalaible_pets':['horse'],
        'saved_pets':{},
        'pet_access':0,
        'pet_maxlvl':0,
        'achievements':[]
    }
    
    
def createpet(id, typee='horse', name='Без имени'):
    return {
        'id': id,
        'type': typee,
        'name': name,
        'lvl': 1,
        'exp': 0,
        'hp': 100,
        'maxhp': 100,
        'lastminutefeed': [],  # Список юзеров, которые проявляли актив в последнюю минуту
        'hunger': 100,
        'maxhunger': 100,
        'title': None,  # Имя чата
        'stats': {},  # Статы игроков: кто сколько кормит лошадь итд
        'spying': None,
        'send_lvlup':True,
        'lvlupers':[]
    }


def medit(message_text, chat_id, message_id, reply_markup=None, parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text, reply_markup=reply_markup,
                                 parse_mode=parse_mode)


def nextlvl(pet):
    return pet['lvl'] * (4 + pet['lvl'] * 100)


def check_hunger(pet, horse_lost):
    hunger = pet['hunger']
    maxhunger = pet['maxhunger']
    exp = pet['exp']
    lvl = pet['lvl']
    lastminutefeed = pet['lastminutefeed']

    # если кто-то писал в чат, прибавить кол-во еды равное кол-во покормивших в эту минуту * 2
    gchat=globalchats.find_one({'id':pet['id']})
    if gchat!=None:
        if len(lastminutefeed)>=10 and '10 users in one minute!' not in gchat['achievements']:
            globalchats.update_one({'id':pet['id']},{'$push':{'achievements':'10 users in one minute!'}})
            globalchats.update_one({'id':pet['id']},{'$inc':{'pet_access':3}})
            bot.send_message(pet['id'], 'Заработано достижение: супер-актив! Получено: 3 куба (/chat_stats).')
            
    if gchat!=None:
        if 86190439 in lastminutefeed and 'dmitriy isaev' not in gchat['achievements']:
            globalchats.update_one({'id':pet['id']},{'$push':{'achievements':'dmitriy isaev'}})
            globalchats.update_one({'id':pet['id']},{'$inc':{'pet_access':3}})
            bot.send_message(pet['id'], 'Заработано достижение: Дмитрий Исаев! Получено: 3 куба (/chat_stats).')
        
        
        
    if len(lastminutefeed) > 0:
        hunger += len(lastminutefeed) * 2
        lastminutefeed = []
        if hunger > maxhunger:
            hunger = maxhunger

    # если лошадь накормлена на 85% и выше, прибавить опыта
    h = hunger / maxhunger * 100
    if h >= 85:
        exp += int(lvl * (2 + (random.randint(-100, 100) / 100)))
    if h >= 90:
        exp += lvl
    if h >= 99:
        exp += lvl
    if exp >= nextlvl(pet):
        lvl += 1
        maxhunger += 15
        if not horse_lost:
            send_message(pet['id'], 'Уровень вашего питомца повышен! Максимальный запас сытости увеличен на 15!', act='lvlup')
     
    ii=100
    if gchat!=None:
        while ii<=10000:
            if lvl>=ii and 'lvl '+str(ii) not in gchat['achievements']:
                globalchats.update_one({'id':pet['id']},{'$push':{'achievements':'lvl '+str(ii)}})
                globalchats.update_one({'id':pet['id']},{'$inc':{'pet_access':1}})
                bot.send_message(pet['id'], 'Заработано достижение: '+str(ii)+' лвл! Получено: 1 куб (/chat_stats).')
            ii+=100

    commit = {'hunger': hunger, 'maxhunger': maxhunger, 'exp': exp, 'lvl': lvl, 'lastminutefeed': lastminutefeed}
    if not horse_lost:
        chats.update_one({'id': pet['id']}, {'$set': commit})
    else:
        lost.update_one({'id': pet['id']}, {'$set': commit})


def check_hp(pet, horse_lost):
    hunger = pet['hunger'] - random.randint(3, 9)
    maxhunger = pet['maxhunger']  # const
    hp = pet['hp']
    maxhp = pet['maxhp']  # const

    if hunger <= 0:
        hunger = 0
        if not horse_lost:
            send_message(pet['id'], 'Ваш питомец СИЛЬНО голодает! Осталось ' + str(
                hunger) + ' сытости! СРОЧНО нужен актив в чат!')
        hp -= random.randint(9, 15)

    elif hunger / maxhunger * 100 <= 30:
        if not horse_lost:
            send_message(pet['id'], 'Ваш питомец голодает! Осталось всего ' + str(
                hunger) + ' сытости! Срочно нужен актив в чат!')
        hp -= random.randint(9, 15)

    elif hunger / maxhunger * 100 >= 75 and hp < maxhp:
        hp += random.randint(3, 9)
        if hp > maxhp:
            hp = maxhp

    if hp <= 0:
        total = lost.find_one({})['amount']
        total += 1
        lost.update_one({'amount': {'$exists': True}}, {'$inc': {'amount': 1}})
        if not horse_lost:
            chats.delete_one({'id': pet['id']})
            try:
                bot.send_message(pet['id'],
                                 'Вашему питомцу плохо в вашем чате, ему не хватает питания. Поэтому я забираю его, чтобы он не умер.\n' +
                                 'Количество лошадей, которых мне пришлось забрать (во всех чатах): ' + str(total))
            except:
                pass
        else:
            lost.delete_one({'id': pet['id']})

    else:
        commit = {'hunger': hunger, 'hp': hp}
        if not horse_lost:
            chats.update_one({'id': pet['id']}, {'$set': commit})
        else:
            lost.update_one({'id': pet['id']}, {'$set': commit})


def check_all_pets_hunger():
    for pet in lost.find({'id': {'$exists': True}}):
        check_hunger(pet, True)
    for pet in chats.find({}):
        check_hunger(pet, False)
    threading.Timer(60, check_all_pets_hunger).start()
    
def check_all_pets_lvlup():
    for pet in chats.find({}):
        check_lvlup(pet)
    chats.update_many({},{'$set':{'lvlupers':[]}})
    threading.Timer(900, check_all_pets_lvlup).start()


def check_all_pets_hp():
    for pet in lost.find({'id': {'$exists': True}}):
        check_hp(pet, True)
    for pet in chats.find({}):
        check_hp(pet, False)
    threading.Timer(1800, check_all_pets_hp).start()

    
def check_lvlup(pet):
    lvl=0
    for ids in pet['lvlupers']:
        lvl+=1
    if lvl>0:
        chats.update_one({'id':pet['id']},{'$inc':{'lvl':lvl, 'maxhunger':lvl*15, 'hunger':lvl*15}})
        lvvl=chats.find_one({'id':pet['id']})['lvl']
        chats.update_one({'id':pet['id']},{'$set':{'exp':nextlvl({'lvl':lvvl-1})}})
        if pet['send_lvlup']==True:
            bot.send_message(pet['id'], '"Друзья животных" в вашем чате подняли уровень лошади на '+str(lvl)+'!')
    

def pettoemoji(pet):
    if pet=='horse':
        return '🐴'
    if pet=='parrot':
        return '🦜'
    if pet=='cat':
        return '🐱'
    if pet=='dog':
        return '🐶'
    if pet=='octopus':
        return '🐙'
    if pet=='turtle':
        return '🐢'
    if pet=='hedgehog':
        return '🦔'
    if pet=='pig':
        return '🐷'
    if pet=='bear':
        return '🐻'
    if pet=='crab':
        return '🦀'
    if pet=='bee':
        return '🐝'
    if pet=='spider':
        return '🕷'
    if pet=='boar':
        return '🐗'
    if pet=='owl':
        return '🦉'
    if pet=='panda':
        return '🐼'
    if pet=='cock':
        return '🐓'
    if pet=='onehorn':
        return '🦄'
    
    
    
def pettype(pet):
    t='не определено'
    if pet=='horse':
        return 'лошадь'
    if pet=='parrot':
        return 'попугай'
    if pet=='cat':
        return 'кот'
    if pet=='dog':
        return 'собака'
    if pet=='bear':
        return 'медведь'
    if pet=='pig':
        return 'свинка'
    if pet=='hedgehog':
        return 'ёж'
    if pet=='octopus':
        return 'осьминог'
    if pet=='turtle':
        return 'черепаха'
    if pet=='crab':
        return 'краб'
    if pet=='spider':
        return 'паук'
    if pet=='bee':
        return 'пчела'
    if pet=='owl':
        return 'сова'
    if pet=='boar':
        return 'кабан'
    if pet=='panda':
        return 'панда'
    if pet=='cock':
        return 'петух'
    if pet=='onehorn':
        return 'единорог'
    return t
    

def send_message(chat_id, text, act=None):  # использовать только чтобы проверить что лошадь все еще в чате
    h=chats.find_one({'id':chat_id})
    try:
        if act==None:
            bot.send_message(chat_id, text)
        else:
            if h['send_lvlup']==True:
                bot.send_message(chat_id, text)
    except:
        if h['hunger']/h['maxhunger']*100<=30:
            lose_horse(chat_id)


def lose_horse(chat_id):  # returns True on success
    pet = chats.find_one({'id': chat_id})
    chats.delete_one({'id': chat_id})

    lost.insert_one(pet)
    horse_id = lost.count_documents({'id': {'$exists': True}})
    while lost.find_one({'id': horse_id}) is not None:
        horse_id += 1
    lost.update_one({'id': chat_id}, {'$set': {'id': horse_id}})
    lost.update_one({'id': horse_id}, {'$set': {'type':'horse'}})
    return True


def take_horse(horse_id, new_chat_id):
    lost.update_one({'id': horse_id}, {'$set': {'id': new_chat_id}})
    pet = lost.find_one({'id': new_chat_id})
    lost.delete_one({'id': new_chat_id})
    chats.insert_one(pet)

    
def check_newday():
    t=threading.Timer(60, check_newday)
    t.start()
    x=time.ctime()
    x=x.split(" ")
    month=0
    year=0
    ind=0
    num=0
    for ids in x:
       for idss in ids:
          if idss==':':
             tru=ids
             ind=num
       num+=1
    day=x[ind-1]
    month=x[1]
    year=x[ind+1]
    x=tru 
    x=x.split(":")  
    y=int(x[1])    # минуты
    x=int(x[0])+3  # часы (+3, потому что heroku в Великобритании)
    z=time.ctime()
 
 
    if y==0 and x==24:
        users.update_many({},{'$set':{'now_elite':False}})
        allist=users.find({})
        alls=[]
        for ids in allist:
            alls.append(ids)
        amount=int(len(alls)/10)
        alreadyelite=[]
        while len(alreadyelite)<amount:
            us=random.choice(alls)
            if us['id'] not in alreadyelite:
                alreadyelite.append(us['id'])
        for ids in alreadyelite:
            users.update_one({'id':ids['id']},{'$set':{'now_elite':True}})
        bot.send_message(441399484, str(amount))
        
       
    

def is_from_admin(m):
    return m.from_user.id == admin_id


check_all_pets_hunger()
check_all_pets_hp()
check_newday()
check_all_pets_lvlup()

print('7777')
bot.polling(none_stop=True, timeout=600)
