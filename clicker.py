import asyncio
import js2py
import requests
import os, sys, ssl
from telethon.sync import TelegramClient
from telethon import events
from telethon.sync import functions, types, events
from urllib.parse import unquote
import aiocron
import base64
import random
import time
import json
from threading import Thread, active_count
# -----------
with open('config.json') as f:
    data = json.load(f)
    api_id = data['api_id']
    api_hash = data['api_hash']
    admin = data['admin']

VERSION = 1.4

client = TelegramClient('bot', api_id, api_hash, device_model=f"NotCoin Clicker V{VERSION}")
client.start()
client_id = client.get_me(True).user_id




db = {
    'click': 'off'
}


print("Client is Ready ;)")

# -----------

class BypassTLSv1_3(requests.adapters.HTTPAdapter):
    SUPPORTED_CIPHERS = [
        "ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384", "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-RSA-AES128-SHA", "ECDHE-RSA-AES256-SHA",
        "AES128-GCM-SHA256", "AES256-GCM-SHA384", "AES128-SHA", "AES256-SHA", "DES-CBC3-SHA",
        "TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_CCM_SHA256", "TLS_AES_256_CCM_8_SHA256"
    ]

    def __init__(self, *args, **kwargs):
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.set_ciphers(':'.join(BypassTLSv1_3.SUPPORTED_CIPHERS))
        self.ssl_context.set_ecdh_curve("prime256v1")
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = None
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = None
        return super().proxy_manager_for(*args, **kwargs)

