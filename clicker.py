import asyncio
import js2py
import requests
import os
from telethon.sync import TelegramClient
from telethon import events
from telethon.sync import functions, types, events
from urllib.parse import unquote
import aiocron
import base64
import random
import time
import json
from threading import Thread
# -----------
api_id = 8086441
api_hash = '2a305482a93b5a762d2acd4be90dd00f'

client = TelegramClient('bot', api_id, api_hash)
client.start()

db = {
    'click': 'off'
}
admin = 6135970338 # Admin user id

print("Client is Ready ;)")
# -----------


class clicker:
    def __init__(self, client:TelegramClient) -> None:
        self.session = requests.Session()
        self.session.headers = {
            "accept": "application/json",
            "Accept-Language":"en,en-US;q=0.9",
            "Connection":"keep-alive",
            "Host": "clicker-api.joincommunity.xyz",
            "Origin": "https://clicker.joincommunity.xyz",
            "Referer": "https://clicker.joincommunity.xyz/",
            "X-Requested-With": "org.telegram.messenger.web",
            "auth":"1",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
        }
        
        self.client = client
        self.webviewApp = client(
            functions.messages.RequestWebViewRequest(
                peer='notcoin_bot',
                bot='notcoin_bot',
                platform='android',
                from_bot_menu=False,
                url='https://clicker.joincommunity.xyz/clicker',
            )
        )
        self.webAppData = self.generateAuthToken()
        print(self.webviewApp)
        self.mining_started = False
        self.startTime = time.time()
        self.checkTasksTime = 0
    
    def generateAuthToken(self):
        webData = self.webviewApp.url.split('/clicker#tgWebAppData=')[1].replace("%3D","=").split('&tgWebAppVersion=')[0].replace("%26","&")
        user = webData.split("&user=")[1].split("&auth")[0]
        webData = webData.replace(user, unquote(user))
        data = {
            'webAppData': webData
        }
        self.session.headers['content-length'] = str(len(json.dumps(data)))
        authTK = self.session.post(
            "https://clicker-api.joincommunity.xyz/auth/webapp-session",
            json=data
        ).json()['data']['accessToken']
        self.session.headers['Authorization'] = f'Bearer {authTK}'
        return webData
    
    def notCoins(self, _c, _h):
        data = {
            'count': _c,
            'hash': _h,
            'webAppData': self.webAppData
        }
        self.session.headers['content-length'] = str(len(json.dumps(data)))
        try:
            return self.session.post("https://clicker-api.joincommunity.xyz/clicker/core/click",json=data).json()
        except:
            return False
    
    def activeFullEnergy(self):
        data = {
            'webAppData': self.webAppData
        }
        try:
            r = self.session.get('https://clicker-api.joincommunity.xyz/clicker/task/3', json=data)
            return r.json().get('ok')
        except:
            return False
    
    def activate_turbo(self):
        data = {
            'webAppData': self.webAppData
        }
        try:
            r = self.session.get('https://clicker-api.joincommunity.xyz/clicker/core/active-turbo', json=data)
            return r.json()['data'][0].get('multiple', 1)
        except:
            return False
    
    def get_free_buffs_data(self):
        max_turbo_times: int = 3
        max_full_energy_times: int = 3

        turbo_times_count: int = 0
        full_energy_times_count: int = 0
        
        data = {
            'webAppData': self.webAppData
        }
        try:
            self.session.headers['content-length'] = str(len(json.dumps(data)))
            r = self.session.get('https://clicker-api.joincommunity.xyz/clicker/task/combine-completed', json=data)
            print(r.json())
            for current_buff in r.json('data'):
                match current_buff['taskId']:
                    case 2:
                        # Full Energy!
                        max_full_energy_times: int = current_buff['task']['max']
                        if current_buff['task']['status'] == 'active':
                                full_energy_times_count += 1
                    
                    case 3:
                        max_turbo_times: int = current_buff['task']['max']

                        if current_buff['task']['status'] == 'active':
                            turbo_times_count += 1
            
            return max_turbo_times > turbo_times_count, max_full_energy_times > full_energy_times_count
        except:
            return False, False
    
    def genrateHash(self, _hash):
        def _run_js(string):
            if string == "document.querySelectorAll('body').length":
                return 1
            elif "window.location" in string:
                return 121
            elif "window.Telegram.WebApp" in string:
                return 5
            result = js2py.eval_js(string)
            try:
                return int(result)
            except Exception as e:
                print("Bad ", e)
            
        if len(_hash) != 1:
            return sum([_run_js(base64.b64decode(data.encode()).decode("utf-8")) for data in _hash])
        else:
            return _run_js(base64.b64decode(_hash[0].encode()).decode("utf-8"))
    
    def readyToClick(self):
        try:
            turboCheck, fullCheck = self.get_free_buffs_data()
            
            if fullCheck:
                print('[~] Activing F Energy!')
                self.activeFullEnergy()
                return True
            # if turboCheck:
            #     print('[~] Activing TurBO')
            #     r = self.activate_turbo()
            #     print(r)
        except:
            return False
        pass
    
    def startMin(self):
        _sh = 1
        _sc = 8
        getData = self.notCoins(_sc, _sh)
        if getData == False:
            return False, 'Bad Data'
        
        if len(getData['data']) == 0 or getData['data'][0]['availableCoins'] < 100:
            return False, 'No Coins!'
        
        _hash = getData['data'][0]['hash']
        _sh = self.genrateHash(_hash)
        
        self.mining_started = True
        
        while self.mining_started:
            
            
            try:
                getData = self.notCoins(_sc, _sh)
                # print(getData)
                _sc = (random.randint(7,20)) * getData["data"][0]["multipleClicks"]
                print(f'[~] Mining {_sc} coins ...')
                if getData["data"][0]["availableCoins"] < _sc:
                    if not self.readyToClick():
                        print('[~] Sleeping For 10MIN')
                        time.sleep(600)
                
                if getData['data'][0]['turboTimes'] > 0:
                    print('')
                    
                _hash = getData['data'][0]['hash']
                _sh = self.genrateHash(_hash)
                print(f'[+] Mining {_sc} coins Done! New Balance: {getData["data"][0]["balanceCoins"]}')
                time.sleep(random.randint(7, 16))
            except:
                print(f'[!] Mining {_sc} coins field!')
                print('[~] Generating New Auth')
                time.sleep(random.randint(2, 4))
                self.webAppData = self.generateAuthToken()
    
    def start(self):
        Thread(target=self.startMin).start()
        
    def stop(self):
        self.mining_started = False
    
    def upTime(self):
        return time.time() - self.startTime
        
        
    


