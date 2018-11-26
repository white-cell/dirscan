#!/usr/bin/env python3
# coding:utf-8
#__author__="Jaqen"
import requests
import re
import threading
import logging
import queue
import time
from lxml import html
from lib.termcolor import colored

good_proxy = []
cache_proxy = []
proxy_queue = queue.Queue(0)
def get_proxy1():
    url = "http://www.66ip.cn/nmtq.php?getnum=1000&isp=1&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip"
    try:
        resp = requests.get(url,headers={'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0",'Cookie':"Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1542093293; Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4=1542093820; yd_cookie=8a8786e6-3418-47eda62ada4672418079baf0f74b8bedbf68; _ydclearance=aebbe4fb0d9bff39f8066feb-d726-4472-9e42-5de7d83d1136-1542452439"})
    except Exception as e:
        logging.error(e)
        return
    if resp is not None and resp.status_code == 200:
        result = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,6}',resp.text)
        for proxy in result:
            proxy_queue.put(proxy)
def get_proxy2():
    for i in range(1,20):
        url = 'https://www.kuaidaili.com/free/inha/%s/'%i
        try:
            resp = requests.get(url)
        except Exception as e:
            logging.error(e)
            continue
        if resp is not None and resp.status_code == 200:
            resp = html.fromstring(resp.text)
            ip_list = resp.xpath("//td[@data-title='IP']/text()")
            port_list = resp.xpath("//td[@data-title='PORT']/text()")
            for i in range(len(ip_list)):
                proxy = ip_list[i] + ":" + port_list[i]
                proxy_queue.put(proxy)

def _fecth(test_url):
    kwargs = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0",
        },
        "timeout": 3,
        "allow_redirects":False
    }
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        cache_proxy.append(proxy)
        kwargs["proxies"] = {"http": proxy, "https": proxy}
        try:
            resp = requests.get(test_url, **kwargs)
        except:
            continue
        if resp.status_code == 200:
            # try:
            #     resp = requests.get(test_url, **kwargs)
            # except:
            #     continue
            print(colored("[%s] proxy pool add %s" % (time.strftime('%H:%M:%S', time.localtime(time.time())),proxy), 'yellow'))
            # if resp.status_code == 302:
            with threading.Lock():
                good_proxy.append(proxy)
def save_cache():
    with open("proxy_list.txt",'w') as cache_file:
        for i in cache_proxy:
            cache_file.write(i+"\n")
    
def proxy_list(domain):
    threads = []
    get_proxy1()
    get_proxy2()
    if proxy_queue.empty():
        return []
    fecth_proxy = [threading.Thread(target=_fecth,args=(domain,)) for i in range(10)]
    threads.extend(fecth_proxy)
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    save_cache()
    return good_proxy

def check_proxy(domain,proxy_list):
    threads = []
    for i in proxy_list:
        proxy_queue.put(i)
    if proxy_queue.empty():
        return []
    fecth_proxy = [threading.Thread(target=_fecth,args=(domain,)) for i in range(10)]
    threads.extend(fecth_proxy)
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    save_cache()
    return good_proxy
