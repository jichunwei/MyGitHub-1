#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Anzuo Liu
#
# Created:     08/05/2014
# Copyright:   (c) Anzuo Liu 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys, time, re, traceback, subprocess, tarfile, stat
import socket, threading, SocketServer
import signal, shutil
import time, datetime
import pdb

shutdown_flag = False
BUFFERSIZE = 1024*1024
CHANGEDIR = ''

def _raise_exception(msg):
    bt = traceback.format_stack
    print bt
    raise Exception(msg)

def _get_testbed_obj_by_name(ltb_name):
    testbed_obj_list = Testbed.objects.all().filter(name=ltb_name)
    if len(testbed_obj_list) != 1:
        return None
    else:
        return testbed_obj_list[0]

def _get_build_obj_by_version(build_version):
    build_obj_list = Build.objects.all().filter(version=build_version)
    if len(build_obj_list) != 1:
        return None
    else:
        return build_obj_list[0]

def _get_batch_obj_by_testbed_obj_and_build_obj(testbed_obj, build_obj):
    batch_obj_list = Batch.objects.all().filter(testbed=testbed_obj, build=build_obj)
    if len(batch_obj_list) != 1:
        return None
    else:
        return batch_obj_list[0]
    
def _get_local_time_stamp():
    ts_tumple = time.localtime()
    #return year,          month,       day,          hour,       minute,      second
    return ts_tumple[0], ts_tumple[1], ts_tumple[2], ts_tumple[3], ts_tumple[4], ts_tumple[5]

def _is_file_exist_and_size_bigger_than_zero(file_name):
    if not os.path.isfile(file_name):
        return False, "image file not exist"
    if not os.path.getsize(file_name) > 0:
        return False, "image file size is wrong"
    return True, ""

def _remove_directory(src):
    os.system("rd /s /q %s" % src)
    
def create_build_stream_if_not_exist(**kwargs):
    '''
    param:  {'product':'ZD3000',
             'mainline':False,
             'prefix':'9.9.0.0'}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    product = kwargs.get('product')
    mainline = kwargs.get('mainline')
    prefix = kwargs.get('prefix')
    
    buildstream_objs = BuildStream.objects.all()
    bs_obj = None
    for buildstream_obj in buildstream_objs.filter(prefix=prefix):
        if product in buildstream_obj.name:
            if mainline:
                bs_obj = buildstream_obj if 'mainline' in buildstream_obj.name else None
            else:
                bs_obj = buildstream_obj if 'production' in buildstream_obj.name else None
    
    if bs_obj:
        return True, "buildstream already exist"
    else:
        bs_name = product+"_"+prefix+"_"
        bs_name = bs_name+"mainline" if mainline else bs_name+"production"
        bs_obj = BuildStream(name=bs_name, prefix=prefix)
        bs_obj.save()
        return True, "create buildstream successfully"
            
def create_build_if_not_exist(**kwargs):
    '''
    param:  {'bs_name':'ZD3000_9.9.0.0_production',
             'number':'123',
             'url':'http://www.baidu.com/'}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    bs_name = kwargs.get('bs_name')
    number = int(kwargs.get('number'))
    url = kwargs.get('url')

    build_objs = Build.objects.all()
    
    buildstream_objs = BuildStream.objects.all().filter(name=bs_name)
    if len(buildstream_objs) == 0:
        tmplist = bs_name.split('_')
        ml = True if 'production' not in tmplist[2] else False
        create_build_stream_if_not_exist(product=tmplist[0], mainline=ml,prefix=tmplist[1])
        buildstream_obj = BuildStream.objects.all().filter(name=bs_name)[0]
    else:
        buildstream_obj = buildstream_objs[0]
    
    if buildstream_obj is None:
        return False, "cannot find buildstrea[%s]" % bs_name
    
    b_obj = None
    Y,M,D,h,m,s = _get_local_time_stamp()
    timestamp = datetime.datetime(Y,M,D,h,m,s)
    
    for build_obj in build_objs.filter(build_stream=buildstream_obj):
        if number == build_obj.number:
            b_obj = build_obj
            break

    if b_obj:
        b_obj.version = b_obj.label = buildstream_obj.prefix+'.'+str(number)
        b_obj.URL = url
        b_obj.timestamp = timestamp
        b_obj.save()
        return True, "build already exist"
    else:
        b_obj = Build(build_stream=buildstream_obj, number=number, timestamp=timestamp)
        b_obj.version = b_obj.label = buildstream_obj.prefix+'.'+str(number)
        b_obj.URL = url
        b_obj.save()
        return True, "create build successfully"
    
