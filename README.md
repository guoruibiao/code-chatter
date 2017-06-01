# code-chatter
重写一个类似于Flask路由控制的后台，与前台通信（给代码，输出执行结果）。

---


## 前言
这两天老是做梦，全根Python有关，这不昨晚梦见我把Python做成了类似于JavaScript一样的功能，在前端混的风生水起。结果是个梦。。。。。。

在第一次接触了Flask之后，就被它优雅的路由映射给俘获了。后来我自己又搜索了相关的知识点，算是勉强做出一个最最简化的版本。详细的内容可以查看我的这篇文章。
http://blog.csdn.net/marksinoberg/article/details/72811360


关于昨晚的梦，早上醒来倒是给了我一个灵感，为什么不能做出一个**代码聊天室**呢？ 说着可能有点让人摸不着头脑，其实说白了，就是一个本地的代码执行环境。大致的模样应该是这个样子的。

![代码聊天室](http://img.blog.csdn.net/20170601085033254?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTWFya3Npbm9iZXJn/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)


## “框架”？

### 项目目录及各自功能
说到底，这根本不能算是一个框架，充其量也只能是一个工具集吧。项目目录也比较简单。如下：

```
C:\Users\biao\Desktop\笔记\code-chatter>tree /f .
文件夹 PATH 列表
卷序列号为 E0C6-0F15
C:\USERS\BIAO\DESKTOP\笔记\CODE-CHATTER
│  .gitignore
│  backend.py              # 服务后台
│  executor.py             # 客户端代码执行工具
│  server.py               # 后台web应用处理器
│  temp.py                 # 客户端临时代码存放
│  test.py                 # 测试相关文件
│
├─templates
│      index.css
│      index.html
│      index.js
│      jquery-2.2.4.min.js
└─
```

### 流程图
大致来说，软件工作的流程如下：
![软件工作流程图](http://img.blog.csdn.net/20170601085508513?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTWFya3Npbm9iZXJn/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)


由于作图工具的问题，原本应该双向交互的对象只画出了单个箭头。不过看到这个图后，这个软件的工作流程应该就不难理解了。

## 后端
基本上来说后端是重中之重啦。接下来一一的介绍一下吧。

### server
按照**WSGI**标准， 一个WEB应用程序或者框架应该满足如下条件：
 - 本身为一个对象（函数，类init，对象call）
 - 有env, start_response两个参数（当然名字可以不固定）
 - 返回对象可迭代

我这里借助了对象的形式来实现，在**`__call__`**方法中添加了处理逻辑。

```
def __call__(self, env, start_response):
        """
        根据WSGI标准，web应用程序需要包含两个参数：
        @param env : 一个包含了请求内容的字典
        @param start_response ： 开始处理来自客户端的请求
        """
        path = env["PATH_INFO"]
        if path in self.routes:
            # 路由映射函数已知
            status = '200 OK'
            headers = [('Content-Type', 'text/html;charset=UTF-8')]
            # print(env)
            # 对来自客户端的请求做封装处理
            request_method = env.get("REQUEST_METHOD", "")
            print("***"*28, request_method)
            if request_method == "POST":
                content_length = int(env.get('CONTENT_LENGTH', 0))
                form_data = parse_qs(env.get('wsgi.input', '').read(content_length))
                self.request.add(key='method', value="POST")
                # TODO 或许在这里处理一下来自用户请求的数据，比如escape防止脚本攻击
                self.request.add(key='post_data', value=form_data)
            elif request_method == "GET":
                self.request.add(key='method', value=request_method)
                query_string = env.get('QUERY_STRING', '')
                self.request.add(key='query_string', value=query_string)
            start_response(status, headers)
            return self.routes[path](self.request)
        else:
            # 处理函数不包含在路由控制器内
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html;charset=UTF-8')]
            start_response(status, headers)
            return ["No handler match for `{}`".format(path).encode('utf8')]
```

### backend
后台存在的意义就是路由映射以及监听客户端请求，并将与请求对应的处理函数进行转发处理。
总的来说类似于一个**控制器**，或者**中间件**。用过**Flask**的童鞋可能会非常容易的理解下面代码的作用了。没用过的话也应该能见名之意。

```
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
    # 也可以尝试使用模板
    with open('./templates/index.html', 'r', encoding="utf8") as f:
        html = f.read()
        f.close()
    yield html.encode('utf8')
    
@app.route('/api/user')
def user(request):
    print(request.params)
    if request.params.get('method', '') == "POST" or request.params.get('method', '')== "GET":
        data = request.params.get('post_data')
        print(data[b'code'][0].decode('utf8'))
        # yield "接口处理相关".encode('utf8')
        code = data[b'code'][0].decode('utf8')
        result = runcode(code)
        yield result
    else:
        yield "Nothing".encode('utf8')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888)
```

通过**装饰器**就可以实现非常方便的路由映射，结合server的分发处理，就可以实现针对不同的路径实现不同的功能了。



### exector
临时代码执行这块稍微有点问题，经过测试，我发现使用**subprocess.Popen()**并不是一个很好的解决办法。具体表现在：
> 临时文件清理工作不够及时，不够彻底。

有待进一步改进。

目前版本也只是够用。。。。。。

```
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

```


## 前端
前端我的思路就是利用**ajax**实现前后端的分离逻辑。让页面和数据处理分离开来，更高效的处理各自的事物。

### ajax

为了验证方便性，我用原生的JavaScript和JQuery分别作了实现，发现还是JQuery好用啊，让我们可以更专注于事物的处理而不是纠结于控制结构上。(⊙﹏⊙)b


```
function send() {
        // 先获取文本域内的代码值
        var sourcecode = $("#sourcecode").val();
        // var sourcecode = document.getElementById("sourcecode").value;
        // 借助ajax实现功能获取
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                console.log(xhr.responseText)
            }
        }
        xhr.open('post', '/api/user')
        xhr.send({ 'code': sourcecode })
    }

    function send2(){
        // 更新聊天页面
        update_chat();
        // 请求代码执行结果
        $.ajax({
            url: '/api/user',
            type: "POST",
            dataType: "json",
            async: true,
            data: {'code': $("#sourcecode").val()},
            success: function(response){
                console.log("Success.")
                console.log(response)
                // console.log(response.responseText);
                // eval('var data = '+ response.responseText)
                // result = response.responseText
                update_robot(response.content);
            },
            error: function(msg){
                console.log("Error.")
                console.log(msg.responseText);
                result = msg.responseText;
                update_robot(result);
            }
        })
        // document.getElementById("sourcecode").value = "";
        // 更新滚动条，以便于自动上划。
        scroll_top();
    }
```

### 页面更新
这里页面更新的触发时机应该是每次点击完**发送**按钮之后，所以只需要在按钮的响应函数里面添加相应的逻辑即可。

```
function update_chat(){
        console.log("Ready to append mywords.")
        // 先创建本人说话的内容节点
        var source = $("#sourcecode").val();
        // http://avatar.csdn.net/0/8/F/3_marksinoberg.jpg
        child_node = "<div class='mywords'><img src='http://avatar.csdn.net/0/8/F/3_marksinoberg.jpg'><span>"+source+"</span><br /><br /></div>"
        var mywords = $(child_node);
        $("#lefttop").append(mywords);
    }


    function update_robot(result){
        console.log('更新聊天机器人代码执行结果。')
        // 创建代码返回结果的节点
        child_node = "<br /><br /><div class='robot'><span>"+result+"</span><img src='http://avatar.csdn.net/0/B/4/1_yangwei19680827.jpg'></div>"
        var robot_words = $(child_node);
        $("#lefttop").append(robot_words);
    }

    // 页面自动上划
    function scroll_top(){
        var messagebox = document.getElementById("lefttop");
        messagebox.scrollTop = messagebox.scrollHeight-messagebox.style.height;
    }
```

## 演示
下面来看几个图片，聊表心意。

### 简易“应答”模式
![简易应答模式](http://img.blog.csdn.net/20170601091334673?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTWFya3Npbm9iZXJn/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

### “代理模式”处理外部请求
![代理模式处理外部请求](http://img.blog.csdn.net/20170601091354642?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTWFya3Npbm9iZXJn/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

### 后台日志
![后台日志监测](http://img.blog.csdn.net/20170601091415454?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvTWFya3Npbm9iZXJn/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

---

## 总结

已知问题：

 - make_server 本身的处理问题。
 - temp.py临时文件更新问题
 - 静态文件路径处理的不是很好(⊙﹏⊙)b

---

完整代码可以到我的GitHub上进行download。

https://github.com/guoruibiao/code-chatter
