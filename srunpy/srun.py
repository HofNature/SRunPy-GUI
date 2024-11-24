"""
This module provides functionality to interact with the Srun authentication system.
Modified from: https://github.com/iskoldt-X/SRUN-authenticator
"""

import json
import requests
import time
import re
import hmac
import hashlib
import math

def get_md5(password, token):
    return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()

def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()

def force(msg):
    ret = []
    for w in msg:
        ret.append(ord(w))
    return bytes(ret)

def ordat(msg, idx):
    if len(msg) > idx:
        return ord(msg[idx])
    return 0

def sencode(msg, key):
    l = len(msg)
    pwd = []
    for i in range(0, l, 4):
        pwd.append(
            ordat(msg, i) | ordat(msg, i + 1) << 8 | ordat(msg, i + 2) << 16
            | ordat(msg, i + 3) << 24)
    if key:
        pwd.append(l)
    return pwd

def lencode(msg, key):
    l = len(msg)
    ll = (l - 1) << 2
    if key:
        m = msg[l - 1]
        if m < ll - 3 or m > ll:
            return
        ll = m
    for i in range(0, l):
        msg[i] = chr(msg[i] & 0xff) + chr(msg[i] >> 8 & 0xff) + chr(
            msg[i] >> 16 & 0xff) + chr(msg[i] >> 24 & 0xff)
    if key:
        return "".join(msg)[0:ll]
    return "".join(msg)

def get_xencode(msg, key):
    if msg == "":
        return ""
    pwd = sencode(msg, True)
    pwdk = sencode(key, False)
    if len(pwdk) < 4:
        pwdk = pwdk + [0] * (4 - len(pwdk))
    n = len(pwd) - 1
    z = pwd[n]
    y = pwd[0]
    c = 0x86014019 | 0x183639A0
    m = 0
    e = 0
    p = 0
    q = math.floor(6 + 52 / (n + 1))
    d = 0
    while 0 < q:
        d = d + c & (0x8CE0D9BF | 0x731F2640)
        e = d >> 2 & 3
        p = 0
        while p < n:
            y = pwd[p + 1]
            m = z >> 5 ^ y << 2
            m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
            m = m + (pwdk[(p & 3) ^ e] ^ z)
            pwd[p] = pwd[p] + m & (0xEFB8D130 | 0x10472ECF)
            z = pwd[p]
            p = p + 1
        y = pwd[0]
        m = z >> 5 ^ y << 2
        m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
        m = m + (pwdk[(p & 3) ^ e] ^ z)
        pwd[n] = pwd[n] + m & (0xBB390742 | 0x44C6F8BD)
        z = pwd[n]
        q = q - 1
    return lencode(pwd, False)

