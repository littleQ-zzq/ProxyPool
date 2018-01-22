from db_connect.redis_connect import redis_conn
from config import config
r = redis_conn(db_n=1)
__author__ = "zhangzhenquan"

"""
此代码用于：
1. 

数据来源：
1.

注意事项：
1.

调用方法：

"""


def get_available_proxy(proxy_key):
    """
    获取可用的代理
    :return:
    """
    proxie_list = []
    proxies = r.lrange(proxy_key, 0, -1)
    for proxy in proxies:
        proxie_list.append(proxy.decode())
    return {"result": proxie_list}


def delete_unavailable_proxy(proxy_list, proxy_key):
    """
    删除不可用代理
    :param proxy_list:
    :return:
    """
    for proxy in proxy_list:
        r.lrem(proxy_key, 0, proxy)
