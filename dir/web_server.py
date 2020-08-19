"""
web_server 程序搭建一个类
展示自己的网页
"""
from socket import *
from select import select
import re


# 搭建比并发服务,实现http功能
class WebServer:
    def __init__(self, host="0.0.0.0", port=80, html=None):
        self.host = host
        self.port = port
        self.html = html  # 网页的根目录
        self.rlist = []
        self.wlist = []
        self.xlist = []
        # 搭建服务的准备工作
        self.create_socket()
        self.bind()

    def create_socket(self):
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setblocking(False)

    def bind(self):
        self.address = (self.host, self.port)
        self.sock.bind(self.address)

    # 实现http功能
    def handle(self, connfd):
        # 接收浏览器请求
        request = connfd.recv(1024 * 10).decode()
        # 解析请求 --> 获取请求内容
        pattern = "[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern, request)
        if result:
            # 匹配到内容
            info = result.group("info")
            print("请求内容:", info)
            # 发送响应数据
            self.send_html(connfd, info)
        else:
            # 没有匹配到内容,客户端断开
            connfd.close()
            self.rlist.remove(connfd)
            return

    # 根据请求发送响应数据
    def send_html(self, connfd, info):
        if info == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html + info
        try:
            f = open(filename,"rb")
        except:
            # 文件不存在
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            response = response.encode()
        else:
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "Content-Length:%d\r\n"%len(data)
            response += "\r\n"
            response = response.encode()+ data
        finally:
            # 发送响应该客户端
            connfd.send(response)


    # 启动服务
    def start(self):
        self.sock.listen(5)
        print("Listen the port %d" % self.port)
        self.rlist = [self.sock]
        while True:
            # 循环监控
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            # 伴随监控的IO的增多,就绪的IO情况也会复杂化
            # 分类讨论 分成两类 sock   ---   connfd
            for r in rs:
                # 有客户端链接
                if r is self.sock:
                    connfd, addr = r.accept()
                    print("connect from", addr)
                    connfd.setblocking(False)
                    self.rlist.append(connfd)  # 客户端链接套接字放入监控列表中
                else:
                    # 某个客户端发消息了
                    try:
                        self.handle(r)
                    except:
                        r.close()
                        self.rlist.remove(r)


if __name__ == '__main__':
    # 实例化对象
    httpd = WebServer(host="0.0.0.0", port=8000, html="./static")
    # 启动服务
    httpd.start()
