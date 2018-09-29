#!/usr/bin/python3
#coding = utf-8

from socket import *
import sys
import getpass

#创建网络连接
def main():
    if len(sys.argv) < 3:
        print('argv is error')
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    sockfd = socket()
    try:
        sockfd.connect((HOST,PORT))
    except Exception as e:
        print(e)
        return
    while 1:
        print('''
            +-------------------+
            |--1.注册           |
            |--2.登录           |
            |--3.退出           |
            +-------------------+
            ''')
        try:
            cmd = int(input('请输入选项：'))
        except Exception as e:
            print("命令错误")
            continue

        if cmd not in [1,2,3]:
            print('请输入正确选项')
            sys.stdin.flush()#清除标准输入
            continue
        elif cmd == 1:
            r = do_register(sockfd)
            if r == 0:
                print("注册成功")
                login(sockfd,name)  #进入二级界面
            elif r == 1:
                print("用户存在")
            else:
                print("注册失败")
        elif cmd == 2:
            name = do_login(sockfd)
            if name:
                print("登录成功")
                login(sockfd,name)
            else:
                print("用户名或密码不正确")
        elif cmd == 3:
            sockfd.send(b'E')
            sys.exit('谢谢使用')

def do_register(sockfd):
    while 1:
        name = input("User:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass('Again:')

        if (' 'in name) or (' ' in passwd):
            print("用户名和密码不许有空格")
            continue
        if passwd != passwd1:
            print("两次密码不一致")
            continue

        msg = 'R {} {}'.format(name,passwd)
        #发送请求
        sockfd.send(msg.encode())
        #等待回复
        data = sockfd.recv(1024).decode()
        if data == 'OK':
            return 0
        elif data == "EXISTS":
            return 1
        else:
            return 2

def do_login(sockfd):
    name = input('User:')
    passwd = getpass.getpass()
    msg = "L {} {}".format(name,passwd)
    sockfd.send(msg.encode())
    data = sockfd.recv(1024).decode()

    if data == "OK":
        return name
    else:
        return

def login(sockfd,name):
    while 1:
        print('''
            +------------------+
            |--1.查询　　　　　　　　　　｜
            |--2.历史记录　　　　　　｜
            |--3.退出　　　　　　　　　　｜
            +------------------+
            ''')

        try:
            cmd = int(input('请输入选项：'))
        except Exception as e:
            print("命令错误")
            continue

        if cmd not in [1,2,3]:
            print('请输入正确选项')
            sys.stdin.flush()#清除标准输入
            continue
        elif cmd == 1:
            do_query(sockfd,name)
        elif cmd == 2:
            do_hist(sockfd,name)
        elif cmd == 3:
            return

def do_query(sockfd,name):
    while 1:
        word = input('单词：')
        if word == '##':
            break
        msg = 'Q {} {}'.format(name,word)
        sockfd.send(msg.encode())
        data = sockfd.recv(1024).decode()
        if data == 'OK':
            data = sockfd.recv(2048).decode()
            print(data)
        else:
            print("没有查到该单词")
def do_hist(sockfd,name):
    msg = 'H {}'.format(name)
    sockfd.send(msg.encode())
    data = sockfd.recv(1024).decode()
    if data == 'OK':
        while 1:
            data = sockfd.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("没有历史记录")

if __name__ == "__main__":
    main()