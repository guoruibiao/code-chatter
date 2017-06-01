# coding: utf8
"""
监听客户端请求，返回相应的执行结果。
"""
import os
from server import Application
from executor import runcode
# from jinja2 import Template

app = Application(__name__)


# 下面开始对于前台的请求做路由控制
@app.route('/')
def index(request):
    """
    可以适当的对首页做下简介。
    """
    print("handler方面：", request)
    # 删除本地临时文件temp.py
    if os.path.exists('./temp.py'):
        os.remove('./temp.py')

    # 也可以尝试使用模板
    with open('./templates/index.html', 'r', encoding="utf8") as f:
        html = f.read()
        f.close()
    yield html.encode('utf8')
    # yield "<h2><strong>It Works.</strong></h2>".encode('utf8')


@app.route('/api/user')
def user(request):
    print(request.params)
    if request.params.get('method', '') == "POST" or request.params.get('method', '')== "GET":
        data = request.params.get('post_data')
        print(data[b'code'][0].decode('utf8'))
        # yield "接口处理相关".encode('utf8')
        # yield data[b'code'][0].decode('utf8').encode('utf8')
        code = data[b'code'][0].decode('utf8')
        result = runcode(code)
        yield result
    else:
        # result = request.params.get('query_string', '')[0].decode('utf8')
        yield "Nothing".encode('utf8')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888)