
import cookiewars
import threading

def poll(b):
    try:
        b.polling(none_stop = True)
    except:
      try:
        b.send_message(441399484, traceback.format_exc())
        b.send_message(441399484, 'Бот упал!')
        #herokuapp = heroku3.from_key(os.environ['herokukey']).apps()['chatpets']
        #herokuapp.restart()
      except:
        pass
try:
    cookiewars.bot.send_message(441399484, 'launched')
except:
    pass

import heroku3
heroku_conn = heroku3.from_key(os.environ['apikey'])

app = heroku_conn.apps()['cookiessswars']

def restartapp():
    app.restart()

try:
    cookiewars.bot.polling(none_stop = True)
except:
    restartapp()

def polll(x):
  try:
    x()
  except:
    try:
        bot.send_message(441399484, traceback.format_exc())
    except:
        pass

print('7777')





