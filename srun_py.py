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
    def __init__(self, srun_host='gw.buaa.edu.cn'):
        self.srun_host = srun_host
        self.init_url = "https://{}".format(srun_host)
        self.get_ip_api = 'http://{}/cgi-bin/rad_user_info?callback=JQuery'.format(srun_host)
        self.get_challenge_api = "https://{}/cgi-bin/get_challenge".format(srun_host)
        self.srun_portal_api = "https://{}/cgi-bin/srun_portal".format(srun_host)
        self.rad_user_dm_api = "https://{}/cgi-bin/rad_user_dm".format(srun_host)
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'}
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
        res = requests.get(self.get_ip_api)
        # [7:-1]是为了去掉前面的 jQuery( 和后面的 )
        data = json.loads(res.text[7:-1])
        ip = data.get('client_ip') or data.get('online_ip')
        username = data.get('user_name')
        # print("{0} ip:".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + ip, flush=True)
        return ip, username


    def get_token(self,username,ip):
        # print("{0} 获取token".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))), flush=True)
        get_challenge_params = {
            "callback": "jQuery112404953340710317169_" + str(int(time.time() * 1000)),
            "username": username,
            "ip": ip,
            "_": int(time.time() * 1000),
        }
        test = requests.Session()
        get_challenge_res = test.get(self.get_challenge_api, params=get_challenge_params, headers=self.header)
        token = re.search('"challenge":"(.*?)"', get_challenge_res.text).group(1)
        # print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), get_challenge_res.text),
        #     flush=True)
        # print("{0}token为:".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + token, flush=True)
        return token


    def is_connected(self):
        try:
            res = requests.get(self.get_ip_api)
            # [7:-1]是为了去掉前面的 jQuery( 和后面的 )
            data = json.loads(res.text[7:-1])
            if 'error' in data and data['error']=='not_online_error':
                return False
            else:
                return True
            # session = requests.Session()
            # html = session.get("https://www.baidu.com", timeout=2)
        except:
            return False
        return True


    def do_complex_work(self,username,password,ip,token):
        i = self.get_info(username,password,ip)
        i = "{SRBX1}" + self.get_base64(get_xencode(i, token))
        hmd5 = get_md5(password, token)
        chksum = get_sha1(self.get_chksum(username,token,hmd5,ip,i))
        # print("{0} 所有加密工作已完成".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
        return i, hmd5, chksum


    def login(self,username,password):
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
        # print(srun_portal_params)
        test = requests.Session()
        srun_portal_res = test.get(self.srun_portal_api, params=srun_portal_params, headers=self.header)
        srun_portal_res = srun_portal_res.text
        data = json.loads(srun_portal_res[srun_portal_res.find('(')+1:-1])
        print(data)
        # print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), srun_portal_res.text),
        #     flush=True)
    
    def logout(self):
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
        user_dm_res = test.get(self.rad_user_dm_api, params=user_dm_params, headers=self.header)
        user_dm_res = user_dm_res.text
        #data = json.loads(user_dm_res[user_dm_res.find('(')+1:-1])
        print(user_dm_res)
        # print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), user_dm_res.text),
        #     flush=True)
    

if __name__ == '__main__':
    srun_client = Srun_Py()
    command = '_'
    while command != 'q':
        command = input('>')
        if command == '1':
            print(srun_client.is_connected())
        elif command == '2':
            import getpass
            username = input('username: ')
            passwd = getpass.getpass('passwd: ')
        elif command == '3':
            srun_client.login(username, passwd)
        elif command == '4':
            srun_client.logout()
        elif command == 'q':
            print('bye!')
        else:
            print('unknown command!')