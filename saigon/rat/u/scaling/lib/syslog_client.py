'''
Created on Nov 4, 2010

Python syslog client.

1. this code must work with a working syslog server.

HOW TO:

Syslog server setup:

1. Install syslog server on either Windows or Linux machine
2. Download MT_syslog.exe (Windows) from Perforce server /tool/rat-common/download
3. Or, download TFTPd32.exe from http://tftpd32.jounin.net/tftpd32_download.html
4. Enable syslog daemon and create a log file for syslog server
5. done

example:
syslog(host='127.0.0.1',message='I am a syslog message')

@author: webber.lin
'''


import socket
import time


FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

SERVITY = {
    'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}

def createTimeFormat():
    '''
    ISOTIMEFORMAT='%Y-%m-%d %X'
    time.strftime( ISOTIMEFORMAT,time.localtime(time.time()))
    '2010-11-05 15:31:25'
    '''
    return time.strftime( '%Y-%m-%d %X',time.localtime(time.time()))

def syslog(message, servity=SERVITY,skey='info', facility=FACILITY,fkey='daemon',host='172.17.19.201', port=514,source_ip='172.17.18.40'):
    '''
    Send syslog UDP packet to given host and port.
    example:
    syslog(message='I am syslog client',host='172.17.16.68',port=514,source_ip='172.17.18.40')
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #with time format
        #rec_time=createTimeFormat()
        #data = '%s[Source_IP(%s):%s.%s] message:%s' % (rec_time,source_ip,skey, fkey,message) 
        #without time format
        data = '[Source_IP(%s):%s.%s] message:%s' % (source_ip,skey, fkey,message) 
        #data = '<%d>%s' % (servity + facility*8, message)
        sock.sendto(data, (host, port))
        sock.close()
    except:
        raise Exception("Error: unable to send message to Syslog Server: %s" % host)