def create_autoconfig_if_not_exist(**kwargs):
    '''
    param:  {'tb_name':'sr.test',
             'bs_name':'ZD3000_9.9.0.0_production',
             'build':'123',
             'ts_name_list':['cmp xml files after first sync',]}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    tb_name = kwargs.get('tb_name')
    bs_name = int(kwargs.get('bs_name'))
    build = kwargs.get('build')
    ts_name_list = kwargs.get('ts_name_list')
    
    ac_objs = AutotestConfig.objects.all()
    tb_obj = Testbed.objects.all().filter(name=tb_name)
    bs_obj = BuildStream.objects.all().filter(name=bs_name)
    ts_objs = []
    
    for ts_name in ts_name_list:
        ts_obj = TestSuite.objects.all().filter(name=ts_name)
        ts_objs += ts_obj
        
    if not tb_obj:
        return False, "cannot find testbed[%s]" % tb_name
    else:
        tb_obj = tb_obj[0]
        
    if not bs_obj:
        return False, "cannot find buildstream[%s]" % bs_name
    else:
        bs_obj = bs_obj[0]
        
    ac_obj = ac_objs.filter(testbed=tb_obj, build_stream=bs_obj)
    if not ac_obj:
        ac_obj = AutotestConfig(testbed=tb, build_stream=bs)
        ac_obj.lastbuildnum = int(build)
        for ts_obj in ts_objs:
            ac_obj.suites.add(ts_obj)
        ac_obj.save()
        return True, "create autotestconfig successfully"
    else:
        ac_obj = ac_obj[0]
        ac_obj.lastbuildnum = int(build)
        for ts_obj in ts_objs:
            ac_obj.suites.add(ts_obj)
        ac_obj.save()
        return True, "update autotestconfig successfully" 
  
def get_online_zd_ip_address_list(**kwargs):
    '''
    param:  {'zd_ip_list':''}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    if kwargs.has_key('zd_ip_list'):
        zd_candidate_ip_list = kwargs.get('zd_ip_list')
    
    online_zd_ip_list = []
    
    for ip in zd_candidate_ip_list:
        res = subprocess.Popen('ping %s -n 1' % ip, stdout=subprocess.PIPE).communicate()[0]
        if 'timed out' not in res:
            online_zd_ip_list.append(ip) 
    return str(online_zd_ip_list)

def get_online_zd_version(**kwargs):
    '''
    param:  {'zd_ip_list':''}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    if kwargs.has_key('zd_ip_list'):
        zd_ip_list = kwargs.get('zd_ip_list')
    
    zd_version_list = []
    from RuckusAutoTest.components import create_zd_cli_by_ip_addr
    if len(zd_ip_list) != 0:
        for zd_ip in zd_ip_list:
            zdcli = create_zd_cli_by_ip_addr(ip_addr=zd_ip)
            zd_version_list.append(zdcli.get_system_info().get('Version'))
            zdcli.close()
            del(zdcli)
    return str(zd_version_list)

def get_current_script_changelist(**kwargs):
    '''
    param:  {'':''}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    changelist = ''
    changelist = os.getcwd().split("\\")[-2]
    changelist = changelist.split("_")[-1]
        
    return str(changelist)

