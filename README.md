# dirscan

* 自用目录扫描器、支持单个网站和批量
* 之后有空再增加爬目录生成字典功能，计划使用selenium+phantomjs解析动态js
* 增加python3支持,python2版本不再更新
* 增加建立代理池功能

```
dirscan Jaqen$ dirscan

     _   _          ____
  __| | (_)  _ __  / ___|  ___ __ _ _ __
 / _` | | | | '__| \___ \ / __/ _` | '_  \ __author__="Jaqen"
| (_| | | | | |     ___) | (_| (_| | | | |
 \__,_| |_| |_|    |____/ \___\__,_|_| |_| 
 

Usage: python dirscan.py http://www.xxxx.com dicname,dicname

       python dirscan.py host.ini dicname,dicname

example: python dirscan.py https://www.baidu.com common,php-small
DIC LIST: ['discuz.txt', 'asp-super.txt', 'jeesite.txt', 'aspx-big.txt', 'editor.txt', 'txt.txt', 'hanweb.txt', 'beifen.txt', 'xheditor.txt', 'jsp-small.txt', 'php-small.txt', 'common.txt', 'jsp-big.txt', 'asp-small.txt', 'asp-big.txt', 'fck.txt', 'test.txt', 'dir-big.txt', 'php-super.txt', 'aspx-small.txt', 'other.txt', 'ashx.txt', 'wsdl.txt', 'php-big.txt', 'html.txt', 'ecshop.txt']
```
# 代理功能
1.自动抓取代理。
2.所有抓到的代理保存在缓存文件proxy_list.txt，如果存在就不重新抓取。若要重新抓取请删除缓存文件。
2.针对扫描网址验证代理可用性。
3.使用可用的代理地址进行代理扫描。

# 运行
![](https://github.com/white-cell/dirscan/blob/master/1.jpg)