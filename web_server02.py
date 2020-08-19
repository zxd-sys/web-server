"""
web_server
"""
from socket import *
from select import select
import re


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, html=None):
        self.host = host
        self.port = port
        self.html = html
        self.rlist = []
        self.wlist = []
        self.xlist = []
        # 创建web服务器准备工作
        self.creat_socket()
        self.bind()

    # 创建tcp套接字
    def creat_socket(self):
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 将套接字设为非阻塞状态
        self.sock.setblocking(False)

    # 绑定地址
    def bind(self):
        self.address = (self.host, self.port)
        self.sock.bind(self.address)

    def handle(self, connfd):
        # 接收客户端请求
        request = connfd.recv(1024 * 10).decode()
        # 解析客户端请求
        pattern = "[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern, request)
        if result:
            # 匹配到的内容
            info = result.group("info")
            print("请求内容:", info)
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
            response += "<hi>Sorry...</h1>"
            response = response.encode()
        else:
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "Content-Length:%d\r\n" % len(data)
            response += "\r\n"
            response = response.encode() + data
        finally:
            connfd.send(response)

    # 创建启动函数
    def start(self):
        # 设置监听
        self.sock.listen(5)
        print("listen the port %d" % self.port)
        # 循环监控,初始监控监听套接字
        self.rlist.append(self.sock)
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sock:
                    connfd, addr = r.accept()
                    print("connect from", addr)
                    connfd.setblocking(False)
                    # 将客户端套接字添加进监听列表
                    self.rlist.append(connfd)
                else:
                    try:
                        self.handle(r)
                    except:
                        r.close()
                        self.rlist.remove(r)


if __name__ == '__main__':
    # 实例化对象
    httpd = WebServer(host="0.0.0.0", port=8005, html="./static")
    # 启动服务
    httpd.start()
