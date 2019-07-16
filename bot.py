# -*- coding: utf-8 -*-
import os
import random
import threading
import traceback

import telebot
from pymongo import MongoClient

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

client = MongoClient(os.environ['database'])
db = client.chatpets
users = db.users
chats = db.chats
lost = db.lost

ban = []
totalban = [243153864]

if lost.find_one({'amount': {'$exists': True}}) is None:
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


@bot.message_handler(commands=['getids'])
def idssssss(m):
    if m.from_user.id == 441399484:
        text = ''
        for h in lost.find({}):
            if 'id' in h:
                text += str(h['id']) + ' ' + h['name'] + '\n'
        bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['remove'])
def removee(m):
    if is_from_admin(m):
        try:
            lost.delete_one({'id': int(m.text.split(' ')[1])})
            bot.send_message(m.chat.id, "success")
        except:
            pass


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
    db_pets = chats.find({})
    horses = []
    for doc in db_pets:
        horses.append(doc)

    text = 'Топ-10 лошадей:\n\n'
    for i in range(1, 11):
        current_pet = None
        current_lvl = 0
        for pet in horses:
            if pet['lvl'] >= current_lvl:
                current_lvl = pet['lvl']
                current_pet = pet

        if current_pet is None:
            break
        horses.remove(current_pet)
        text += str(i) + ' место: ' + current_pet['name'] + ' (' + str(current_pet['lvl']) + ' лвл)\n'

    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['help'])
def help(m):
    text = ''
    text += 'Чатовые питомцы питаются активностью юзеров. Чем больше вы общаетесь в чате, тем счастливее будет питомец! '
    text += 'Если долго не общаться, питомец начинает голодать и терять жизни. Назвать питомца можно командой /name!'
    bot.send_message(m.chat.id, text)


@bot.message_handler(func=lambda message: message.migrate_from_chat_id is not None, content_types=None)
def migrate(m):
    old_chat_id = m.migrate_from_chat_id
    new_chat_id = m.chat.id
    if chats.find_one({'id': old_chat_id}) is not None:
        chats.update_one({'id': old_chat_id}, {'$set': {'id': new_chat_id}})


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


@bot.message_handler(commands=['losthorses'])
def losthorses(m):
    if lost.count_documents({'id': {'$exists': True}}) == 0:
        bot.send_message(m.chat.id, "На улице лошадей нет!")
        return

    text = 'Чтобы забрать лошадь, введите команду /takeh id\n\n'
    for pet in lost.find({'id': {'$exists': True}}):
        text += str(pet['id']) + ': ' + pet['name'] + " (" + str(pet['lvl']) + ' лвл)' + '\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['takeh'])
def takeh(m):
    try:
        horse_id = int(m.text.split(' ')[1])
        if lost.find_one({'id': horse_id}) is None:
            bot.send_message(m.chat.id, "Лошадь не существует!")
            return

        if chats.find_one({'id': m.chat.id}) is not None:
            bot.send_message(m.chat.id, "У вас уже есть лошадь!")
            return

        take_horse(horse_id, m.chat.id)
        chats.update_one({'id': horse_id}, {'$set': {'id': m.chat.id}})
        bot.send_message(m.chat.id,
                         "Поздравляем, вы спасли лошадь от голода! Следите за ней, чтобы она росла и не умирала!")
    except:
        pass


def unban(id):
    try:
        ban.remove(id)
    except:
        pass


@bot.message_handler(commands=['throwh'])
def throwh(m):
    if m.chat.id not in ban:
        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                m) and m.from_user.id != m.chat.id:
            bot.send_message(m.chat.id, 'Только админ может делать это!')
            return

        if chats.find_one({'id': m.chat.id}) is None:
            bot.send_message(m.chat.id, "У вас даже лошади нет, а вы ее выкидывать собрались :(")
            return

        if lose_horse(m.chat.id):
            ban.append(m.chat.id)
            t = threading.Timer(3600, unban, args=[m.chat.id])
            t.start()
            bot.send_message(m.chat.id,
                             "Вы выбросили лошадь на улицу... Если ее никто не подберет, она умрет от голода!")
        else:
            bot.send_message(m.chat.id,
                             "На улице гуляет слишком много лошадей, поэтому, как только вы ее выкинули, лошадь украли цыгане!")
    else:
        bot.send_message(m.chat.id, 'Можно выгонять только одну лошадь в час!')


