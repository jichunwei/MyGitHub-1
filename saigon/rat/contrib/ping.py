'''
Created on Jan 20, 2011

@author: lab
'''

"""A wrapper around ping"""
import sys
import os,subprocess

def ping_win32(target_ip, num=4, length=64, timeout_ms=1000):
    """ping the target and return a list of successful result times in milliseco                                                                              nds"""
    cmd = "ping %s -n %d -l %d -w %d" % (target_ip, num, length, timeout_ms)
    #print cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    err = p.wait()

    res = p.stdout.readlines()
    # extract time from ping results
    res = [x.split(' ') for x in res if x.startswith('Reply from')]
    res = [[t for t in x if t.startswith('time')][0] for x in res]

    # XXX TODO deal with pings that dont return the same number of bytes as tran                                                                              smitted !

    # normalize "<1ms" result to be same as "=1ms"
    res = [x.replace('<','=') for x in res]
    res = [int(x.split('=')[1].replace('ms','')) for x in res]
    return res


def ping_linux(target_ip, num=4, length=64, timeout_ms=1000):
    """ping the target and return a list of successful result times in milliseco                                                                              nds"""
    cmd = "ping %s -i 0.2 -c %d -s %d -W 5" % (target_ip, num, length)
    p = os.popen(cmd, 'r')

    res = p.readlines()

    # extract time from ping results
    res = [x.split(' ') for x in res if 'bytes from' in x]
    res = [[t for t in x if t.startswith('time')][0] for x in res]

    # XXX TODO deal with pings that dont return the same number of bytes as tran                                                                              smitted !

    # normalize "<1ms" result to be same as "=1ms"
    res = [x.replace('<','=') for x in res]
    res = [float(x.split('=')[1].replace('ms','')) for x in res]
    return res

def ping(target_ip, num=4, length=64, timeout_ms=1000):
    if sys.platform == "win32":
        return ping_win32(target_ip, num,length,timeout_ms)
    else:
        return ping_linux(target_ip, num,length,timeout_ms)

if __name__ == "__main__":
    print sys.version
    print sys.argv[1]
    print ping(sys.argv[1])
