import requests
import redis
from threading import Thread, Lock
from bs4 import BeautifulSoup
from tqdm import tqdm
import asyncio
import aiohttp
import time

session = aiohttp.ClientSession()
pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
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
URL_KUAIDAILI = "https://www.kuaidaili.com/free/inha/{}/"


@asyncio.coroutine
def get_total_pages():
    gen_response = yield from session.get(url=URL_KUAIDAILI.format("1"))
    html_response = yield from gen_response.read()
    soup = BeautifulSoup(html_response, "lxml")
    tags_aims = soup.select(selector="#listnav > ul > li > a")
    total_pages = tags_aims[-1].text if tags_aims else 0

    return total_pages


@asyncio.coroutine
def get_proxy_info(start_idx, end_idx, bar_n):
    time.sleep(0.5)
    text = "bar {}".format(bar_n)
    for page in tqdm(range(start_idx, int(end_idx)+1), desc=text, position=bar_n):
        gen_response = yield from session.get(url=URL_KUAIDAILI.format(str(page)))
        html_response = yield from gen_response.read()
        soup = BeautifulSoup(html_response, "lxml")
        tags_aims = soup.select(selector="#list > table > tbody > tr")
        for i in range(len(tags_aims)):
            if tags_aims[i]:
                info_list = list(tags_aims[i].strings)
                proxy_ip = info_list[1] + info_list[3]
                r.lpush("proxy_ips", proxy_ip)
            else:
                pass


def run():
    loop = asyncio.get_event_loop()
    to_do = [get_proxy_info(1, 200, 0), get_proxy_info(200, 400, 1)]
    wait_coro = asyncio.wait(to_do)
    loop.run_until_complete(wait_coro)
    loop.close()


if __name__ == '__main__':
    run()

