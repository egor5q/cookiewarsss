# -*- coding: utf-8 -*-
import os
import random
import threading

import telebot
from pymongo import MongoClient

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

client = MongoClient(os.environ['database'])
db = client.chatpets
users = db.users
chats = db.chats
lost = db.lost

if lost.find_one({}) is None:
    lost.insert_one({'amount': 0})

botname = 'Chatpetsbot'
admin_id = 441399484


@bot.message_handler(commands=['growpet'])
def grow(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        chats.insert_one(createpet(m.chat.id))
        bot.send_message(m.chat.id,
                         'Поздравляю! Вы завели лошадь! О том, как за ней ухаживать, можно прочитать в /help.')


@bot.message_handler(commands=['start'])
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


@bot.message_handler(commands=['top'])
def top(m):
    best_pets = []

    for i in range(1, 11):
        chat = None
        nextt = 0
        for ids in chats.find({}):
            if ids['lvl'] > nextt and ids not in best_pets:
                nextt = ids['lvl']
                chat = ids
        if chat is not None:
            best_pets.append(chat)

    text = 'Топ-10 лошадей:\n\n'
    i = 1
    for ids in best_pets:
        text += str(i) + ' место: ' + ids['name'] + ' (' + str(ids['lvl']) + ' лвл)\n'
        i += 1
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['help'])
def help(m):
    if m.text != "/help@" + botname:
        return

    text = ''
    text += 'Чатовые питомцы питаются активностью юзеров. Чем больше вы общаетесь в чате, тем счастливее будет питомец! '
    text += 'Если долго не общаться, питомец начинает голодать и терять жизни. Назвать питомца можно командой /name!'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['addexp'])
def addexp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'exp': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['addlvl'])
def addlvl(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'lvl': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['petstats'])
def petstats(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        return

    text = ''
    text += '🐴Имя: ' + animal['name'] + '\n'
    text += '🏅Уровень: ' + str(animal['lvl']) + '\n'
    text += '🔥Опыт: ' + str(animal['exp']) + '/' + str(nextlvl(animal)) + '\n'
    text += '♥Здоровье: ' + str(animal['hp']) + '/' + str(animal['maxhp']) + '\n'
    text += '🍔Сытость: ' + str(animal['hunger']) + '/' + str(animal['maxhunger']) + '\n'
    text += 'Нужно сытости для постоянного получения опыта: ' + str(int(animal['maxhunger'] * 0.85))
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['name'])
def name(m):
    try:
        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        if user.status == 'creator' or user.status == 'administrator' or m.from_user.id == 441399484 or m.from_user.id == m.chat.id:
            name = m.text.split('/name ')[1]
            if chats.find_one({'id': m.chat.id}) is not None:
                chats.update_one({'id': m.chat.id}, {'$set': {'name': name}})
                bot.send_message(m.chat.id, 'Вы успешно сменили имя лошади на ' + name + '!')
        else:
            bot.send_message(m.chat.id, 'Только админ может делать это!')
    except:
        pass


@bot.message_handler(commands=['allinfo'])
def allinfo(m):
    if is_from_admin(m):
        text = str(chats.find_one({'id': m.chat.id}))
        bot.send_message(441399484, text)


@bot.message_handler(content_types=['text'])
def messages(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        return

    if m.from_user.id not in animal['lastminutefeed']:
        chats.update_one({'id': m.chat.id}, {'$push': {'lastminutefeed': m.from_user.id}})


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
        'stats': {}  # Статы игроков: кто сколько кормит лошадь итд
    }


def medit(message_text, chat_id, message_id, reply_markup=None, parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text, reply_markup=reply_markup,
                                 parse_mode=parse_mode)


def nextlvl(pet):
    return pet['lvl'] * (4 + pet['lvl'] * 100)


def check1():
    for pet in chats.find({}):
        hunger = pet['hunger']
        maxhunger = pet['maxhunger']
        exp = pet['exp']
        lvl = pet['lvl']
        lastminutefeed = pet['lastminutefeed']

        # если кто-то писал в чат, прибавить кол-во еды равное кол-во покормивших в эту минуту * 2
        if len(lastminutefeed) > 0:
            hunger += len(lastminutefeed) * 2
            lastminutefeed = []
            if hunger > maxhunger:
                hunger = maxhunger

        # если лошадь накормлена на 85% и выше, прибавить опыта
        if hunger / maxhunger * 100 >= 85:
            exp += int(lvl * (2 + (random.randint(-100, 100) / 100)))

        if exp >= nextlvl(pet):
            lvl += 1
            maxhunger += 15
            try:
                bot.send_message(pet['id'], 'Уровень вашей лошади повышен! Максимальный запас сытости увеличен на 15!')
            except:
                pass

        commit = {'hunger': hunger, 'maxhunger': maxhunger, 'exp': exp, 'lvl': lvl, 'lastminutefeed': lastminutefeed}
        chats.update_one({'id': pet['id']}, {'$set': commit})

    t = threading.Timer(60, check1)
    t.start()


def check10():
    t = threading.Timer(1800, check10)
    t.start()
    for pet in chats.find({}):
        hunger = pet['hunger'] - random.randint(2, 6)
        maxhunger = pet['maxhunger']  # const
        hp = pet['hp']
        maxhp = pet['maxhp']  # const

        if hunger <= 0:
            hunger = 0
            try:
                bot.send_message(pet['id'], 'Ваша лошадь СИЛЬНО голодает! Осталось ' + str(
                    hunger) + ' сытости! СРОЧНО нужен актив в чат!')
            except:
                pass
            hp -= random.randint(9, 15)

        elif hunger / maxhunger * 100 <= 30:
            try:
                bot.send_message(pet['id'], 'Ваша лошадь голодает! Осталось всего ' + str(
                    hunger) + ' сытости! Срочно нужен актив в чат!')
            except:
                pass
            hp -= random.randint(9, 15)

        elif hunger / maxhunger * 100 >= 75 and hp < maxhp:
            hp += random.randint(3, 9)
            if hp > maxhp:
                hp = maxhp

        commit = {'hunger': hunger, 'hp': hp}
        chats.update_one({'id': pet['id']}, {'$set': commit})

        if hp <= 0:
            total = lost.find_one({})['amount']
            total += 1
            lost.update_one({}, {'$inc': {'amount': 1}})
            chats.remove({'id': pet['id']})
        try:
            bot.send_message(pet['id'],
                             'Вашей лошади плохо в вашем чате, ей не хватает питания. Поэтому я забираю её, чтобы не откинула копыта.\n' +
                             'Количество лошадей, которых мне пришлось забрать (во всех чатах): ' + str(total))
        except:
            pass


def is_from_admin(m):
    return m.from_user.id == admin_id


check1()
check10()

print('7777')
bot.polling(none_stop=True, timeout=600)
