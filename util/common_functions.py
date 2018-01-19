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


def splist(l, s):
    return [l[i:i + s] for i in range(len(l)) if i % s == 0]
