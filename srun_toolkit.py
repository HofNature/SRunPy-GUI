#!/usr/bin/python3
import json
import requests
import time
import re
import hmac
import hashlib
import math
# import os

username = ''
password = ''
srun_host = 'gw.buaa.edu.cn'
get_ip_api='http://{}/cgi-bin/rad_user_info?callback=JQuery'.format(srun_host)
init_url="https://{}".format(srun_host)
get_challenge_api="https://{}/cgi-bin/get_challenge".format(srun_host)
srun_portal_api="https://{}/cgi-bin/srun_portal".format(srun_host)
rad_user_dm_api="https://{}/cgi-bin/rad_user_dm".format(srun_host)
sleeptime = 300

# if username == '':
#     username = os.getenv('USERNAME').strip()
# if password == '':
#     password = os.getenv('PASSWORD').strip()
# if init_url == '':
#     init_url = os.getenv('init_url').strip()
# if get_challenge_api == '':
#     get_challenge_api = os.getenv('get_challenge_api').strip()
# if srun_portal_api == '':
#     srun_portal_api = os.getenv('srun_portal_api').strip()
# if get_ip_api == '':
#     get_ip_api = os.getenv('get_ip_api').strip()

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
}

n = '200'
type = '1'
ac_id = '1'
enc = "srun_bx1"

_ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"


def _getbyte(s, i):
    x = ord(s[i])
    if x > 255:
        print("{0} INVALID_CHARACTER_ERR: DOM Exception 5".format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
        exit(0)
    return x


def get_base64(s):
    r = []
    x = len(s) % 3
    if x:
        s = s + '\0' * (3 - x)
    for i in range(0, len(s), 3):
        d = s[i:i + 3]
        a = ord(d[0]) << 16 | ord(d[1]) << 8 | ord(d[2])
        r.append(_ALPHA[a >> 18])
        r.append(_ALPHA[a >> 12 & 63])
        r.append(_ALPHA[a >> 6 & 63])
        r.append(_ALPHA[a & 63])
    if x == 1:
        r[-1] = '='
        r[-2] = '='
    if x == 2:
        r[-1] = '='
    return ''.join(r)


def get_md5(password, token):
    return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()


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


def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()


def get_chksum():
    chkstr = token + username
    chkstr += token + hmd5
    chkstr += token + ac_id
    chkstr += token + ip
    chkstr += token + n
    chkstr += token + type
    chkstr += token + i
    return chkstr


def get_info():
    info_temp = {
        "username": username,
        "password": password,
        "ip": ip,
        "acid": ac_id,
        "enc_ver": enc
    }
    i = re.sub("'", '"', str(info_temp))
    i = re.sub(" ", '', i)
    return i


def init_getip():
    global ip
    res = requests.get(get_ip_api)
    # [7:-1]是为了去掉前面的 jQuery( 和后面的 )
    data = json.loads(res.text[7:-1])
    ip = data.get('client_ip') or data.get('online_ip')
    print("{0} ip:".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + ip, flush=True)
    return ip


def get_token():
    # print("{0} 获取token".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))), flush=True)
    global token
    get_challenge_params = {
        "callback": "jQuery112404953340710317169_" + str(int(time.time() * 1000)),
        "username": username,
        "ip": ip,
        "_": int(time.time() * 1000),
    }
    test = requests.Session()
    get_challenge_res = test.get(get_challenge_api, params=get_challenge_params, headers=header)
    token = re.search('"challenge":"(.*?)"', get_challenge_res.text).group(1)
    print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), get_challenge_res.text),
          flush=True)
    print("{0}token为:".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + token, flush=True)


def is_connected():
    try:
        res = requests.get(get_ip_api)
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


def do_complex_work():
    global i, hmd5, chksum
    i = get_info()
    i = "{SRBX1}" + get_base64(get_xencode(i, token))
    hmd5 = get_md5(password, token)
    chksum = get_sha1(get_chksum())
    print("{0} 所有加密工作已完成".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)


def login():
    srun_portal_params = {
        'callback': 'jQuery11240645308969735664_' + str(int(time.time() * 1000)),
        'action': 'login',
        'username': username,
        'password': '{MD5}' + hmd5,
        'ac_id': ac_id,
        'ip': ip,
        'chksum': chksum,
        'info': i,
        'n': n,
        'type': type,
        'os': 'windows+10',
        'name': 'windows',
        'double_stack': '0',
        '_': int(time.time() * 1000)
    }
    # print(srun_portal_params)
    test = requests.Session()
    srun_portal_res = test.get(srun_portal_api, params=srun_portal_params, headers=header)
    print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), srun_portal_res.text),
          flush=True)
    
def logout():
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
    user_dm_res = test.get(rad_user_dm_api, params=user_dm_params, headers=header)
    print("{0} {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), user_dm_res.text),
        flush=True)
    


if __name__ == '__main__':
    while True:
        if is_connected():
            print('{0} 已通过认证，无需再次认证'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
        else:
            ip = init_getip()
            get_token()
            do_complex_work()
            login()
            time.sleep(5)
            logout()
        time.sleep(sleeptime)
