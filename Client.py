#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import ssl
import sys
import base64
import time


def get_err_dict():
    err_dict = {
        '500': 'Syntax error, command unrecognized',
        '501': 'Syntax error in parameters of arguments',
        '502': 'Command not implemented',
        '503': 'Bad sequence of commands',
        '504': 'Command parameter not implemented',
        '211': 'System status, or system help reply',
        '214': 'Help message',
        '220': '<domain> Service ready',
        '221': '<domain> Service closing transmission channel',
        '421': '<domain> Service not available, closing transmission channel',
        '250': 'Requested mail action okay, completed',
        '251': 'User not local',
        '252': 'Cannot VRFY user, but will accept message and attempt delivery',
        '455': 'Server unable to accommodate parameters',
        '555': 'MAIL FROM/RCPT TO parameters not recognized or not implemented',
        '450': 'Requested mail action not taken: mailbox unavailable',
        '550': 'Requested action not taken: mailbox unavailable',
        '451': 'Requested action aborted: error in processing',
        '551': 'User not local; please try <forward-path>',
        '452': 'Requested action not taken: insufficient system storage',
        '552': 'Requested mail action aborted: exceeded storage allocation',
        '553': 'Requested action not taken: mailbox name not allowed',
        '354': 'Start mail input; end with <CRLF>.<CRLF>',
        '554': 'Transaction failed',
        '334': 'Go on',
        '235': 'Successful authorisation',
        '535': 'Username and Password not accepted',
        'wrong host or port': 'wrong host or port'
    }
    return err_dict


def err_proc_log(err_code, query):
    err_dict = get_err_dict()
    log_file = open('log.txt', 'a')
    log_file.write(query+'\n'+'\r')
    log_file.write(err_code + ' ' + str(err_dict[err_code]) + '\n' + '\r')
    log_file.close()


def err_handling(err_code):
    err_dict = get_err_dict()
    print(err_dict[err_code])
    time.sleep(5)
    conn.close()
    sys.exit()


def code_check(err_code,query):
    err_proc_log(err_code,query)
    if err_code[0] == '5' or err_code[0] == '4' or err_code == '221':
        err_handling(err_code)


#  "smtp.gmail.com" Host нашего сервера
#  465 Порт для подключения(SSL)


buff = bytearray()
code = str()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создаём сокет для наших нужд
sock.settimeout(180)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)  # Получаем контекст(?) для сокета



HOST = input('Enter your host: ')
try:
    PORT = int(input('Enter your port: '))
except ValueError :
    err_proc_log('wrong host or port',str(PORT))
    print('Wrong host or port')
    time.sleep(3)
    sys.exit()
try:
    conn = context.wrap_socket(sock, server_hostname=HOST)  # Оборачиваем(?) сокет в контекст
    conn.connect((HOST, PORT))
except Exception:
    err_proc_log('wrong host or port',HOST)
    print('Wrong host or port')
    time.sleep(3)
    sys.exit()

conn.send(bytearray('helo '+HOST+'\r\n', encoding='utf8'))
code = str(conn.recv().decode()[0:3])
code_check(code,str('helo '+HOST))
conn.send(bytearray('auth login\r\n', encoding='utf8'))
code = str(conn.recv().decode()[0:3])
code_check(code,str('auth login'))
login = base64.b64encode(bytes(input("Enter your login: "), encoding='utf8'))
conn.send(bytearray(str(login.decode('utf8')) + "\r\n", encoding='utf8'))
code = str(conn.recv().decode()[0:3])
code_check(code,"Enter your login: ")
pas = base64.b64encode(bytes(input("Enter your pass: "), encoding='utf8'))
conn.send(bytearray(str(pas.decode('utf8')) + "\r\n", encoding='utf8'))
code = str(conn.recv().decode()[0:3])
code_check(code, "Enter your pass: ")
if input('Would you like to type commands by yourself?(enter y if so)') == 'y':
    in_custom_mode = bool(True)
else:
    in_custom_mode = bool(False)

while not in_custom_mode:
    conn.send(bytearray('mail from: ' + input('What is your address(use <some@mail.com>)?:') + '\r\n', encoding='utf8'))
    code = str(conn.recv().decode()[0:3])
    code_check(code,'mail from: + adress')
    conn.send(bytearray('rcpt to: ' + input("Who would you like to write to(use <some@mail.com>)?:")+"\r\n", encoding='utf8'))
    code = str(conn.recv().decode()[0:3])
    code_check(code,'rcpt to: + adress')
    print("Enter your message text ending up with coma all alone on the string after an empty string: ")
    conn.send(bytearray('data\r\n', encoding='utf8'))
    code = str(conn.recv().decode()[0:3])
    code_check(code,'data')
    while (1):
        buff = bytearray(input() + "\r" + "\n", encoding='utf8')
        conn.send(buff)
        if bytearray('.' + "\r" + '\n', encoding='utf8') == buff:
            code = str(conn.recv().decode()[0:3])
            code_check(code,'.')
            code = str(conn.recv().decode()[0:3])
            code = code
            if code == '250':
                print("Successfully sent!"+"\r"+"\n")
            break
    if input("Print 'yes' if you want to send another message:") != 'yes':
        break

while(in_custom_mode):
    if code[0] == '5' or code[0] == '4' or code == '221':
        err_handling(code)
    if code != '354':
        buff = bytearray(input() + "\r" + "\n", encoding='utf8')
        temp = str(buff.decode('utf8'))
        conn.send(buff)
    else:
        while(1):
            buff = bytearray(input() + "\r" + "\n", encoding='utf8')
            conn.send(buff)
            if bytearray('.'+"\r"+'\n', encoding='utf8') == buff:
                break
    buff = conn.recv().decode()
    code = str(buff[0:3])
    print(buff)
    err_proc_log(code,str(temp))
conn.send(bytearray('quit\r\n', encoding='utf8'))
err_proc_log(str(conn.recv().decode()[0:3]),'End of session')
print("Goodbye!")
time.sleep(1)
conn.close()
sys.exit()






