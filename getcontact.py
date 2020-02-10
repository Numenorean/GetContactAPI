import requests
import base64
import time
import hmac
import hashlib
import binascii
import json
from Crypto import Random
from Crypto.Cipher import AES
import sys

'''
by  SERJ.WS. Modded for python by _Skill_

AES_KEY и TOKEN берем в

/data/data/app.source.getcontact/shared_prefs/GetContactSettingsPref.xml
'''




AES_KEY = 'e62efa9ff5ebbc08701f636fcb5842d8760e28cc51e991f7ca45c574ec0ab15c' # Юзайте пока работает :)
TOKEN = 'gWFDtf18f16d9c97c01a58948fee3c6201094e93d6d3f102177c5778052'

key = b'2Wq7)qkX~cp7)H|n_tc&o+:G_USN3/-uIi~>M+c ;Oq]E{t9)RC_5|lhAA_Qq%_4'


class AESCipher(object):

    def __init__(self, AES_KEY): 
        self.bs = AES.block_size
        self.AES_KEY = binascii.unhexlify(AES_KEY)

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


aes = AESCipher(AES_KEY)

def sendPost(url, data, sig, ts):
    headers = {'X-App-Version': '4.9.1',
        'X-Token':TOKEN,
        'X-Os': 'android 5.0',
        'X-Client-Device-Id': '14130e29cebe9c39',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'deflate',
        'X-Req-Timestamp': ts,
        'X-Req-Signature': sig,
        'X-Encrypted': '1'}
    r = requests.post(url, data=data, headers=headers, verify=True)
    return json.loads(aes.decrypt(r.json()['data']))

def getByPhone(phone):
    ts = str(int(time.time()))
    req = f'"countryCode":"RU","source":"search","token":"{TOKEN}","phoneNumber":"{phone}"'
    req = '{'+req+'}'
    string = str(ts)+'-'+req
    sig = base64.b64encode(hmac.new(key, string.encode(), hashlib.sha256).digest()).decode()
    crypt_data = aes.encrypt(req)
    return sendPost('https://pbssrv-centralevents.com/v2.5/search',
                    b'{"data":"'+crypt_data+b'"}', sig, ts)

def getByPhoneTags(phone):
    ts = str(int(time.time()))
    req = f'"countryCode":"RU","source":"details","token":"{TOKEN}","phoneNumber":"{phone}"'
    req = '{'+req+'}'
    string = str(ts)+'-'+req
    sig = base64.b64encode(hmac.new(key, string.encode(), hashlib.sha256).digest()).decode()
    crypt_data = aes.encrypt(req)
    return sendPost('https://pbssrv-centralevents.com/v2.5/number-detail',
                    b'{"data":"'+crypt_data+b'"}', sig, ts)




def main(phone):
    if '+' not in phone:
        phone = '+'+phone
    print('======================')
    print(phone)
    finfo = getByPhone(phone)
    if finfo['result']['profile']['displayName']:
        print(finfo['result']['profile']['displayName'])
        print('Тегов найдено: '+str(finfo['result']['profile']['tagCount']))
        try:
            print('\n'.join([i['tag'] for i in getByPhoneTags(phone)['result']['tags']]))
        except KeyError:
            if finfo['result']['profile']['tagCount'] > 0:
                print('Теги найдены, но для просморта нужен премиум')
            else:
                print('Тегов не найдено!')
    else:
        print('Не найдено!')
    print('Осталось обычных поисков: '+str(finfo['result']['subscriptionInfo']['usage']['search']['remainingCount'])+'/'+str(finfo['result']['subscriptionInfo']['usage']['search']['limit']))
    print('С тегами: '+str(finfo['result']['subscriptionInfo']['usage']['numberDetail']['remainingCount'])+'/'+str(finfo['result']['subscriptionInfo']['usage']['numberDetail']['limit']))
    print('======================')

main(sys.argv[1])
