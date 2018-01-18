import requests
import redis
from bs4 import BeautifulSoup
from tqdm import tqdm
import asyncio
import aiohttp
import time

from log import logger

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
URL_66IP = "http://www.66ip.cn/{}.html"


def get_total_pages():
    html_response = requests.get(url=URL_66IP.format("index")).content
    soup = BeautifulSoup(html_response, "lxml")
    tags_aims = soup.select(selector="#PageList > a")
    total_pages = tags_aims[-2].text if tags_aims else 0

    return int(total_pages)


@asyncio.coroutine
def get_proxy_info(index_num, bar_n):
    total_count = 0
    time.sleep(0.5)
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
                proxie = {"http": proxy_ip, "https": proxy_ip}
                try:
                    status_code = requests.get(url="http://www.baidu.com", timeout=1, proxies=proxie).status_code
                    if status_code == 200:
                        total_count += 1
                        logger.info("Available agents：{}".format(proxy_ip))
                        r.lpush("proxy_66ips", proxy_ip)
                    else:
                        logger.info("Not available proxy")
                except:
                    logger.info("Not available proxy")
            else:
                logger.warning("Web page is empty")
    logger.info("total usable proxy: {}".format(total_count))


def splist(l, s):
    return [l[i:i + s] for i in range(len(l)) if i % s == 0]


def run():
    total_pages = get_total_pages()
    page_list = list(range(2, total_pages+1)) + ["index"]
    num_list = splist(page_list, total_pages//10)
    to_do = []
    for idx, l in enumerate(num_list):
        to_do.append(get_proxy_info(l, idx))
    loop = asyncio.get_event_loop()
    wait_coro = asyncio.wait(to_do)
    loop.run_until_complete(wait_coro)
    loop.close()


if __name__ == '__main__':
    run()
