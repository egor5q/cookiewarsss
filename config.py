import os
from pymongo import MongoClient

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
        'groups':{}
    }

def creategroup(m, bot):
    return {
        'title':m.chat.title,
        'username':m.chat.username,
        'description':bot.get_chat(m.chat.id).description
    
           }

def about(m, bot):

    a_u = about_user.find_one({'id':m.from_user.id})
    if a_u == None:
        about_user.insert_one(createabout(m))
        a_u = about_user.find_one({'id':m.from_user.id})
    about_user.update_one({'id':m.from_user.id},{'$inc':{'msgcount':1}})
    if m.from_user.first_name not in a_u['names']:
        about_user.update_one({'id':m.from_user.id},{'$push':{'names':m.from_user.first_name}})
        about_user.update_one({'id':m.from_user.id},{'$set':{'name':m.from_user.first_name}})
    
    if m.from_user.username not in a_u['usernames']:
        about_user.update_one({'id':m.from_user.id},{'$push':{'usernames':m.from_user.username}})
        about_user.update_one({'id':m.from_user.id},{'$set':{'username':m.from_user.username}})
        
    if str(m.chat.id) not in a_u['groups'] and m.chat.id < 0:
        about_user.update_one({'id':m.from_user.id},{'$set':{'groups.'+str(m.chat.id):creategroup(m, bot)}})
