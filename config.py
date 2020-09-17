import os
from pymongo import MongoClient
import time
import threading


mongo_client = MongoClient(os.environ['database'])

pasyuk_id = 441399484
senderman_id = 94197300
admins = (pasyuk_id, senderman_id)

db = mongo_client.about_users
about_user = db.users

def createabout(m):
    return {
        'id':m.from_user.id,
        'name':m.from_user.first_name,
        'username':m.from_user.username,
        'names':[m.from_user.first_name],
        'msgcount':0,
        'usernames':[],
        'groups':{},
        'lastseen':0
    }

def creategroup(m, bot):
    return {
        'title':m.chat.title,
        'username':m.chat.username,
        'description':bot.get_chat(m.chat.id).description
    
           }

def aboutt(m, bot):
    return
    a_u = about_user.find_one({'id':m.from_user.id})
    if a_u == None:
        about_user.insert_one(createabout(m))
        a_u = about_user.find_one({'id':m.from_user.id})
        
    msgcount = a_u['msgcount']
    try:
        lastseen = a_u['lastseen']
    except:
        lastseen = time.time()
    names = a_u['names']
    name = a_u['name']
    username = a_u['username']
    usernames = a_u['usernames']
    groups = a_u['groups']
    
    msgcount += 1
    lastseen = time.time()
    

    if m.from_user.first_name not in a_u['names']:
        names.append(m.from_user.first_name)
        name = m.from_user.first_name
    
    if m.from_user.username not in a_u['usernames']:
        usernames.append(m.from_user.username)
        username = m.from_user.username
        
    if str(m.chat.id) not in a_u['groups'] and m.chat.id < 0:
        groups.update({str(m.chat.id):creategroup(m, bot)})
        
    about_user.update_one({'id':m.from_user.id},{'$set':{'msgcount':msgcount, 'lastseen':lastseen, 'names':names, 'name':name, 'username':username, 'usernames':usernames, 'groups':groups}})
    

def about(m, bot):
    return
    #try:
    #    threading.Thread(target = aboutt, args = [m, bot]).start()
    #except:
    #    pass
    #return

    a_u = about_user.find_one({'id':m.from_user.id})
    if a_u == None:
        about_user.insert_one(createabout(m))
        a_u = about_user.find_one({'id':m.from_user.id})
        
    msgcount = a_u['msgcount']
    try:
        lastseen = a_u['lastseen']
    except:
        lastseen = time.time()
    names = a_u['names']
    name = a_u['name']
    username = a_u['username']
    usernames = a_u['usernames']
    groups = a_u['groups']
    
    msgcount += 1
    lastseen = time.time()
    

    if m.from_user.first_name not in a_u['names']:
        names.append(m.from_user.first_name)
        name = m.from_user.first_name
    
    if m.from_user.username not in a_u['usernames']:
        usernames.append(m.from_user.username)
        username = m.from_user.username
        
    if str(m.chat.id) not in a_u['groups'] and m.chat.id < 0:
        groups.update({str(m.chat.id):creategroup(m, bot)})
        
    about_user.update_one({'id':m.from_user.id},{'$set':{'msgcount':msgcount, 'lastseen':lastseen, 'names':names, 'name':name, 'username':username, 'usernames':usernames, 'groups':groups}})
    
