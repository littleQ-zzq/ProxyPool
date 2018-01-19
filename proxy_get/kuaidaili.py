import requests
import redis
from threading import Thread, Lock
from bs4 import BeautifulSoup
from tqdm import tqdm
import socket
import time
socket.setdefaulttimeout(10)
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


def get_total_pages():
    response = requests.get(url=URL_KUAIDAILI.format("1"))
    soup = BeautifulSoup(response.content, "lxml")
    tags_aims = soup.select(selector="#listnav > ul > li > a")
    total_pages = tags_aims[-1].text if tags_aims else 0
    response.close()

    return total_pages


def get_proxy_info(start_idx, end_idx, thread_n, write_lock):
    tqdm.set_lock(write_lock)
    text = "bar {}".format(thread_n)
    for page in tqdm(range(start_idx, int(end_idx)+1), desc=text, position=thread_n, leave=False):
        time.sleep(0.5)
        response = requests.get(url=URL_KUAIDAILI.format(str(page)))
        soup = BeautifulSoup(response.content, "lxml")
        tags_aims = soup.select(selector="#list > table > tbody > tr")
        for i in range(len(tags_aims)):
            if tags_aims[i]:
                info_list = list(tags_aims[i].strings)
                proxy_ip = info_list[1] + info_list[3]
                r.lpush("proxy_ips", proxy_ip)
            else:
                pass
        response.close()


def run():
    write_lock = Lock()
    t0 = Thread(target=get_proxy_info, args=(1, 200, 0, write_lock))
    t1 = Thread(target=get_proxy_info, args=(200, 400, 1, write_lock))
    t2 = Thread(target=get_proxy_info, args=(400, 600, 2, write_lock))
    t3 = Thread(target=get_proxy_info, args=(600, 800, 3, write_lock))
    t4 = Thread(target=get_proxy_info, args=(800, 1000, 4, write_lock))

    thread_list = [t0, t1, t2, t3, t4]
    for i in thread_list:
        i.start()


if __name__ == '__main__':
    run()

