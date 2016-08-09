#coding:utf-8

from IPy import IP

ip_s = raw_input("Please input an IP or net-range: ")

ips = IP(ip_s)
if len(ips) > 1: #为一个网络地址
    print ("net: %s" % ips.net()) #输出网络地址
    print ("netmask: %s" % ips.netmask()) #输出网络地址掩码
    print ("broadcast: %s " % ips.broadcast()) #输出网络广播地址
    print ("reverse address: %s" % ips.reverseNames()[0]) #输出地址反向解析
    print ('subnet: %s' % len(ips))      #输出网络子网数
else: # 为单个IP地址
    print ('reverse address: %s' % ips.reverseNames()[0])

print ('hexadecimal: %s' % ips.strHex())
print ('binary ip: %s ' % ips.strBin())
print 'iptype：%s' % ips.iptype()



