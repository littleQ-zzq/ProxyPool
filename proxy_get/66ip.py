import asyncio
import time
from threading import Thread, Lock

import aiohttp
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from util.log import logger
from db_connect.redis_connect import redis_conn
from util.common_functions import splist

session = aiohttp.ClientSession()

__author__ = "zhangzhenquan"

"""
此代码用于：
1. 抓取代理网站上的代理ip

数据来源：
1.

注意事项：
1.

调用方法：

"""
URL_66IP = "http://www.66ip.cn/{}.html"
PROXY_ALL_IP_KEY = "proxy_66ips"
PROXY_AVAILABLE_IP_KEY = "proxy_available_66ips"


def get_total_pages():
    html_response = requests.get(url=URL_66IP.format("index")).content
    soup = BeautifulSoup(html_response, "lxml")
    tags_aims = soup.select(selector="#PageList > a")
    total_pages = tags_aims[-2].text if tags_aims else 0
    return int(total_pages)


@asyncio.coroutine
def get_proxy_info(index_num, bar_n):
    r = redis_conn()
    r.delete(PROXY_ALL_IP_KEY)
    text = "bar {}".format(bar_n)
    for page in tqdm(index_num, desc=text, position=bar_n):
        gen_response = yield from session.get(url=URL_66IP.format(str(page)))
        html_response = yield from gen_response.read()
        soup = BeautifulSoup(html_response, "lxml")
        tags_aims = soup.select(selector="#main > div > div > table > tr")
        tags_aims = tags_aims[1:]
        for i in range(len(tags_aims)):
            if tags_aims[i]:
                info_list = list(tags_aims[i].strings)
                proxy_ip = info_list[0] + ":" + info_list[1]
                r.lpush(PROXY_ALL_IP_KEY, proxy_ip)
            else:
                logger.warning("Web page is empty")


def get_available_proxies(proxies, r, thread_num, write_lock):
    tqdm.set_lock(write_lock)
    for proxy_ip in tqdm(proxies, desc="bar{}".format(thread_num), position=thread_num):
        proxie = {"http": proxy_ip.decode(), "https": proxy_ip.decode()}
        try:
            status_code = requests.get(url="http://www.baidu.com", timeout=1, proxies=proxie).status_code
            if status_code == 200:
                logger.info("Available agents：{}".format(proxy_ip))
                r.lpush(PROXY_AVAILABLE_IP_KEY, proxy_ip)
            else:
                logger.info("Not available proxy")
        except:
            logger.info("Not available proxy")


def run_get_all_ips():
    total_pages = get_total_pages( )
    if total_pages:
        page_list = list(range(2, total_pages+1)) + ["index"]
        num_list = splist(page_list, total_pages//10)
        to_do = []
        for idx, l in enumerate(num_list):
            to_do.append(get_proxy_info(l, idx))
        loop = asyncio.get_event_loop()
        wait_coro = asyncio.wait(to_do)
        loop.run_until_complete(wait_coro)
        loop.close()


def run_get_available_ips():
    write_lock = Lock()
    r = redis_conn()
    r.delete(PROXY_AVAILABLE_IP_KEY)
    proxies = r.lrange(PROXY_ALL_IP_KEY, 0, r.llen(PROXY_ALL_IP_KEY))
    num_list = splist(proxies, len(proxies) // 10)
    for idx, i in enumerate(num_list):
        t = Thread(target=get_available_proxies, args=(i, r, idx, write_lock))
        t.start()


if __name__ == '__main__':
    run_get_all_ips()
    run_get_available_ips()
