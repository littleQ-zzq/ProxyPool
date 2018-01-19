from flask import jsonify, request
from proxy_api import *
from proxy_api.api_proxy import *
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


@app.route("/server/get_available_proxy")
def api_get_available_proxy():
    proxy_key = request.args.get("proxy_key", [])
    res = get_available_proxy(proxy_key)
    return jsonify(res)


@app.route("/server/delete_unavailable_proxy", methods=["GET", "POST"])
def api_delete_unavailable_proxy():
    params = request.json
    proxy_key = params.get("proxy_key", "unknow_list")
    proxy_list = params.get("proxy_list", [])
    delete_unavailable_proxy(proxy_list, proxy_key)
    return jsonify({"status": "finished"})

if __name__ == '__main__':
    app.run("0.0.0.0", 1234)