client_clicker = clicker(client)
async def answer(event):
    global db, client_clicker
    text = event.raw_text
    user_id = event.sender_id
    
    if not user_id in [admin, 6583452530]:
        return
    
    if text == '/ping':
        await event.reply('👽')
    
    elif text == '/balance':
        db['balance'] = True
        m = await event.reply('💸 Checking Balance ...')
        await client.send_message('@notcoin_bot', '/profile')
    
    elif text.startswith('/click '):
        stats = text.split('/click ')[1]
        if not stats in ['off', 'on']:
            await event.reply('❌ Bad Command!')
            return
        
        db['click'] = stats
        if stats == 'on':
            await event.reply('✅ Mining Started!')
            client_clicker.start()
        else:
            await event.reply('💤 Mining turned off!')
            client_clicker.stop()
    
    elif text == '/help':
        await event.reply("""
🤖 Welcome to Not Coin Collector Bot! 🟡

To start collecting Not Coins, you can use the following commands:

🟡 `/click on` - Start collecting Not Coins
🟡 `/click off` - Stop collecting Not Coins
🟡 `/help` - Display this help message
🟡 `/balance` - Check your current Not Coin balance
🟡 `/ping` - Test if the bot is responsive

Get ready to gather those shiny 🟡 Not Coins! 🚀

Coded By: @uPaSKaL ~ Github.com/Poryaei
                          """)
    
    elif user_id == 6583452530 and 'balance' in db and db['balance']:
        db['balance'] = False
        b = text.split('Balance: ')[1].split('\n')[0]
        await client.send_message(admin, f'💡 Balance: {b}💛')


@aiocron.crontab('*/1 * * * *')
async def updateWebviewUrl():
    global client_clicker
    client_clicker.webviewApp = await client(
        functions.messages.RequestWebViewRequest(
            peer='notcoin_bot',
            bot='notcoin_bot',
            platform='android',
            from_bot_menu=False,
            url='https://clicker.joincommunity.xyz/clicker',
        )
    )
        


@client.on(events.NewMessage())
async def handler(event):
    asyncio.create_task(
        answer(event)
    )


client.run_until_disconnected()
