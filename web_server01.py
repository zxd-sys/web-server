"""
网页服务复打
"""
from socket import *
from select import select
import re


class WebServer:
    def __init__(self, host="0.0.0.0", port=80, html=None):
        self.host = host
        self.port = port
        self.html = html  # 网页根目录
        self.rlist = []
        self.wlist = []
        self.xlist = []
        # 搭建网页服务准备工作
        self.creat_socket()
        self.bind()

    # 创建套接字
    def creat_socket(self):
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setblocking(False)

    # 绑定地址
    def bind(self):
        self.address = (self.host, self.port)
        self.sock.bind(self.address)

    def handle(self, connfd):
        # 接收服务端请求
        request = connfd.recv(1024 * 10).decode()
        # 解析服务端请求
        pattern = "[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern, request)
        if result:
            # 匹配到内容
            info = result.group("info")
            print("请求内容", info)
            self.send_html(connfd, info)
        else:
            connfd.close()
            self.rlist.remove(connfd)
            return

    # 创建发送服务
    def send_html(self, connfd, info):
        if info == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html + info
        try:
            f = open(filename, "rb")
        except:
            # 文件不存在
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            response = response.encode()
        else:
            # 文件存在
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "Content-Length:%d\r\n" % len(data)
            response += "\r\n"
            response = response.encode() + data
        finally:
            # 发送响应给客户端
            connfd.send(response)

    # 启动服务
    def start(self):
        self.sock.listen(5)
        print('listen the port %d' % self.port)
        self.rlist.append(self.sock)
        # 循环监控
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sock:
                    connfd, addr = r.accept()
                    print("connect from", addr)
                    connfd.setblocking(False)
                    # 客户端链接套接字放入监控列表中
                    self.rlist.append(connfd)
                else:
                    try:
                        self.handle(r)
                    except:
                        r.close()
                        self.rlist.remove(r)


if __name__ == '__main__':
    # 实例化对象
    httpd = WebServer(host="0.0.0.0", port=22223, html="./static")
    # 启动服务
    httpd.start()