@bot.message_handler(commands=['ban'])
def bannn(m):
    if m.from_user.id == 441399484:
        try:
            totalban.append(int(m.text.split(' ')[1]))
            bot.send_message(m.chat.id, 'Success')
        except:
            pass


@bot.message_handler(commands=['name'])
def name(m):
  try:
    if m.chat.id in totalban and m.from_user.id not in totalban:
        bot.send_message(m.chat.id,
                         'Вам было запрещено менять имя лошади! Разбан через рандомное время (1 минута - 24 часа).')
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
    bot.send_message(m.chat.id, 'Вы успешно сменили имя лошади на ' + name + '!')
  except:
    bot.send_message(441399484, traceback.format_exc())

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
    bot.send_message(m.chat.id, "Сообщение успешно получило " + str(i) + " чатиков")


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


def check_hunger(pet, horse_lost):
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
    h = hunger / maxhunger * 100
    if h >= 85:
        exp += int(lvl * (2 + (random.randint(-100, 100) / 100)))
    if h >= 90:
        exp+=lvl
    if h >= 99:
        exp += lvl
    if exp >= nextlvl(pet):
        lvl += 1
        maxhunger += 15
        if not horse_lost:
            send_message(pet['id'], 'Уровень вашей лошади повышен! Максимальный запас сытости увеличен на 15!')

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
            send_message(pet['id'], 'Ваша лошадь СИЛЬНО голодает! Осталось ' + str(
                hunger) + ' сытости! СРОЧНО нужен актив в чат!')
        hp -= random.randint(9, 15)

    elif hunger / maxhunger * 100 <= 30:
        if not horse_lost:
            send_message(pet['id'], 'Ваша лошадь голодает! Осталось всего ' + str(
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
                                 'Вашей лошади плохо в вашем чате, ей не хватает питания. Поэтому я забираю её, чтобы не откинула копыта.\n' +
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
    for pet in chats.find({}):
        check_hunger(pet, False)
    for pet in lost.find({'id': {'$exists': True}}):
        check_hunger(pet, True)
    threading.Timer(60, check_all_pets_hunger).start()


def check_all_pets_hp():
    for pet in chats.find({}):
        check_hp(pet, False)
    for pet in lost.find({'id': {'$exists': True}}):
        check_hp(pet, True)
    threading.Timer(1800, check_all_pets_hp).start()


def send_message(chat_id, text):  # использовать только чтобы проверить что лошадь все еще в чате
    try:
        bot.send_message(chat_id, text)
    except:
        lose_horse(chat_id)


def lose_horse(chat_id):  # returns True on success
    pet = chats.find_one({'id': chat_id})
    chats.delete_one({'id': chat_id})

    lost.insert_one(pet)
    horse_id = lost.count_documents({'id': {'$exists': True}})
    while lost.find_one({'id': horse_id}) is not None:
        horse_id += 1
    lost.update_one({'id': chat_id}, {'$set': {'id': horse_id}})
    return True


def take_horse(horse_id, new_chat_id):
    lost.update_one({'id': horse_id}, {'$set': {'id': new_chat_id}})
    pet = lost.find_one({'id': new_chat_id})
    lost.delete_one({'id': new_chat_id})
    chats.insert_one(pet)


def is_from_admin(m):
    return m.from_user.id == admin_id


check_all_pets_hunger()
check_all_pets_hp()

print('7777')
bot.polling(none_stop=True, timeout=600)
