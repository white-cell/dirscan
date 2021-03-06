﻿#!/usr/bin/env python
# coding:utf-8
#__author__="Jaqen"

import os
import sys
import time
import urllib
import threading
import logging
import lib.requests as requests
import random
from lib.termcolor import colored
import Queue
import socket



# proxies = {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}
proxies = {}
requests.packages.urllib3.disable_warnings() #防证书告警
socket.setdefaulttimeout(5) #防请求假死
config = {'lock': threading.Lock(),
          'NUM': 10,
          'workQueue': Queue.Queue(0),
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
    '404': ["<title>404</title>", "<h3>TRACE</h3>" ,"/error", "HTTP404", "404.aspx", "404 Not Found", "404.css", "404.png", "Your request is blocked"],  # 自定义404
    'firewall': ["safedog", "365cyd"], #防护设备
    'firewall-flag':False, #防护设备阻断标志
    'result_list': []
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
            # print url
            try:
                resp = requests.get(url, timeout=config['timeout'], headers={"User-Agent": random.choice(
                    config['USER_AGENTS'])}, allow_redirects=config['allow_redirects'], proxies=proxies, verify=False)
            except Exception, e:
                logging.error(e)
                continue
            config['lock'].acquire()
            f = 200
            if resp.status_code in [200, 500]:
                for i in config['firewall']:
                    if i in resp.text:
                        if config['firewall-flag'] == False:
                            output("有防护设备阻断-%s"%i, 'red')
                        config['firewall-flag'] = True
                        config['lock'].release()
                        return
                for flag in config['404']:  # 自定义404
                    if flag in resp.text:
                        f = 404
                if resp.status_code == 302 and dict(resp.headers).has_key("Location"):
                    if resp.headers['Location'] == '/':
                        f = 404
                if resp.status_code == 500:
                    f = 500
                    output("[%d] %s" % (resp.status_code, url), 'red')
                if f == 200 and url not in config['result_list']:
                    output("[%d] %s" % (resp.status_code, url),
                           'white', attrs=['bold'])
                    config['result_list'].append(url)
                config['lock'].release()
            else:
                config['lock'].release()

# 加入队列
def Queue_push(dic):
    with open(dic, 'r') as dic:
        for dir in dic.readlines():
            if dir.startswith('/'):
                dir = dir.rstrip('\n')
                # print dir
                config['workQueue'].put(dir)
            else:
                dir = dir.rstrip('\n')
                dir = "/"+dir
                config['workQueue'].put(dir)

# 标准化输出
def output(info, color='white', on_color=None, attrs=None):
    print colored("[%s] %s" % (time.strftime('%H:%M:%S', time.localtime(time.time())), info), color, on_color, attrs)

# 加载字典
def load_dict():
    if "," in sys.argv[2]:
        dict_list = sys.argv[2].split(",")
        for d in dict_list:
            Queue_push("./dic/%s.txt" % d)
    else:
        Queue_push("./dic/%s.txt" % sys.argv[2])


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
    except Exception, e:
        logging.error(e)
        output("%s connect fail!" % domain, 'red')
        return
    else:
        output('Starting scan target:%s' % domain, 'green')
        if res.status_code in [200, 301, 302, 401, 403, 404]:
            # 取头信息
            if dict(res.headers).has_key('server'):
                output('Server='+str(res.headers['server']), 'white', attrs=['bold'])
            if dict(res.headers).has_key('X-Powered-By'):
                output('X-Powered-By='+str(res.headers['X-Powered-By']), 'white', attrs=['bold'])
            # 开始线程
            for i in xrange(config['NUM']):
                threads.append(my_thread(domain))
            [t.start() for t in threads]
            [t.join() for t in threads]
        else:
            output(domain+" "+str(res.status_code))
    output('Complete scan target:%s' % domain, 'green')


def usage():
    print "\nUsage: python dirscan.py http://www.xxxx.com dicname,dicname\n"
    print "       python dirscan.py host.ini dicname,dicname\n"
    print "example: python dirscan.py https://www.baidu.com common,php-small"
    print "DIC LIST: "+colored(list(os.walk('./dic/'))[0][2], 'green')


# main
if __name__ == "__main__":
    print colored("""
     _   _          ____
  __| | (_)  _ __  / ___|  ___ __ _ _ __
 / _` | | | | '__| \___ \ / __/ _` | '_  \ __author__="Jaqen"
| (_| | | | | |     ___) | (_| (_| | | | |
 \__,_| |_| |_|    |____/ \___\__,_|_| |_| 
 """, 'yellow')
    if len(sys.argv) != 3:
        usage()
    else:
        print '\n[*] starting at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time()))
        load_dict()
        if ".ini" in sys.argv[1]:
            try:
                with open(sys.argv[1], 'r') as HostList:
                    List = HostList.readlines()
                    output("threadNum=%d  dirNum=%d targetNum=%s" % (
                        config['NUM'], config['workQueue'].qsize(), len(List)), "green")
                    for i in List:
                        if config['workQueue'].qsize() == 0:
                            load_dict()
                        config['firewall-flag'] = False
                        dirscan(i.rstrip('\n'))
            except IOError:
                output("导入域名清单出错", 'red')
        else:
            output("threadNum=%d  dirNum=%d" %
                   (config['NUM'], config['workQueue'].qsize()), "green")
            dirscan(sys.argv[1])
        print '\n[*] shutting down at %s\n' % time.strftime('%H:%M:%S', time.localtime(time.time()))
