#coding:utf-8

#熟悉IPy模块的使用

from IPy import  IP

# '4'代表ipv4, '6'代表ipv6
ip_type = IP("10.0.0.0/8").version()
ip_v6_type = IP('::1').version()
print ip_type, ip_v6_type

ip = IP('192.168.0.0/16')
print ip.len() #输出192.168.0.0/16网段的IP个数
# for x in ip:  #输出192.168.0.0/16网段内的所有IP清单
#     print x


ip = IP('192.168.1.20')
print ip.reverseName() #反向解析地址格式
print ip.iptype()  #'192.168.1.20 为私网类型'PRIVATE'
print IP('8.8.8.8').iptype()  #8.8.8.8为公网类型
print IP('8.8.8.8').int() #转换成整形类型
print IP('8.8.8.8').strHex()  #转换成十六进制格式
print IP('8.8.8.8').strBin()  #转换成二进制格式
print (IP(0x8080808))   #十六进制转换成IP格式


#子网掩码
print IP('192.168.1.0').make_net('255.255.255.0')
print IP('192.168.1.0/255.255.255.0', make_net=True)
print IP('192.168.1.0-192.168.1.255', make_net=True)

#判断IP地址网段是否包含于另一个网段中
res = IP('10.0.0.0/24') < IP('12.0.0.0/24')
print res
print  '192.168.1.100'  in IP('192.168.1.0/24')
print IP('192.168.1.0/24') in IP('192.168.0.0/16')

#判断俩个网段是否存在重叠
print IP('192.168.0.0/23').overlaps('192.168.1.0/24') #返回1代表存在重叠
print IP('192.168.1.0/24').overlaps('192.168.2.0') #返回0代表不重叠


