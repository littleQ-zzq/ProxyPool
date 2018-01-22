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
from config import config

r = redis_conn(db_n=1)
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


def get_total_pages():
    """
    get需要爬取的总页数
    :return:
    """
    html_response = requests.get(url=config.URL_66IP.format("index")).content
    soup = BeautifulSoup(html_response, "lxml")
    tags_aims = soup.select(selector="#PageList > a")
    total_pages = tags_aims[-2].text if tags_aims else 0
    return int(total_pages)


@asyncio.coroutine
def get_proxy_info(index_num, bar_n):
    """
    爬取所有代理并存储
    :param index_num:
    :param bar_n:
    :return:
    """
    text = "bar {}".format(bar_n)
    for page in tqdm(index_num, desc=text, position=bar_n):
        gen_response = yield from session.get(url=config.URL_66IP.format(str(page)))
        html_response = yield from gen_response.read()
        soup = BeautifulSoup(html_response, "lxml")
        tags_aims = soup.select(selector="#main > div > div > table > tr")
        tags_aims = tags_aims[1:]
        for i in range(len(tags_aims)):
            if tags_aims[i]:
                info_list = list(tags_aims[i].strings)
                proxy_ip = info_list[0] + ":" + info_list[1]
                r.lpush(config.PROXY_ALL_66IP_KEY, proxy_ip)
            else:
                logger.warning("Web page is empty")


def get_available_proxies(proxies, r, thread_num, write_lock):
    """
    检测可用的代理并存储
    :param proxies:
    :param r:
    :param thread_num:
    :param write_lock:
    :return:
    """
    tqdm.set_lock(write_lock)
    for proxy_ip in tqdm(proxies, desc="bar{}".format(thread_num), position=thread_num):
        proxie = {"http": proxy_ip.decode(), "https": proxy_ip.decode()}
        try:
            status_code = requests.get(url="http://www.baidu.com", timeout=1, proxies=proxie).status_code
            if status_code == 200:
                logger.info("Available agents：{}".format(proxy_ip))
                r.lpush(config.PROXY_AVAILABLE_66IP_KEY, proxy_ip)
            else:
                logger.info("Not available proxy")
        except:
            logger.info("Not available proxy")


def run_get_all_ips(concurrent_num):
    total_pages = get_total_pages()
    if total_pages:
        r.delete(config.PROXY_ALL_66IP_KEY)
        page_list = list(range(2, total_pages+1)) + ["index"]
        num_list = splist(page_list, total_pages//concurrent_num)
        to_do = []
        for idx, l in enumerate(num_list):
            to_do.append(get_proxy_info(l, idx))
        loop = asyncio.get_event_loop()
        wait_coro = asyncio.wait(to_do)
        loop.run_until_complete(wait_coro)
        loop.close()


def run_get_available_ips(thread_num):
    write_lock = Lock()
    r.delete(config.PROXY_AVAILABLE_66IP_KEY)
    proxies = r.lrange(config.PROXY_ALL_66IP_KEY, 0, -1)
    num_list = splist(proxies, len(proxies) // thread_num)
    for idx, i in enumerate(num_list):
        t = Thread(target=get_available_proxies, args=(i, r, idx, write_lock))
        t.start()


if __name__ == '__main__':
    run_get_all_ips(20)
    run_get_available_ips(50)
