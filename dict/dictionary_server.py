'''
name : Tedu
date : 2018-10-1
email : xxx
modules : pymongo
This is a dict project for AID
'''

from socket import *
import os
import time
import signal
import pymysql
import sys

#定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 16688
ADDR = (HOST,PORT)

#流程控制
def main():
    #创建数据库连接
    db = pymysql.connect('localhost','root',
        '123456','dictionary')

    #创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    #忽略子进程信号
    signal.signal(signal.SIGCHLD,
        signal.SIG_IGN)
    while 1:
        try:
            connfd,addr = sockfd.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue

        #创建子进程
        pid = os.fork()
        if pid == 0:
            sockfd.close()
            do_child(connfd,db)
        else:
            connfd.close()
            continue

def do_child(connfd,db):
    #循环接收客户端请求
    while 1:
        data = connfd.recv(1024).decode()
        print(connfd.getpeername(),':',data)
        if (not data) or data[0] == 'E':
            connfd.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(connfd,db,data)
        elif data[0] == 'L':
            do_login(connfd,db,data)
        elif data[0] == 'Q':
            do_query(connfd,db,data)
        elif data[0] == 'H':
            do_hist(connfd,db,data)


def do_login(connfd,db,data):
    print('登录操作')
    l = data.split(" ")
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s' \
    and passwd='%s'"%(name,passwd)

    cursor.execute(sql)
    r = cursor.fetchone()

    if r == None:
        connfd.send(b'FALL')
    else:
        print('%s登录成功'%name)
        connfd.send(b'OK')

def do_register(connfd,db,data):
    print("注册操作")
    l = data.split(" ")
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s'"%name
    cursor.execute(sql)
    r = cursor.fetchone()

    if r != None:
        connfd.send(b'EXISTS')
        return
    #用户不存在插入用户
    sql = "insert into user (name,passwd) \
    values ('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        connfd.send(b'OK')
    except:
        db.rollback()
        connfd.send(b'FALL')
    else:
        print("%s注册成功"%name)

def do_query(connfd,db,data):
    print("查询操作")
    l = data.split(" ")
    name = l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()

        sql = "insert into hist (name,word,time) \
        values('%s','%s','%s')"%(name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    #文本查询
    try:
        f = open(DICT_TEXT)
    except:
        connfd.send(b'FALL')
        return

    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'FALL')
            f.close()
            return
        elif tmp == word:
            connfd.send(b'OK')
            time.sleep(0.1)
            connfd.send(line.encode())
            f.close()
            insert_history()
            return
    connfd.send(b'FALL')
    f.close()


def do_host():
    print('历史记录')
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()

    sql = "select * from hist where name='%s'"%name
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        connfd.send(b'FALL')
        return
    else:
        connfd.send(b'OK')

    for i in r:
        time.sleep(0.1)
        msg = "%s    %s    %s"%(i[1],i[2],1[3])
        connfd.send(msg.encode())
    time.sleep(0.1)
    connfd.send(b'##')

if __name__ == '__main__':
    main()