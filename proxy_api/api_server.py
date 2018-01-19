from flask import jsonify
from proxy_api import *
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


@app.route("/")
def hello_word():
    return jsonify({"name": "flask", "version": "0.12.2"})


if __name__ == '__main__':
    app.run("0.0.0.0", 1234)