def download_zd_build(**kwargs):
    '''
    param:  {'url':'',
             ''   :''}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    if kwargs.has_key('url'):
        url = kwargs.get('url')
    
    import urllib2, tarfile
    try:
        file_name = url.split('/')[-1]
        tmp_url = url.replace(file_name, '')
        item = urllib2.urlopen(tmp_url)
        header = item.read()
        item.close()
        header = header.replace("\n", '').replace(' ', '')
        header = re.search("<tr>.+?%s.+?</tr>" % file_name, header).group()
        tmp_list = re.split("<.+?>", header)
        
        size = 0
        for x in tmp_list:
            if re.search("^\d", x):
                size = int(x)
                break
        
        item = urllib2.urlopen(url)
        local_file = open(file_name, 'wb')
        
        buffer = 1024*1024
        data_size = 0
        if size > 0:
            while size > data_size:
                data = item.read(buffer)
                local_file.write(data)
                sys.stdout.write("Complete %2.2f%%\r" % (data_size/float(size)*100))
                sys.stdout.flush()
                data_size = data_size + buffer
        else:  
            local_file.write(item.read())
    except Exception,e:
        return e.message
    finally:
        local_file.close()
        res, msg = _is_file_exist_and_size_bigger_than_zero(file_name)
        if not res:
            return msg
    
    try:
        tar_file = tarfile.open(file_name, 'r')
        for item in tar_file:
            if item.name.split('.')[-1] == 'img':
                img_file_name = item.name
                tar_file.extract(item)
                break
    except Exception, e:
        print e.message
    finally:
        tar_file.close()
        os.remove(file_name)
        res, msg = _is_file_exist_and_size_bigger_than_zero(img_file_name)
        if not res:
            return msg
    
    return img_file_name

def _upgrade_zd_image(zd_ip, img_file_name):
    from RuckusAutoTest.components import create_zd_by_ip_addr
    try:
        zd = create_zd_by_ip_addr(ip_addr=zd_ip)
        img_file_name = os.getcwd()+"\\"+img_file_name
        zd.upgrade_sw(filename=img_file_name)
    except Exception, e:
        print e.message
    finally:
        zd.s.close()
        zd.selenium.stop() 
        del(zd)

def upgrade_zd_image(**kwargs):
    '''
    param:  {'zd_ip'         :['192.168.0.2'],
             'img_file_name' :'zd3k_9.8.0.0.342.ap_9.8.0.0.342.img'}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)
    
    if kwargs.has_key('zd_ip'):
        zd_ip = kwargs.get('zd_ip')
    if kwargs.has_key('img_file_name'):
        img_file_name = kwargs.get('img_file_name')
    
    _funcList = []
    for zd in zd_ip:
        _funcList.append(threading.Thread(target=_upgrade_zd_image, kwargs={'zd_ip':zd, 'img_file_name':img_file_name}))
    
    for ins in _funcList:
        ins.start()
    for ins in _funcList:
        ins.join()
    
def get_batch_result(**kwargs):
    '''
    param:  {'ltb_name':'zd3k.wlan.option',
             'build'   :'9.8.0.0.14'}
    '''
    if type(kwargs) is not dict:
        _raise_exception("incoming param(%s) is not a dict" % kwargs)

    if kwargs.has_key('ltb_name'):
        ltb_name = kwargs.get('ltb_name')
    else:
        _raise_exception("there is no key 'ltb_name'")

    if kwargs.has_key('build'):
        build = kwargs.get('build')
    else:
        _raise_exception("there is no key 'build'")

    ltb_obj = _get_testbed_obj_by_name(ltb_name)
    build_obj = _get_build_obj_by_version(build)
    if ltb_obj == None or build_obj == None:
        _raise_exception("cannot get testbed(%s) or build(%s)" % (ltb_name, build))

    batch_obj = _get_batch_obj_by_testbed_obj_and_build_obj(ltb_obj, build_obj)
    if batch_obj == None:
        _raise_exception("cannot get batch(%s, %s)" % (ltb_name, build))

    return lviews.generate_batch_result(batch_obj)


class MsgHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "rec msg from client(%s)!" % str(self.client_address)
        
        while True:
            time.sleep(1)
            try:
                msg = self.receive()

                if len(msg) == 0:
                    continue
                print "[%s] -- %s" % (self.client_address,msg)

                if re.search("quit", msg, re.IGNORECASE):
                    break
                elif re.search("file:.+", msg, re.IGNORECASE):
                    pwd = "../.."
                    filename = re.search("file:.+", msg, re.IGNORECASE).group().split(":")[-1]
                    print filename
                    file = open("%s/%s" % (pwd, filename), 'wb')
                    self.send("got file")
                    
                    filesize = 0
                    while True:
                        time.sleep(1)
                        msg = self.receive()
                        if re.search("size:.+", msg, re.IGNORECASE):
                            filesize = re.search("size:.+", msg, re.IGNORECASE).group().split(":")[-1]
                            filesize = int(filesize)
                            print filesize
                            break
                    self.send("got size")
                    
                    i = 0
                    size = 0
                    while True:
                        try:
                            data = self.request.recv(4096)
                            file.write(data)
                            
                            i += 1
                            size += len(data)
#                            print i, "  ", size
                            if size >= filesize:
                                break
                        except Exception, e:
                            file.close()
                            self.send("done")
                            print "catch a exception(%s)" % e.message
                            break
                     
                    file.close()
