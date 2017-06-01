# coding: utf8
"""
接受Python脚本，执行相关代码，返回相应结果。
"""

import subprocess
import os


def runcode(data):
    """
    运行前台传过来的Python代码
    """
    # 删除临时文件， 防止上次产生的结果产生影响。
    if os.path.exists('temp.py'):
        os.remove('temp.py')
    with open('temp.py', 'w', encoding='utf8', buffering=1) as f:
        f.write(data)
        f.close()
    # 开启管道，获取执行结果
    process = subprocess.Popen('python temp.py', stdout=subprocess.PIPE)
    data = process.stdout.read()
    del process
    return data