class Srun_Py():
    def __init__(self, srun_host='gw.buaa.edu.cn',host_ip='10.200.21.4'):
        self.srun_host = srun_host
        self.init_url = "https://{}".format(srun_host)
        self.get_ip_api = 'https://{}/cgi-bin/rad_user_info?callback=JQuery'.format(srun_host)
        self.get_ip_api_ip= 'https://{}/cgi-bin/rad_user_info?callback=JQuery'.format(host_ip)
        self.get_challenge_api = "https://{}/cgi-bin/get_challenge".format(srun_host)
        self.get_challenge_api_ip = "https://{}/cgi-bin/get_challenge".format(host_ip)
        self.srun_portal_api = "https://{}/cgi-bin/srun_portal".format(srun_host)
        self.srun_portal_api_ip = "https://{}/cgi-bin/srun_portal".format(host_ip)
        self.rad_user_dm_api = "https://{}/cgi-bin/rad_user_dm".format(srun_host)
        self.rad_user_dm_api_ip = "https://{}/cgi-bin/rad_user_dm".format(host_ip)
        self.header = {'Host':srun_host,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'}
        self.n = '200'
        self.type = '1'
        self.ac_id = '1'
        self.enc = "srun_bx1"
        self._ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

    def get_base64(self,s):
        r = []
        x = len(s) % 3
        if x:
            s = s + '\0' * (3 - x)
        for i in range(0, len(s), 3):
            d = s[i:i + 3]
            a = ord(d[0]) << 16 | ord(d[1]) << 8 | ord(d[2])
            r.append(self._ALPHA[a >> 18])
            r.append(self._ALPHA[a >> 12 & 63])
            r.append(self._ALPHA[a >> 6 & 63])
            r.append(self._ALPHA[a & 63])
        if x == 1:
            r[-1] = '='
            r[-2] = '='
        if x == 2:
            r[-1] = '='
        return ''.join(r)

    def get_chksum(self,username,token,hmd5,ip,i):
        chkstr = token + username
        chkstr += token + hmd5
        chkstr += token + self.ac_id
        chkstr += token + ip
        chkstr += token + self.n
        chkstr += token + self.type
        chkstr += token + i
        return chkstr

    def get_info(self,username,password,ip):
        info_temp = {
            "username": username,
            "password": password,
            "ip": ip,
            "acid": self.ac_id,
            "enc_ver": self.enc
        }
        i = re.sub("'", '"', str(info_temp))
        i = re.sub(" ", '', i)
        return i

    def init_getip(self):
        try:
            res = requests.get(self.get_ip_api)
        except:
            try:
                res = requests.get(self.get_ip_api_ip,headers=self.header,verify=False)
            except:
                try:
                    res = requests.get(self.get_ip_api.replace('https','http',1))
                except:
                    res = requests.get(self.get_ip_api_ip.replace('https','http',1),headers=self.header,verify=False)
        data = json.loads(res.text[res.text.find('(')+1:-1])
        ip = data.get('client_ip') or data.get('online_ip')
        username = data.get('user_name')
        return ip, username

    def get_token(self,username,ip):
        get_challenge_params = {
            "callback": "jQuery112404953340710317169_" + str(int(time.time() * 1000)),
            "username": username,
            "ip": ip,
            "_": int(time.time() * 1000),
        }
        test = requests.Session()
        try:
            get_challenge_res = test.get(self.get_challenge_api, params=get_challenge_params, headers=self.header)
        except:
            try:
                get_challenge_res = test.get(self.get_challenge_api_ip, params=get_challenge_params, headers=self.header,verify=False)
            except:
                try:
                    get_challenge_res = test.get(self.get_challenge_api.replace('https','http',1), params=get_challenge_params, headers=self.header)
                except:
                    get_challenge_res = test.get(self.get_challenge_api_ip.replace('https','http',1), params=get_challenge_params, headers=self.header,verify=False)
        token = re.search('"challenge":"(.*?)"', get_challenge_res.text).group(1)
        return token

    def is_connected(self):
        try:
            try:
                res = requests.get(self.get_ip_api)
            except:
                try:
                    res = requests.get(self.get_ip_api_ip,headers=self.header,verify=False)
                except:
                    try:
                        res = requests.get(self.get_ip_api.replace('https','http',1))
                    except:
                        res = requests.get(self.get_ip_api_ip.replace('https','http',1),headers=self.header,verify=False)
            data = json.loads(res.text[res.text.find('(')+1:-1])
            if 'error' in data and data['error']=='not_online_error':
                return True, False, data
            else:
                return True, True, data
        except:
            return False, False

    def do_complex_work(self,username,password,ip,token):
        i = self.get_info(username,password,ip)
        i = "{SRBX1}" + self.get_base64(get_xencode(i, token))
        hmd5 = get_md5(password, token)
        chksum = get_sha1(self.get_chksum(username,token,hmd5,ip,i))
        return i, hmd5, chksum

    def login(self,username,password):
        is_available, is_online, _ = self.is_connected()
        if not is_available or is_online:
            raise Exception('You are already online or the network is not available!')
        ip , _ = self.init_getip()
        token = self.get_token(username,ip)
        i, hmd5, chksum = self.do_complex_work(username,password,ip,token)
        srun_portal_params = {
            'callback': 'jQuery11240645308969735664_' + str(int(time.time() * 1000)),
            'action': 'login',
            'username': username,
            'password': '{MD5}' + hmd5,
            'ac_id': self.ac_id,
            'ip': ip,
            'chksum': chksum,
            'info': i,
            'n': self.n,
            'type': self.type,
            'os': 'windows+10',
            'name': 'windows',
            'double_stack': '0',
            '_': int(time.time() * 1000)
        }
        test = requests.Session()
        try:
            srun_portal_res = test.get(self.srun_portal_api, params=srun_portal_params, headers=self.header)
        except:
            try:
                srun_portal_res = test.get(self.srun_portal_api_ip, params=srun_portal_params, headers=self.header,verify=False)
            except:
                try:
                    srun_portal_res = test.get(self.srun_portal_api.replace('https','http',1), params=srun_portal_params, headers=self.header)
                except:
                    srun_portal_res = test.get(self.srun_portal_api_ip.replace('https','http',1), params=srun_portal_params, headers=self.header,verify=False)
        srun_portal_res = srun_portal_res.text
        data = json.loads(srun_portal_res[srun_portal_res.find('(')+1:-1])
        return data.get('error') == 'ok'
    
    def logout(self):
        is_available, is_online, _ = self.is_connected()
        if not is_available or not is_online:
            raise Exception('You are not online or the network is not available!')
        ip , username = self.init_getip()
        t = int(time.time() * 1000);
        sign = get_sha1(str(t) + username + ip + '0' + str(t));
        user_dm_params={
            'ip': ip,
            'username': username,
            'time': t,
            'unbind': 0,
            'sign': sign
        }
        test = requests.Session()
        try:
            user_dm_res = test.get(self.rad_user_dm_api, params=user_dm_params, headers=self.header)
        except:
            try:
                user_dm_res = test.get(self.rad_user_dm_api_ip, params=user_dm_params, headers=self.header,verify=False)
            except:
                try:
                    user_dm_res = test.get(self.rad_user_dm_api.replace('https','http',1), params=user_dm_params, headers=self.header)
                except:
                    user_dm_res = test.get(self.rad_user_dm_api_ip.replace('https','http',1), params=user_dm_params, headers=self.header,verify=False)
        user_dm_res = user_dm_res.text
        return user_dm_res=='logout_ok'