class Proxy_Tools:
    def __init__(self):
        self.proxies = None
        self.valid_proxy = None

    def getProxies(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Referer': 'https://.proxyscrape.com'
        }
        try:
            proxies = requests.get('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=7000&country=all&ssl=all&anonymity=all', timeout=10, headers=headers).text.replace('\n', '').replace('\b', '')
            print('[+] Proxy List Updated!')
        except Exception as e:
            print(e)
            
        with open('socks4.txt', 'w') as f:
            f.write(proxies)
        return open('socks4.txt').read().split('\n')
    
    def get_proxies_v2(self, protocol):
        proxies_data = requests.get(f"https://api.proxyscrape.com/v2/?request=getproxies&protocol={protocol}&timeout=7000&country=all&ssl=all&anonymity=all").text
        proxies_list = proxies_data.split('\n')
        formatted_proxies = []

        for p in proxies_list:
            if p.strip():
                formatted_proxies.append({
                    'http': f'{protocol}://{p.strip().replace("/r", "")}',
                    'https': f'{protocol}://{p.strip().replace("/r", "")}'
                })

        return formatted_proxies

    def checkProxy(self, p):
        session = requests.sessions.Session()
        session.mount("https://", BypassTLSv1_3())
        session.headers = {
            "Host": "clicker-api.joincommunity.xyz",
            "Accept": "*/*",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "auth,authorization,content-type",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Auth": "5",
            "Content-Type": "application/json",
            "Origin": "https://clicker.joincommunity.xyz",
            "Referer": "https://clicker.joincommunity.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        }

        data = {
            'count': '100',
            'hash': -1,
            'webAppData': "user=pass"
        }

        proxies = p

        try:
            r = session.options('https://clicker-api.joincommunity.xyz/clicker/core/click', timeout=9, proxies=proxies,
                        headers=session.headers)
            r = session.post('https://clicker-api.joincommunity.xyz/clicker/core/click', timeout=9, proxies=proxies,
                         headers=session.headers, json=data)
            r.json()
            self.valid_proxy = proxies
        except Exception as e:
            pass

    def new(self, _to = 7000):
        print('[~] Checking Proxies ...')
        for p in self.get_proxies_v2('socks4') + self.get_proxies_v2('socks5') + self.get_proxies_v2('https'):
            while active_count() > 20:
                pass
            Thread(
                target=self.checkProxy, args=(p,)
            ).start()
            if self.valid_proxy != None:
                return self.valid_proxy
        if _to > 12000:
            print("[!] I didn't find a suitable proxy! I'm shutting down the process.")
            sys.exit()
        if self.valid_proxy == None:
            print('[!] Trying find new proxy ...')
            return self.new(_to+1000)

class clicker:
    def __init__(self, client:TelegramClient) -> None:
        self.session = requests.sessions.Session()
        self.session.mount("https://", BypassTLSv1_3())
        self.session.headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Auth": "1",
            "Content-Type": "application/json",
            "Origin": "https://clicker.joincommunity.xyz",
            "Referer": "https://clicker.joincommunity.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        }
        self.option_headers = {
            "Host": "clicker-api.joincommunity.xyz",
            "Accept": "*/*",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "auth,authorization,content-type",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Auth": "5",
            "Content-Type": "application/json",
            "Origin": "https://clicker.joincommunity.xyz",
            "Referer": "https://clicker.joincommunity.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        }
        self.scraper = self.session
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
        print(self.webviewApp, self.webAppData)
        self._mining_stats = ['Sleeping 💤', 'Mining 🔨 ', 'OFF 🔴']
        self.mining_stats = self._mining_stats[-1]
        self.mining_started = False
        self.startTime = time.time()
        self.checkTasksTime = 0
        self.notCoinBalance = 0
        self.speed = (7, 20)
        self.turbo = False
        self.useProxy = True
        # Proxy 
        self.proxies = {}
        if self.useProxy:
            self.updateProxies()
    
    def updateProxies(self):
        if self.useProxy:
            try:
                _pt = Proxy_Tools()
                self.proxies = _pt.new()
                print('[+] Proxies:  ', self.proxies)
            except Exception as e:
                print(e)
                pass
    
    def updateUrl(self, url):
        self.webviewApp = url
    
    def changeSpeed(self, speed):
        self.speed = (speed*2, speed*5)
        
    def profile(self):
        data = {
            'webAppData': self.webAppData
        }
        try:
            
            r = self.session.get('https://clicker-api.joincommunity.xyz/clicker/profile', json=data).json()
            _balance = r['data'][0]['balanceCoins']
            return _balance
        except:
            return False
    
    def generateAuthToken(self):
        try:
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
        except Exception as e:
            print('[!] Error auth:  ', e)
            return False

    
    def notCoins(self, _c, _h):
        data = {
            'count': _c,
            'hash': _h,
            'webAppData': self.webAppData
        }
        self.session.headers['content-length'] = str(len(json.dumps(data)))
        try:
            r = self.scraper.options('https://clicker-api.joincommunity.xyz/clicker/core/click', json=data, headers=self.option_headers, proxies=self.proxies, timeout=10)
            r = self.scraper.post('https://clicker-api.joincommunity.xyz/clicker/core/click', json=data, headers=self.session.headers, proxies=self.proxies, timeout=10)
            if 'just a moment' in r.text.lower():
                print('[!] Cloudflare detected!')
                raise Exception('Cloudflare detected!')
            return r.json()
        except ConnectionError as e:
            print('Connection Error: ', e)
            print('Updating Proxies ...')
            self.updateProxies()
            return self.notCoins(_c, _h)
        except Exception as e:
            print('Mining Error: ', e)
            self.updateProxies()
            return False
    
    def activeFullEnergy(self):
        data = {
            'webAppData': self.webAppData
        }
        try:
            r = self.session.options('https://clicker-api.joincommunity.xyz/clicker/task/2', json=data)
            r = self.session.post('https://clicker-api.joincommunity.xyz/clicker/task/2', json=data)
            return ['ok'] in r.json()
        except Exception as e:
            print('[!] Mining Error:   ', e)
            return False
    
    def activate_turbo(self):
        data = {
            'webAppData': self.webAppData
        }
        try:
            r = self.session.POST('https://clicker-api.joincommunity.xyz/clicker/core/active-turbo', json=data)
            return r.json()['data'][0]['multiple']
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
            for current_buff in r.json()['data']:
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
            return max_turbo_times >= turbo_times_count, max_full_energy_times >= full_energy_times_count
        except Exception as e:
            print(e)
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
        
        return sum([_run_js(base64.b64decode(data.encode()).decode("utf-8")) for data in _hash])
    
    def readyToClick(self):
        try:
            turboCheck, fullCheck = self.get_free_buffs_data()
            
            if fullCheck:
                print('[~] Activing F Energy!')
                return self.activeFullEnergy()

            # elif turboCheck:
            #     _tb = self.activate_turbo()
            #     if _tb != False:
            #         self.turbo = True
                
        except:
            return False
        pass
    
    def startMin(self):
        _sh = -1
        _sc = 20
        getData = self.notCoins(_sc, _sh)

        self.mining_started = True
        self.mining_stats = self._mining_stats[1]
        
        while self.mining_started:
            try:
                print('[+] Lets mine ...')
                getData = self.notCoins(_sc, _sh)
                print(getData)
                if not 'data' in getData:
                    raise
                _sc = (random.randint(self.speed[0], self.speed[1])) * getData["data"][0]["multipleClicks"]
                print(f'[~] Mining {_sc} coins ...')
                if getData["data"][0]["availableCoins"] < _sc:
                    if not self.readyToClick():
                        print('[~] Sleeping For 10MIN')
                        self.mining_stats = self._mining_stats[0]
                        time.sleep(600)
                
                if getData['data'][0]['turboTimes'] > 0:
                    print('')
                    
                _hash = getData['data'][0]['hash']
                _sh = self.genrateHash(_hash)
                print(f'[+] Mining {_sc} coins Done! New Balance: {getData["data"][0]["balanceCoins"]}')
                self.notCoinBalance = getData["data"][0]["balanceCoins"]
                time.sleep(random.randint(7, 16))
            except Exception as e:
                print(f'[!] Mining {_sc} coins field!')
                print('[~] Generating New Auth')
                time.sleep(random.randint(2, 4))
                self.webAppData = self.generateAuthToken()
    
    def start(self):
        if not self.mining_started:
            Thread(target=self.startMin).start()
        
    def stop(self):
        self.mining_started = False
    
    def upTime(self):
        return time.time() - self.startTime
    
    def balance(self):
        return self.profile()
    


client_clicker = clicker(client)

async def answer(event):
    global db, client_clicker
    text = event.raw_text
    user_id = event.sender_id
    
    if not user_id in [admin, 6583452530]:
        return
    
    if admin == client_id:
        _sendMessage = event.edit
    else:
        _sendMessage = event.reply
    
    if text == '/ping':
        await _sendMessage('👽')
    
    elif text == '/balance':
        db['balance'] = True
        m = await _sendMessage('💸 Checking Balance ...')
        _balance = client_clicker.balance()
        if _balance != False:
            db['balance'] = False
            await m.edit(f'💡 Balance: {_balance}💛')
        else:
            await client.send_message('@notcoin_bot', '/profile')
    
    elif text.startswith('/click '):
        stats = text.split('/click ')[1]
        if not stats in ['off', 'on']:
            await _sendMessage('❌ Bad Command!')
            return
        
        db['click'] = stats
        if stats == 'on':
            await _sendMessage('✅ Mining Started!')
            client_clicker.start()
        else:
            await _sendMessage('💤 Mining turned off!')
            client_clicker.stop()
    
    elif text.startswith('/speed '):
        speed_str = text.split('/speed ')[1]
        if speed_str.isdigit():
            speed = int(speed_str)
            if 1 <= speed <= 10:
                client_clicker.changeSpeed(speed)
                await _sendMessage(f'⚡️ Speed changed to: {speed}')
            else:
                await _sendMessage('⚠️ Please provide a speed value between 1 and 10.')
        else:
            await _sendMessage('⚠️ Speed value must be a valid number.')
    
    elif text == '/help':
        _mining_clicker = client_clicker.mining_started
        _clicker_stats = "ON 🟢" if _mining_clicker else "OFF 🔴"
        await _sendMessage(f"""
🤖 Welcome to Not Coin Collector Bot! 🟡

📊 Clicker stats: {_clicker_stats} ({client_clicker.mining_stats})

To start collecting Not Coins, you can use the following commands:

🟡 `/click on` - Start collecting Not Coins
🟡 `/click off` - Stop collecting Not Coins
🟡 `/speed 1-10` - Set collection speed (1-10) (4 - 6 is best!)
🟡 `/help` - Display this help message
🟡 `/balance` - Check your current Not Coin balance
🟡 `/ping` - Test if the bot is responsive
🟡 `/info` - Display information about the bot
🟡 `/version` - Show the bot version
🟡 `/stop` - Stop bot

Get ready to gather those shiny 🟡 Not Coins! 🚀

Coded By: @uPaSKaL ~ [GitHub](https://github.com/Poryaei)
                          """)
    
    elif text == '/info':
        await _sendMessage("""
🤖 Bot Name: Not Coin Collector Bot
💻 Author: Abolfazl Poryaei
🌐 GitHub: [Poryaei](https://github.com/Poryaei)
        """)
    
    elif text == '/version':
        await _sendMessage(f"ℹ️ Version: {VERSION}")
    
    elif text == '/stop':
        client_clicker.stop()
        await _sendMessage('👋')
        sys.exit()
  
    elif user_id == 6583452530 and 'balance' in db and db['balance']:
        db['balance'] = False
        b = text.split('Balance: ')[1].split('\n')[0]
        await client.send_message(admin, f'💡 Balance: {b}💛')


@aiocron.crontab('*/15 * * * *')
async def updateWebviewUrl():
    global client_clicker
    while True:
        try:
            print("[~] Updating webview URL ...")
            url = await client(
                functions.messages.RequestWebViewRequest(
                    peer='notcoin_bot',
                    bot='notcoin_bot',
                    platform='android',
                    from_bot_menu=False,
                    url='https://clicker.joincommunity.xyz/clicker',
                )
            )
            client_clicker.updateUrl(url)
            print("[+] WebView URL UPDATED!")
            break
        except Exception as e:
            print('[!] Update Error:  ', e)
            await asyncio.sleep(10)


client.send_message(admin, "✅ Miner Activated! \nUse the `/help` command to view help. 💪")

@aiocron.crontab('*/5 * * * *')
async def updateProxies():
    global client_clicker
    client_clicker.updateProxies()
        


@client.on(events.NewMessage())
async def handler(event):
    asyncio.create_task(
        answer(event)
    )


client.run_until_disconnected()
