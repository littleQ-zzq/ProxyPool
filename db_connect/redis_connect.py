import redis
from tqdm import tqdm

from config import config
from util.log import logger
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


def redis_conn(host=config.REDIS_IP, port=config.REDIS_PORT, db_n=0):
    pool = redis.ConnectionPool(host=host, port=port, db=db_n)
    r = redis.StrictRedis(connection_pool=pool)

    return r

if __name__ == '__main__':
    r = redis_conn()
    r.delete("test_list")
    for i in tqdm(range(100), desc="process"):
        r.lpush("test_list", i)
    logger.info("the lenth of test_list is {}".format(r.llen("test_list")))
