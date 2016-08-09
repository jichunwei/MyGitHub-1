#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import urllib
import urllib2
import threading
import base64

#############################################################################
#
# self-defined exception classes
#
#############################################################################
class ConnectionError(Exception): pass
class URLUnreachable(Exception):pass
class CanotDownload(Exception):pass

#############################################################################
#
# multiple threads download module starts here
#
#############################################################################
class HttpGetThread(threading.Thread):
    def __init__(self, name, url, filename, range=0):
        threading.Thread.__init__(self, name=name)
        self.url = url        
        self.filename = filename
        self.range = range
        self.totalLength = range[1] - range[0] +1
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192
        


    def run(self):
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        #self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192
        #request = urllib2.Request(self.url)
        #request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
        downloadAll = False
        retries = 1
        while not downloadAll:
            if retries > 10:
                break
            try:
                self.headerrange = (self.range[0]+self.downloaded, self.range[1])
                
                if check_nanhu(self.url):
                    hnd = get_handler()
                    hnd.addheaders += [('Range', 'bytes=%d-%d' %self.headerrange)]
                    conn = hnd.open(self.url)
                               
                else:
                    request = urllib2.Request(self.url)                
                    b64s = base64.encodestring('%s:%s' % (username, password))[:-1]
                    encryptstr  =  "Basic %s" % b64s    
                                               
                    request.add_header('Authorization', encryptstr)
                    request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
                    conn = urllib2.urlopen(request)
                    
                startTime = time.time()
                data = conn.read(self.bufferSize)
                while data:
                    f = open(self.filename, 'ab')
                    f.write(data)
                    f.close()
                    self.time = int(time.time() - startTime)
                    self.downloaded += len(data)
                    self.percent = self.downloaded/float(self.totalLength) *100             
                    data = conn.read(self.bufferSize)
                downloadAll = True
            except Exception :
                retries += 1
                time.sleep(1)
                continue

(username,password) = ('qaauto', 'QaAuto!880')
class OpenerWithAuth(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return username, password

def split(size,blocks):
    ranges = []
    blocksize = size / blocks
    for i in xrange(blocks-1):
        ranges.append(( i*blocksize, i*blocksize+blocksize-1))
    ranges.append(( blocksize*(blocks-1), size-1))

    return ranges

def get_handler(url="http://nanhu.tw.video54.local/login/j_acegi_security_check"):
    
       
    hnd = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(hnd)
    values = {'j_username':username,
              'j_password':password,
              }
    p = urllib.urlencode(values)
    f = hnd.open(url, p)
#    logging.info(f.read())
    f.close()
        
    return hnd

def check_nanhu(url):
    return True if 'nanhu' in url else False

#Updated by cwang@20130627, to support ODC office
def get_http_filesize(url):
    length = 0
    try:
        if check_nanhu(url):
            hnd = get_handler()
            conn = hnd.open(url)           
        elif "yangming" in url:  
            conn = OpenerWithAuth().open(url)
        else:
            conn = urllib.urlopen(url)
                
        headers = conn.info().headers
        for header in headers:
            if header.find('Length') != -1:
                length = header.split(':')[-1].strip()
                length = int(length)
    except Exception :
        pass
      
    return length

def has_live(ts):
    for t in ts:
        if t.isAlive():
            return True
    return False

def http_get(url, output=None, connections=1):
    """
    arguments:
        url, in GBK encoding
        output, default encoding, do no convertion
        connections, integer
    """
    length = get_http_filesize(url)
    print length
    mb = length/1024/1024.0
    if length == 0:
        raise URLUnreachable
    blocks = connections
    if output:
        filename = output
    else:
        output = url.split('/')[-1]
        filename = output

    ranges = split(length, blocks)
    names = ["%s_%d" %(output,i) for i in xrange(blocks)]
  
    ts = []
    for i in xrange(blocks):
        t = HttpGetThread(i, url, names[i], ranges[i])
        t.setDaemon(True)
        t.start()
        ts.append(t)

    live = has_live(ts)
    startSize = sum([t.downloaded for t in ts])
    startTime = time.time()
    etime = 0
    while live:
        try:
            etime = time.time() - startTime
            d = sum([t.downloaded for t in ts])/float(length)*100
            downloadedThistime = sum([t.downloaded for t in ts])-startSize
            try:
                rate = downloadedThistime / float(etime)/1024
            except:
                rate = 100.0
            progressStr = u'\rFilesize: %d(%.2fM) Downloaded: %.2f%% Avg rate: %.1fKB/s' %(length, mb, d, rate)
            sys.stdout.write(progressStr)
            sys.stdout.flush()
            #sys.stdout.write('\b'*(len(progressStr)+1))
            live = has_live(ts)
            time.sleep(0.2)
        except KeyboardInterrupt:
            print
            print "Exit..."
            for n in names:
                try:
                    os.remove(n)
                except:
                    pass
            sys.exit(1)
          
    #print u'used time: %d:%d, pingjunsudu:%.2fKB/s' %(int(etime)/60, int(etime)%60,rate)

    f = open(filename, 'wb')
    for n in names:
        f.write(open(n,'rb').read())
        try:
            os.remove(n)
        except:
            pass
    f.close()
    if os.path.getsize(filename) == length:
        return True
    else:
        return False

    



if __name__ == '__main__':
    http_get('http://nanhu.tw.video54.local/view/ALL/job/Mainline_0.0.0.99_ZD3000-OFFICIAL/lastSuccessfulBuild/artifact/tftpboot/ZD3000_production/zd3k_0.0.0.99.237.ap_0.0.0.99.237.img','test.img',16)
    
