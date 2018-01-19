from flask import Flask

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
app = Flask(__name__)
app.config.update(dict(
    DEBUG=False,
    SECRET_KEY='j\xa0\xac\xe6\xa5\xda{"\x93\x02\x90z\xab}0\xdf&\xfc\x87\xb4\x89\x94\x0b\xa5'
))


if __name__ == "__main__":

    # 生成secret_key,可能会出现乱码
    import os
    secret_key = os.urandom(24)