#                    self.send("done")
                    
                    try:
                        file = tarfile.open("%s/%s" % (pwd, filename), 'r')
                        file.extractall(pwd)
                        file.close()
                        os.remove("%s/%s" % (pwd, filename))
                        
                        old_dir_name = "%s/saigon" % pwd
                        new_dir_name = "%s/%s" % (pwd, filename.split('.')[0])
                        
                        if filename.split('.')[0] in os.getcwd():
                            continue
                        
                        if os.path.isdir(new_dir_name):
                            curr_path = os.getcwd()
                            os.chdir(pwd)
                            _remove_directory(filename.split('.')[0])
                            os.chdir(curr_path)
                        
                        os.rename(old_dir_name, new_dir_name)
                        
                        shutil.copyfile("./rat.db", new_dir_name+"/rat/rat.db")
                        
                        global CHANGEDIR
                        CHANGEDIR = new_dir_name
                    except Exception, e:
                        print "catch a exception(%s)" % e.message
                        file.close()
                    finally:
                        self.send("done")
                else:
                    self.execution(msg)

            except Exception, e:
                print "catch a exception(%s)" % e.message
                break

    def send(self, msg):
        self.request.sendall(msg)

    def receive(self, size=4096):
        msg = self.request.recv(size).strip()
        return msg

    def execution(self, raw_cmd):
        '''
        raw_cmd's pattern must be: operate_sth_xxx;xxx
        for example: get_batch_result;9.7.0.0
        '''
        cmd_regx = '([a-zA-Z0-9_.]+);(.*)'

        obj = re.match(cmd_regx, raw_cmd)
        if obj:
            cmd = obj.group(1).strip()
            param = obj.group(2).strip()
        else:
            _raise_exception("Invalid CMD format -- %s" % raw_cmd)

        param = eval(param) if param else ''
        exec("res = %(cmd)s(**param)" % locals())
        print "---> Reuslt: %s\n" % str(res)
        self.send(str(res))

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def kill_process(pid):
    if sys.platform == 'win32':
        import ctypes
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)
    else:
        os.kill(pid, signal.SIGKILL)

def sigHandler(signum, frame):
    global shutdown_flag
    shutdown_flag = True
    print shutdown_flag

def stop_web():
    output = subprocess.Popen(['netstat', '-o', '-a'], stdout=subprocess.PIPE).communicate()[0]
    output = output.split("\r\n")
    pidlist = []
    for item in output:
        if ":8009" in item:
            pidlist.append(item.split()[-1])
    
    for item in pidlist:
        os.system("taskkill /F /PID %s" % item) 

def start_web():
    stop_web()
    subprocess.Popen("startweb.bat", creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    global CHANGEDIR, shutdown_flag
    time.sleep(5)
    CHANGEDIR = ''
    HOST, PORT = "", 9999
    
    start_web()
    
    try:
        signal.signal(signal.SIGINT, sigHandler)
        signal.signal(signal.SIGTERM, sigHandler)
    
        SocketServer.TCPServer.allow_reuse_address = True
        server = ThreadedTCPServer((HOST, PORT), MsgHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()
        print "I am a tcp server, and ready to rec msg[%s]" % os.getcwd()
    except Exception, e:
        print "catch a exception(%s)" % e.message
        raise e

    while True:
        #TODO: 
        #    as my original design, server_thread.py should be exist in a CL folder, like ../regression/boston/saigon_xxx/server_thread.py
        #    when update scripts, server_thread.py will get new script compress file like saigon_xxx.rar, and decompress to its up level folder
        #    then shutdown tcp server and kill itself after start a new process to run new server_thread.py
        #
        #    but there are several problems I cannot resolve
        #    1. env variable inherit between father process and child process
        #    2. CPU usage will be very high when change to new process
        #    3. python 2.5 cannot close the port when shutdown tcp server, but 2.7 ok
        #
        #    So, I change my design, users have to start server_thread.py by themselves after update script
#        if CHANGEDIR != '':
#            os.chdir(CHANGEDIR+"\\rat")
#            del ratenv, TestCase, Testbed, TestRun, Batch, Build, BuildStream, AutotestConfig, TestSuite, lviews
#            
#            import ratenv
#            from RuckusAutoTest.models import TestCase, Testbed, TestRun, Batch, Build, BuildStream, AutotestConfig, TestSuite
#            import RuckusAutoTest.lib_Views as lviews
#            
#            start_web()
#            CHANGEDIR = ''
#            stop_web()
#            shutdown_flag = True
            
        time.sleep(1)        
        if shutdown_flag:
            server.socket.close()
            if "2.5." in sys.version:
                print "shutdown server"
                server.server_close()
            else:
                server.shutdown()     
            break

if __name__ == '__main__':
    from ratenv import *
    from RuckusAutoTest.models import TestCase, Testbed, TestRun, Batch, Build, BuildStream, AutotestConfig, TestSuite
    import RuckusAutoTest.lib_Views as lviews
    main()
