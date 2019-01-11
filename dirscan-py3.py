#!/usr/bin/env python
# coding:utf-8
#__author__="Jaqen"

import os
import sys
import time
import threading
import logging
import lib.requests as requests
from lib.get_proxy import proxy_list,check_proxy
import random
from lib.termcolor import colored
import queue
import socket



# proxies = {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}
proxies = {}
requests.packages.urllib3.disable_warnings() #防证书告警
socket.setdefaulttimeout(5) #防请求假死
config = {'lock': threading.Lock(),
          'NUM': 10,
          'workQueue': queue.Queue(0),
          'timeout': 3,
          'allow_redirects': False,
          'USER_AGENTS': [
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52", ],
    'customize_flag': 'n', #自定义字典标识位
    '404': [ "The requested URL was rejected. Please consult with your administrator","javascript:Relogin()","Default.aspx","<title>404</title>", "<title>Error</title>", "<h3>TRACE</h3>", "This page can't be displayed", "HR noShade SIZE", "/error", "HTTP404", "404.aspx", "404 Not Found", "404.css", "404.png", "Your request is blocked", "mailto:anquan@jd.com"],  # 自定义404
    'firewall': ["safedog", "365cyd"], #防护设备
    'firewall-flag':False, #防护设备阻断标志
    'result_list': [],
    'proxy_list': [],
    'proxy_flag':False #是否使用代理池
}


class my_thread(threading.Thread):
    def __init__(self, domain):
        threading.Thread.__init__(self)
        self.rule = []
        self.domain = domain

    def run(self):
        while not config['workQueue'].empty():
            payload = config['workQueue'].get(True).lstrip('/')
            url = "%s/%s" % (self.domain.rstrip('/'), payload)
            kwargs = {"timeout":config['timeout'], "headers":{"User-Agent": random.choice(
                    config['USER_AGENTS'])}, "allow_redirects":config['allow_redirects'], "verify":False}
            if config['proxy_flag']:
                if len(config['proxy_list']) > 5:
                    kwargs["proxies"] = {"http": random.choice(config['proxy_list']), "https": random.choice(config['proxy_list'])}
                else:
                    output("get useful proxy too less,keep real IP!",'red')
                    config['proxy_flag'] = False
            # print url
            try:
                resp = requests.get(url, **kwargs)
            except Exception as e:
                logging.error(e)
                continue
            with config['lock']:
                f = 200
                if resp.status_code in [200, 500]:
                    for i in config['firewall']:
                        if i in resp.text:
                            if config['firewall-flag'] == False:
                                config['firewall-flag'] = True
                                output("有防护设备阻断-%s"%i, 'red')
                            return
                    for flag in config['404']:  # 自定义404
                        if flag in resp.text:
                            f = 404
                    if resp.status_code == 302 and "Location" in dict(resp.headers):
                        if resp.headers['Location'] == '/':
                            f = 404
                    if resp.status_code == 500:
                        f = 500
                        output("[%d] %s" % (resp.status_code, url), 'red')
                    if f == 200 and url not in config['result_list']:
                        output("[%d] %s [lenth:%s]" % (resp.status_code, url, len(resp.text)),
                               'white', attrs=['bold'])
                        config['result_list'].append(url)

# 加入队列
def Queue_push(dic):
    with open(dic, 'r') as dic:
        for dir in dic.readlines():
            if dir.startswith('/'):
                dir = dir.rstrip('\r').rstrip('\n')
                # print dir
                config['workQueue'].put(dir)
            else:
                dir = dir.rstrip('\r').rstrip('\n')
                dir = "/"+dir
                config['workQueue'].put(dir)

# 标准化输出
def output(info, color='white', on_color=None, attrs=None):
    print(colored("[%s] %s" % (time.strftime('%H:%M:%S', time.localtime(time.time())), info), color, on_color, attrs))

# 加载字典
def load_dict():
    dic = list(os.walk('./dic/'))[0][2]
    if "," in sys.argv[2]:
        dict_list = sys.argv[2].split(",")
        for d in dict_list:
            if d+'.txt' in dic:
                Queue_push("./dic/%s.txt" % d)
            else:
                output('dicname error','red')
                print('\n[*] shutting down at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time    ())))
                exit()
    else:
        if sys.argv[2]+'.txt' in dic:
            Queue_push("./dic/%s.txt" % sys.argv[2])
        else:
            output('dicname error','red')
            print('\n[*] shutting down at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time    ())))
            exit()

# 整理定制字典未完成
def load_customize_dic():
    p_severity = re.compile('{severity=(\d)}')
    p_tag = re.compile('{tag="([^"]+)"}')
    p_status = re.compile('{status=(\d{3})}')
    p_content_type = re.compile('{type="([^"]+)"}')
    p_content_type_no = re.compile('{type_no="([^"]+)"}')
    with open("dic/customize.txt") as customize:
        for rule in custonize.readlines():
            rule = rule.strip().replace('{hostname}', hostname)
            if rule.startswith('/'):
                dir = rule.split()[0]

# main
def dirscan(domain):
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s <%(message)s>',
                        filename='run.log',
                        filemode='w')
    if not domain.startswith('http'):
        domain = 'http://%s' % domain
    threads = []
    # 确认网站可访问
    try:
        res = requests.get(domain, timeout=config['timeout'], headers={"User-Agent": random.choice(
            config['USER_AGENTS'])}, allow_redirects=config['allow_redirects'], proxies=proxies, verify=False)
        # print res
    except Exception as e:
        logging.error(e)
        output("%s connect fail!" % domain, 'red')
        return
    output('Starting scan target:%s' % domain, 'green')
    if res.status_code:
        output(domain+" "+str(res.status_code))
        # 取头信息
        if 'Server' in dict(res.headers):
            output('Server='+str(res.headers['server']), 'white', attrs=['bold'])
        if 'X-Powered-By' in dict(res.headers):
            output('X-Powered-By='+str(res.headers['X-Powered-By']), 'white', attrs=['bold'])
        # 获取代理池
        if config['proxy_flag']:
            if os.path.exists('proxy_list.txt'):
                with open('proxy_list.txt','r') as proxy_file:
                    proxy_list = proxy_file.readlines()
                if len(proxy_list) > 10:
                    for i in proxy_list:
                        config['proxy_list'].append(i.rstrip('\n'))
                    output("Start check cache proxy useful,will loss some time", 'green')
                    config['proxy_list'] = check_proxy(domain,config['proxy_list'])
                    output("Complete check cache proxy useful,will loss some time", 'green')
                else:
                    output("Start get proxy list,will loss some time", 'green')
                    config['proxy_list'] = proxy_list(domain)
                    output("Complete get proxy list", 'green')
            else:
                output("Start get proxy list,will loss some time", 'green')
                config['proxy_list'] = proxy_list(domain)
                output("Complete get proxy list", 'green')
        # 开始线程
        for i in range(config['NUM']):
            threads.append(my_thread(domain))
        [t.start() for t in threads]
        [t.join() for t in threads]
    else:
        output(domain+" "+str(res.status_code))
    output('Complete scan target:%s' % domain, 'green')


def usage():
    print("\nUsage: python3 dirscan-py3.py http://www.xxxx.com dicname,dicname\n")
    print("       python3 dirscan-py3.py host.ini dicname,dicname\n")
    print("example: python3 dirscan-py3.py https://www.baidu.com common,php-small")
    print("DIC LIST: "+colored(list(os.walk('./dic/'))[0][2], 'green'))


# main
if __name__ == "__main__":
    print(colored("""
     _   _          ____
  __| | (_)  _ __  / ___|  ___ __ _ _ __
 / _` | | | | '__| \___ \ / __/ _` | '_  \ __author__="Jaqen"
| (_| | | | | |     ___) | (_| (_| | | | |
 \__,_| |_| |_|    |____/ \___\__,_|_| |_| 
 """, 'yellow'))
    if len(sys.argv) != 3:
        usage()
    else:
        print('\n[*] starting at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time())))
        load_dict()
        #代理ip质量太差，影响扫描结果
        if  input(colored("[%s] Use proxy pool?[y/N]" %time.strftime('%H:%M:%S', time.localtime(time.time())), 'green')).lower() == 'y':
            config['proxy_flag'] = True
        if ".ini" in sys.argv[1]:
            try:
                with open(sys.argv[1], 'r') as HostList:
                    List = HostList.readlines()
                    output("threadNum=%d  dirNum=%d targetNum=%s proxy_mode=%s" % (
                        config['NUM'], config['workQueue'].qsize(), len(List), config['proxy_flag']), "green")
                    for i in List:
                        if config['workQueue'].qsize() == 0:
                            load_dict()
                        config['firewall-flag'] = False
                        dirscan(i.rstrip('\r').rstrip('\n'))
            except IOError:
                output("导入域名清单出错", 'red')
        else:
            output("threadNum=%d  dirNum=%d" %
                   (config['NUM'], config['workQueue'].qsize()), "green")
            dirscan(sys.argv[1])
        print('\n[*] shutting down at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time())))
