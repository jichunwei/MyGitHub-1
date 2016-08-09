'''
The RatTLInvoker accepting command and execute it accordingly:
 1) Status.
 2) Status<batch-id>#list the result of test run map in brief format.
 3) Batch add<batch-id>
 4) Batch del<batch-id>
 5) Shutdown
 6) TL<batch-id> #trigger the rat-2-tl report process immediately
 7) set {Devkey|TestlinkURL|ReportInterval}<value>

Things to Watch:
    1) Dead lock due to here are there process accessing 
       rat.db at the same time.
    2) Rat and tl communication broken.
    3) Disputed records due to manual process.

How to use:
    server:
        python rat_tl_invoker.py
    client:
        telnet <remote_ip> <port>
        Example:
            telnet 172.18.35.150 10889
            Hello('127.0.0.1', 56121)

            Command# help
            For more information on the a specific command, type HELP command-name
             BATCH list/del batch info.
             TL    get/put/map rat to test link.
             SET   key=value for test link association.
            Command#

Created on Mar 21, 2011
@author: cwang@ruckuswireless
'''

import os
import re
import sys
import traceback
import time
import datetime
import pdb
import ConfigParser
import threading
import logging
import subprocess as sp

from pprint import pprint, pformat
from Queue import Queue
from SocketServer import (ThreadingTCPServer, 
                          StreamRequestHandler)

from RatLogger import RatLogger

import update_test_db
import map_test_run
import db_env

from tlc22.TestlinkClient22 import TestlinkClient22
from TLReportMgr import TLReportMgr

from RuckusAutoTest import models as rat_m

_RatTLInvoker_VERSION = '1.0.0.1'

invoker = None
try:
    invoker['tm_init'] = time.time()
except Exception, e:
    invoker = dict(tm_init=time.time(), qarun=None)

invoker['pid'] = os.getpid()

CurrClient = {'init': time.time()}
#_one_user_only = r"SORRY %s. I only serve one client a time. Login later. Thanks.\r\n"

#INTERVAL = 60 * 60 * 2#report interval 4 Hours
INTERVAL = 60 * 15

def start_server(**kwargs):
    tcfg = dict(port=10889)
    tcfg.update(kwargs)    

    if tcfg.has_key('debug') and tcfg['debug']: pdb.set_trace()
    if tcfg.has_key('h') or tcfg.has_key('help'):
        logging.info(tcfg)
        return    
    
    msg = "Launch service [version %s] [pid %s] at port %s" \
        % ( str(_RatTLInvoker_VERSION), str(invoker['pid']), str(tcfg['port']))
    dln = "+-" + "-" * len(msg) + "-+"
    logging.info("\n%s\n| %s |\n%s" % (dln, msg, dln))
    
    invoker['param'] = ParamMgr()
    invoker['mgr'] = BatchMgr()
    invoker['ctl'] = TLController(invoker['param'])
    invoker['report'] = Reporter(invoker['ctl'], invoker['param'])
    invoker['report'].start()
    
    invoker['executor'] = QARunner(invoker['report'])
    invoker['executor'].start()
        
    invoker['rat'] = TasksController(invoker['executor'], invoker['report'])
    invoker['daily_build'] = DailybuildController(invoker['executor'], invoker['param'])
    
    invoker['server'] = ThreadingTCPServer(('', int(tcfg['port'])), UserRequestHandler)
    invoker['server'].serve_forever()


def stop_server():
    if invoker['server']:
        invoker['server'].server_close()
        invoker['server'] = None


def pretty_print(cfg_dict):
    res = ""
    for k, v in cfg_dict.items():
        res += "%s=%s\r\n" % (k, v)
    return res

def help(key='all'):    
    help_dict = {}
    res = """
    For more information on the a specific command, type HELP command-name
        <batch {list|del}> batch command.
        <tl  {get|map|put|clear}> tl command.
        <rat {start|stop|reload|get cur|get all cur|report}> rat command.
        <set key=value> set command.
        <list param> list command.      
        <dev args> daily build command.  
    """
    help_dict['all'] = res

    res = """
    BATCH operation.
        batch list 'list all the batch'
        batch <batch_id> 'list batch by batch_id'
        batch del <batch_id> 'del batch by batch_id, be carefully'
    """
    help_dict['batch'] = res

    res = """
    TL operation.
        tl get 'get testcases assigned from testlink'
        tl map 'map test case between testlink and rat'
        tl put 'put test report to testlink'    
        tl all 'get & map & put test case between testlink and rat'
        tl clear 'clear up local testlink database.'
    """
    help_dict['tl'] = res

    res = """
    SET operation.
        set key=value
        key={server_url|dev_key|project|plan|build|auto_cases_top_folder}
        Example:set build=9.2.0.0.12"""
    help_dict['set'] = res
    
    res = """
    RAT operation.
        rat start  'load latest execution list and step by step execute logical test bed.'
        rat stop   'stop all of execution.'
        rat reload 'reload latest execution list, QARunner will use it till current test bed finished.'
        rat reload enforce=True 'reload latest execution list, QARunner will stop immediately and perform the latest one.'
        rat get cur 'get current running testbed.'
        rat get all cur 'get all current testbeds.'
        rat report 'report all test bed to testlink except skipped..'
    """
    help_dict['rat'] = res    
    
    res = """
    Dev operation.
        dev <build stream> <build no>, i.e. 'dev ZD3000_7.1.1.0_production 18' 
    """
    
    help_dict['dev'] = res
    
    if help_dict.has_key(key):
        help_str = help_dict[key]
    else:
        help_str = help_dict['all']
    
    fn = lambda x, y: x.join([x for i in range(y)])
    headline = "\n"+fn("=", 50)+"\n"
    footline = "\n"+fn("*", 50)+"\n"
    help_str = headline + help_str + footline
    return help_str.replace("\n", "\r\n") 


def mojo_output(output):
    output = output.replace('\n', '\r\n')
    return output

    
class QARunner(threading.Thread):
    '''
    QARun executor
    '''               
    def __init__(self, reporter = None):        
        threading.Thread.__init__(self)        
        self.q = Queue()
        self.lock = threading.Lock()        
        self._pid = -1
        self.flag = True
        self.command = ""
        self.reporter = reporter
    
    def reset_queue(self, queue):
        try:
            self.lock.acquire()
            self.q = queue
            self.flag = True
        finally:
            self.lock.release()        
        
    def _kill_process(self):        
        try:            
            pid = self._pid     
            self._print_process_info(pid)
            logging.info("Is about to Kill myself.pid %s" % str(pid))
            sp.call(r'c:\bin\win\pskill -t %s' % str(pid))
            sp.call(r'c:\bin\win\pskill java')
            sp.call(r'c:\bin\win\pskill firefox')
            time.sleep(10)
        except:
            pass

    def _print_process_info(self, pid):        
        pipe = sp.Popen(r'c:\bin\win\pslist -t %s' % str(pid), shell=True, stdout=sp.PIPE)
        data = pipe.stdout.read()
        logging.info(data)
    
    def _build_cmd(self, obj):
        tbname = obj.autoconfig.testbed.name
        bstream = obj.autoconfig.build_stream.name
        bno = obj.build_number
        chkv = obj.check_version
        reboot_sta = obj.reboot_station
        title = '%s %s bno=%d chkv=%s reboot_sta=%s p#%s' \
            %(bstream, tbname, int(bno),                                      
              chkv, reboot_sta, obj.priority)
        
        qarun = os.path.join(os.getcwd(), 'qarun.py')
        return 'start "%s" python %s %s %s bno=%d chkv=%s reboot_sta=%s rebuildbatch=True' \
            % (title, qarun, bstream, tbname, 
               int(bno), chkv, reboot_sta)
           
    def run(self):
        while True:
            self.lock.acquire()
            fnd = True
            try:                  
                if self.q.empty():                
#                    logging.debug("Haven't any tasks in Queue, Jump into sleep.")
                    self.command = None
                    fnd = False                    
                elif not self.flag:
#                    logging.debug("All of tasks have been stopped, Jump into sleep.")
                    fnd = False
            finally:
                self.lock.release()
            
            if not fnd:
                time.sleep(10)
                continue                        
                        
            while self.flag:                
                try:
                    obj = self.q.get()
                    self.command = self._build_cmd(obj)
                    logging.info(self.command)
                    self.q.task_done()
                    try:
                        obj.cur_status = "R"
                        obj.save(force_update=True)
                        self.pipe = sp.Popen(self.command, 
                                     shell=True,
                                     stdin=sp.PIPE,
                                     stdout=sp.PIPE,
                                     stderr=sp.PIPE)
                        self._pid = self.pipe.pid                        
                        self.data = self.pipe.stdout.read()
                                                
                    except:
                        logging.debug(traceback.format_exc())                        
                        
                    finally:
                        try:                        
                            batch = obj._get_batch()
                            if batch:
                                if batch.complete:
                                    testquery = rat_m.TestRun.objects.filter(batch = batch, 
                                                                             complete = False, 
                                                                             skip_run = False).exclude(result__icontains = 'SKIP')
                                    if testquery.count():
                                        obj.cur_status = 'U'
                                    else:                                        
                                        obj.cur_status = 'D'
                                else:
                                    obj.cur_status = "U"
                            else:
                                obj.cur_status = "N"                            
                                 
                            obj.save(force_update=True)
                            
                            #Add Task to Report TestLink Thread if batch existed.
                            if batch and self._pid != -1:
#                                logging.info('Reporter%s' % obj)
                                self.reporter.add_task(obj, True)
                                self.reporter.associate_rat_mgr()                                                                                                         
                        except:
                            logging.debug(traceback.format_exc())
                        
                        self._pid = -1                                                                                                                                            
                except:
                    logging.debug(traceback.format_exc())
                    
                finally:
                    if self.q.empty():
                        break                     
    
    def getpid(self):
        return self._pid
    
    def stop(self):
        self.lock.acquire()
        try:            
            self._kill_process()
            self.flag = False
            self._pid = -1
        except:
            logging.info("Can't stop current test bed.")
            logging.debug(traceback.format_exc())
        finally:
            self.lock.release()
            
    def get_cur_cmd(self):
        return self.command
    
    def add_task(self, obj):
        self.q.put(obj)
        logging.info('New Task[%s] Joins' % obj)    
    
    pid = property(getpid)

class TasksController():
    """
    Apply for Testbed manage: 
        +start/stop logical test bed.        
        +handler latest logical test bed, and monitor its status.        
    """
    def __init__(self, executor, reporter):
        self.executor = executor
        self.reporter = reporter
        self.q = Queue()
        self.titles = []
              
    def pp(self, msg):
        print msg
    
    def _print_tblist(self, writer = None):
        if not self.titles:
            writer("Haven't any test bed in execution list.")
            
        fn = lambda x, y: x.join([x for i in range(y)])
        writer(fn("=", 100))
        for cmd in self.titles:
            writer(cmd)
        writer(fn("*", 100))        
    
    def get_all_cur_tb(self, writer = None):
        if not self.titles:
            self._load_tblist()
        self._print_tblist(writer)        
    
    def get_cur_tb(self):        
        cmd = self.executor.get_cur_cmd()
        if cmd:
            return cmd.split("python")[0]
        else:
            self.pp("Haven't find any test bed in running.")
        
        
    def start(self, writer = None):
        '''
        Launch qarun.py for my testbed. 
        '''        
        pp = writer if writer else self.pp         
        try:
            pp('Starting....')
            self._load()
            self._print_tblist(writer)            
            if self.executor.pid != -1:
                pp("Have a task in running, Please stop first.")
                return            
            self.executor.reset_queue(self.q)                    
            time.sleep(5)
            pp('Start successfully')                       
        except Exception, e:
            # run c:\bin\win\pskill java 
            sp.call(r'c:\bin\win\pskill java')            
            time.sleep(10)
            logging.debug(traceback.format_exc())            
            pp('Occur error %s' % e.message)                        
              
    
    def report(self, writer = None):
        pp = writer if writer else self.pp
        try:                        
            pp("Reporting...")
            objs = self._load_tblist()            
            for obj in objs:
                batch = obj._get_batch()            
                #Add Task to Report TestLink Thread if batch existed.
                if batch:
#                    logging.info('Reporter%s' % obj)
                    pp("Report Task# %s" % obj)
                    self.reporter.bind_client_writer(writer)
                    self.reporter.add_task(obj, True)
                    self.reporter.associate_rat_mgr()
                                                                                                                                    
        except:
            logging.debug(traceback.format_exc())
    
    def stop(self, writer=None):
        '''
        Stop qarun.py for my testbed.        
        '''
        pp = writer if writer else self.pp
        try:
            if self.executor:
                pp('Stopping...')
                self.executor.reset_queue(Queue())
                self.executor.stop()          
                pp('Stopped')
            else:
                pp('Can not find any executor.')
        except Exception, e:
            pp('Occur issue %s' % e.message)
                
    
    def reload(self, enforce=False, writer = None):        
        pp = writer if writer else self.pp
        try:
            pp('Loading....')
            if not enforce:                        
                self._load()
                self._print_tblist(writer)            
                self.executor.reset_queue(self.q)
            else:
                self.stop()
                self.start()
            pp('Reload DONE.')
        except Exception, e:
            pp('Occur issue %s' % e.message)
            
    def _load(self):
        '''
        Load testbeds and deploy commands.
        '''
        _objs = self._load_tblist()
        self.q = Queue()        
        for _obj in _objs:            
            self.q.put(_obj)
            
    def _load_tblist(self):
        #@author: Jane.Guo @since: 2013-09 delete cur_status=D to report all select run
        _objs = rat_m.AutotestExecution.objects.filter(skip_run=False).order_by("priority")
#        _objs = rat_m.AutotestExecution.objects.filter(skip_run=False).exclude(cur_status='D').order_by("priority")
        self.titles = []
        for obj in _objs:
            tbname = obj.autoconfig.testbed.name
            bstream = obj.autoconfig.build_stream.name
            bno = obj.build_number
            chkv = obj.check_version
            reboot_sta = obj.reboot_station
            title = '%s %s bno=%d chkv=%s reboot_sta=%s p#%s' % \
                                    (bstream, tbname, int(bno), chkv, reboot_sta, obj.priority)
            self.titles.append(title)   
    
        return _objs


class Reporter(threading.Thread):
    def __init__(self, report_ctl, param_mgr):
        threading.Thread.__init__(self)        
        self.report_ctl = report_ctl
        self.param_mgr = param_mgr
        self._init = True
        self._queue = Queue()
        self._lock = threading.Lock()
        self.obj = None 
        self.standalone = False
    
        
    def run(self):
        while True:
            if self.report_ctl.get_flag():
                time.sleep(100)
                logging.info('Another process is report data, waiting...')
                continue
            
            
            if not self.standalone:
                if self._queue.empty():
                    time.sleep(10)
#                    logging.info("Haven't any Report tasks in Queue")
                    continue
                                
                try:                    
                    self.obj = self._queue.get()                    
                    batch = self.obj._get_batch()
                    if batch:                        
                        self.param_mgr.update_tl_param(self.obj.test_plan.name, 
                                                       self.obj.top_suite, 
                                                       batch.build.version)
                        self.report_ctl.update_param(self.param_mgr)  
                        logging.info("Try to Report %s" % self.obj)
                    else:
                        logging.debug("Haven't any batch in RAT while do [%s]" % self.obj)
                        continue                                                              
                except Exception, e:
                    print e.message
                finally:
                    self._queue.task_done()       
            
            else:
                logging.info('It will be report after %s(s)' % INTERVAL)
                time.sleep(INTERVAL)#Static testbed report.
                                        
            self.report_ctl.set_flag(True)
            try:                    
                if self._init or (hasattr(self.obj, "init") and self.obj.init):             
                    self.report_ctl.retrieve_data()
                    logging.info('Get data DONE')
                    self.report_ctl.map_data()
                    logging.info('Map data DONE')
                    
                    if hasattr(self.obj, "init"):
                        self.obj.init = False
                    else:
                        self._init = False                    
                                            
                self.report_ctl.report_data()
                if self.obj:
                    msg = "DONE, Report %s" % self.obj
                    if hasattr(self, "writer") and self.writer:
                        self.writer(msg)
                        
                    logging.info(msg)
                    
                logging.info('Auto-report DONE')
            finally:
                self.report_ctl.set_flag(False)
    
    
    def add_task(self, obj, init=True):
        self._lock.acquire()
        try:
            if obj:            
                obj.init = init
                self._queue.put(obj)                
                logging.info('New Task is coming %s' % obj)      
        finally:
            self._lock.release()    
    
    def bind_client_writer(self, writer=None):
        self.writer = writer
    
    def associate_rat_mgr(self):
        self.standalone = False
    
    def disassociate_rat_mgr(self):
        self.standalone = True
    
class ParamMgr():
    def __init__(self, filename=None):
        self.TL_SECTION  = 'tl'
        self.SERVER_URL = 'server_url'
        self.DEV_KEY = 'dev_key'
        self.PROJECT = 'project'
        self.PLAN = 'plan'
        self.BUILD = 'build'
        self.AUTO_CASES_TOP_FOLDER = 'auto_cases_top_folder'
        
        self.RAT_SECTION = "rat"
        self.TESTBED_NAME = "tbname"

        self.filename = 'rat_tl.ini'
        if filename:
            self.filename = filename
        self.cfg_hnd = ConfigParser.ConfigParser()
        self.cfg_hnd.read(self.filename)
        
    def __write(self):
        f = open(self.filename, "w")
        self.cfg_hnd.write(f)

    def update_tl_param(self, plan, top_suite, build):
        self.set_plan_name(plan)
        self.set_build_name(build)
        self.set_key_value(self.AUTO_CASES_TOP_FOLDER, top_suite, self.TL_SECTION)
        invoker['ctl'].update_param(self)
        
    def get_tl_param(self):
        cfg = dict()
        cfg[self.SERVER_URL] = self.cfg_hnd.get(self.TL_SECTION, self.SERVER_URL)
        cfg[self.DEV_KEY] = self.cfg_hnd.get(self.TL_SECTION, self.DEV_KEY)
        cfg[self.PROJECT] = self.cfg_hnd.get(self.TL_SECTION, self.PROJECT)
        cfg[self.PLAN] = self.cfg_hnd.get(self.TL_SECTION, self.PLAN)
        cfg[self.BUILD] = self.cfg_hnd.get(self.TL_SECTION, self.BUILD)
        cfg[self.AUTO_CASES_TOP_FOLDER] = self.cfg_hnd.get(self.TL_SECTION, self.AUTO_CASES_TOP_FOLDER)
#        pprint(cfg)
        return cfg

    def set_key_value(self, key, value, section='tl'):
        try:
            self.cfg_hnd.set(section, key, value)
            self.__write()
            return (True, 'OK.')
        
        except Exception:
            logging.debug(traceback.format_exc())
            return (False, 'key=%s, value=%s set is unsuccessful, detail %s' % (key, value, e))
    
    def get_tb_name(self):
        return self.cfg_hnd.get(self.RAT_SECTION, self.TESTBED_NAME)
    
    def set_tb_name(self, tbname):
        self.set_key_value(self.TESTBED_NAME, tbname, self.RAT_SECTION)

    def set_server_url(self, url):
        self.set_key_value(self.SERVER_URL, url)

    def set_project_name(self, project_name):
        self.set_key_value(self.PROJECT, project_name)

    def set_dev_key(self, dev_key):
        self.set_key_value(self.DEV_KEY, dev_key)

    def set_plan_name(self, plan_name):
        self.set_key_value(self.PLAN, plan_name)

    def set_build_name(self, build_name):
        self.set_key_value(self.BUILD, build_name)


class BatchMgr():
    '''
    Used for add/del/report/search batch info.
    '''
    def __init__(self):
        pass
    
    def get_batch(self, batch_id):
        batches = rat_m.Batch.objects.filter(id=batch_id)
        return batches if batches else "Not found with batch id [%s]" % batch_id

    def del_batch(self, batch_id):
        batches = rat_m.Batch.objects.filter(id=batch_id)
        size = len(batches)
        if size==1:
#            print batches
            batches[0].delete()
            return (True, 'Delete batch[%s] successfully' % batch_id)
        elif size>1:
            return (False, 'More than one record with search option [%s]' % batch_id)
        else:
            return (False, 'Not found with with batch id[%s]' % batch_id)


    def list_batches(self):
        batches = rat_m.Batch.objects.all()
        return batches

    def head_batches(self, n=5):
        batches = self.list_batches()
        i = 0
        head = []
        while i < n:
            head.append(batches[i])
            i += 1

        return head

    def tail_batches(self, n=5):
        batches = self.list_batches()
        batches.reverse()
        return self.head_batches(n)

    def get_latest_batch(self):
        return self.tail_batches(1)

    def pretty_format(self, batches):
        def geth(h='=', n=40):
            res = ''
            for i in range(n):
                res += h
            return res

        result = '%3s%20s%10s\r\n' % ('ID', 'Test_bed_name', 'Build')
        result += geth(h='-')+"\n\r"
        for x in batches:
            result += '%3d ' % x.id
            result += '%20s ' % str(x.testbed)
            result +="%10s\r\n" % str(x.build)
        result += geth(h='-')+"\n\r"
        return result


class TLController():
    '''
    Instance for retrieve data from TL, mapp data from Rat to TL, and report data to TL.
    '''
    def __init__(self, param_mgr):
        self.cfg = {
            'server_url': 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php',
            'dev_key': '4a21255bbbe77e64a6c5a75439b3704b',
            'project': 'Zone Director',
            'plan': 'Toronto 9.1 Automation',
            'build': '9.1.0.0.9',
        }
        self.update_param(param_mgr)
        #Create TestLinkClient
        self.tlc = TestlinkClient22(self.dev_key, self.server_url)
        self.flag = False#competition resource 

    def update_param(self, param_mgr):
        self.cfg.update(**param_mgr.get_tl_param())
        self.server_url = self.cfg[param_mgr.SERVER_URL]
        self.dev_key = self.cfg[param_mgr.DEV_KEY]
        self.project = self.cfg[param_mgr.PROJECT]
        self.plan = self.cfg[param_mgr.PLAN]
        self.build = self.cfg[param_mgr.BUILD]
        self.auto_cases_top_folder = self.cfg[param_mgr.AUTO_CASES_TOP_FOLDER]
        update_test_db.AUTO_CASES_TOP_FOLDER_LIST = [self.auto_cases_top_folder]
#        print 'update AUTO_CASES_TOP_FOLDER_LIST to %s' % update_test_db.AUTO_CASES_TOP_FOLDER_LIST      
        db_env.AUTO_CASES_TOP_FOLDER_LIST = [self.auto_cases_top_folder]
#        logging.info('Update AUTO_CASES_TOP_FOLDER_LIST TO %s' % db_env.AUTO_CASES_TOP_FOLDER_LIST)

    #get test link client instance.
    def get_connector(self):
        return self.tlc
    
    def set_flag(self, tag):
        self.flag = tag
    
    def get_flag(self):
        return self.flag
    
    def full_report(self):
        '''
        Do retrieve & map & report data once time.
        '''
        self.retrieve_data()
        self.map_data()
        self.report_data()
    
    def pp(self, msg=''):
        print msg
    
    #retrieve data from TL.
    def retrieve_data(self, writer=None):
        pp = writer if writer else self.pp
        cnt = 10
        while cnt:
            try:      
                pp('Starting...')
                res = update_test_db.update_test_db(self.tlc, self.project, self.plan)                                
                pp('Retrieve data DONE!')  
                return res    
            except Exception, e:
                logging.debug(traceback.format_exc())                
                logging.info('Try to retrieve data from project [%s], test plan [%s], but failure, detail [%s]' % 
                             (self.cfg['project'], self.cfg['plan'], e))
                cnt -= 1
                logging.info('Go to pending, wait for %d' % (5 * (11-cnt)))
                time.sleep(5 * (11-cnt))
                
        logging.debug('Please check your network, we have tried 10 times, but failure always.')

    #map data from TL to rat.
    def map_data(self):        
        map_test_run.main(**self.cfg)

    #report test result data from rat to TL.
    def report_data(self):
        cnt = 10
        while cnt:
            try:        
                project_id = self.tlc.get_project_by_name(self.project)[0]['id']
                builds = self.tlc.get_builds_by_plan_name(self.project, self.plan)        
                for b in builds:
                    if b['name'] == self.build:
                        build_id = b['id']
                        plan_id = b['testplan_id']
                        break
        
                logging.info('Begin to report...')        
                rm = TLReportMgr(self.tlc, project_id, plan_id, build_id)            
                rm.main()
                return
            except UnboundLocalError:
                logging.info(traceback.format_exc())
                logging.info('Quit to report')
                return
            except:
                logging.info(traceback.format_exc())                
                cnt -= 1
                logging.info('Go to pending, wait for %d' % (5 * (11-cnt)))
                time.sleep(5 * (11-cnt))
        
        
        logging.debug('Please check your network, we have tried 10 times, but failure always.')


class DailybuildController():
    """
    Manager daily build request.
    Update auto execution object.
    Follow command to QARunner.
    """
    DAILYBUILD_PLAN = "Sandbox Automation"
    TOP_SUITE = "Sandbox Automation"
    
    
    def __init__(self, executor, param_mgr):
        self.executor = executor
        self.param_mgr = param_mgr
    
    def update_auto_obj(self, tbname, bstream, bno):
        """
        Update auto execution object.
        @param tbname: test bed name.
        @param bstream: build stream name.
        @param bno: build number.
        """        
        tbs = rat_m.AutotestConfig.objects.filter(testbed__name = tbname, 
                                                  build_stream__name=bstream)
        if not tbs:
            tbs = rat_m.AutotestConfig.objects.filter(testbed__name = tbname)
            if not tbs:
                logging.debug("Haven't found test bed [%s]" % tbname)
                return (False, None)
            
            else:
                logging.info("Create a new Build Stream")
                bs = rat_m.BuildStream()
                bs.name = bstream
                PREFIX_INDEX = 1
                bs.prefix = bstream.split("_")[PREFIX_INDEX]
                bs.URL = "http://nanhu.tw.video54.local"
                bs.save(force_insert=True)
                
                #Clone an AutotestConfig
                tb = tbs[0]
                newtb = rat_m.AutotestConfig()
                newtb.testbed = tb.testbed
                newtb.suites = tb.suites
                newtb.build_stream = bs
                newtb.lastbuildnum = bno
                newtb.save(force_insert=True)
                                
                #Check and Create Build
                self._create_build(bstream, bno)
                    
        elif len(tbs)>1:
            logging.debug("More than one test bed[%s, %s], please remove one." % tbname, bstream)
            return (False, None)
        
        else:
            #Skip previous tasks.
            rat_m.AutotestExecution.objects.all().update(skip_run=True)
            #Check and Add AutoExecution Task
            autoconfig = tbs[0]
            tasks = rat_m.AutotestExecution.objects.filter(autoconfig = autoconfig, build_number = bno)
            if tasks:
                logging.info("Have a task in queue.")
                tasks[0].skip_run = False
                tasks[0].save(force_update=True)
                self._create_build(bstream, bno)
                              
                return (True, tasks[0])
            
            else:
                tasks = rat_m.AutotestExecution.objects.filter(autoconfig = autoconfig)
                if tasks:
                    task = tasks[0]
                    #Clone a Task
                    newtask = task.clone()
                    newtask.build_number = bno
                    newtask.skip_run = False
                    newtask.save(force_insert=True)    
                    return (True, newtask)
                
                else:
                    #Create a New Task
                    newtask = rat_m.AutotestExecution()
                    newtask.autoconfig = autoconfig
                    newtask.build_number = bno                    
                    obj = rat_m.TestPlan.objects.filter(name=self.DAILYBUILD_PLAN)[0]
                    newtask.test_plan = obj
                    newtask.top_suite = self.TOP_SUITE
                    newtask.save(force_insert=True)
                    
                    self._create_build(bstream, bno)
                                    
                    return (True, newtask)
        
    
    def _create_build(self, bstream, bno):
        #Check and Create Build
        bss = rat_m.BuildStream.objects.filter(name=bstream)
        if bss:
            bs = bss[0]
        else:
            logging.warning("Haven't found build stream [%s]" % bstream)
            return False
        
        builds = rat_m.Build.objects\
            .filter(build_stream = bs)\
            .filter(number = bno)
            
        if not builds:
            BUILD_PREFIX_INDEX = 1
            build = rat_m.Build()
            build.build_stream = bs
            build.number = bno            
            build.version = "%s.%s" % (build.build_stream.name.split("_")[BUILD_PREFIX_INDEX], bno)
            build.label =  build.version
            build.timestamp = datetime.datetime.now()
            build.URL = "http://nanhu.tw.video54.local"
            build.save(force_insert=True)
        
        return True
    
    def fire_on(self,cmdstr):
        tbname = self.param_mgr.get_tb_name()
        m = re.match(r'\s*([^\s]+)\s+(\d+)(.*)', cmdstr)
        if m:
            bstream, bno, cmdopts = m.group(1), m.group(2), m.group(3)
            logging.info('buildstream[%s], testbed[%s], bno[%s], options[%s]' \
                         % (bstream, tbname, bno, cmdopts))
            
            (res, obj) = self.update_auto_obj(tbname, bstream, int(bno))
            if res:
                msg = 'Update AutoExecution DONE.'
                logging.info(msg)
                #Get AutoExecution and push to QARunner
                self.executor.add_task(obj)
                
                msg = "Task in Queue, System will assign to execution."
                logging.info(msg)                
                return msg
            
            else:
                msg = 'Update AutoExecution FAIL, please check command [%s].' % cmdstr                
                logging.debug(msg)
                return msg
                        
        else:
            msg = "Wrong Command [%s]." % cmdstr
            logging.debug(msg)
            return msg
                 
        
class UserRequestHandler(StreamRequestHandler):
    '''
        Handler customer command.
    '''
    def writeln(self, x):
        if x:
            self.wfile.write(x+"\r\n")

    def setup(self):
        StreamRequestHandler.setup(self)
        logging.info('%s%s' % (self.client_address, ' connected'))
        self.writeln("Hello" + str(self.client_address))
        self.inbuf = ''
        
    def handle_tl_cmd(self, cmd):
        '''
        TL command like get/map/put etc.
        '''
        if re.match('^TL\s*get', cmd, re.I):
                if invoker['ctl'].get_flag():
                    self.writeln('Auto report process is handling, please re-try later on')
                    
                else:
                    invoker['ctl'].set_flag(True)
                    try:
                        _tt = threading.Thread(target = invoker['ctl'].retrieve_data, 
                                               kwargs = {'writer':self.writeln})
                        _tt.start()
                        
                    finally:
                        invoker['ctl'].set_flag(False)
                        
        elif re.match('^TL\s*put', cmd, re.I):
            if invoker['ctl'].get_flag():
                self.writeln('Auto report process is handling, please re-try later on')
                
            else:
                invoker['ctl'].set_flag(True)
                try:
                    invoker['ctl'].report_data()
                    self.writeln('report data DONE!')
                    
                finally:
                    invoker['ctl'].set_flag(False)                    
            
        elif re.match('^TL\s*map', cmd, re.I):                    
            if invoker['ctl'].get_flag():
                self.writeln('Auto report process is handling, please re-try later on')
                
            else:
                invoker['ctl'].set_flag(True)
                try:                        
                    invoker['ctl'].map_data()
                    self.writeln('Mapping DONE!')
                    
                finally:
                    invoker['ctl'].set_flag(False)
                    
        elif re.match('^TL\s*all', cmd, re.I):                    
            if invoker['ctl'].get_flag():
                self.writeln('Auto report process is handling, please re-try later on')
                
            else:
                invoker['ctl'].set_flag(True)
                try:                        
                    invoker['ctl'].full_report()
                    self.writeln('Get/Map/Put DONE!')
                    
                finally:
                    invoker['ctl'].set_flag(False)
                    
        elif re.match('^TL\s*clear', cmd, re.I):
            from Testlink import models as TLM
            tcs = TLM.ProjectTestCase.objects.all()
            for tc in tcs:
                tc.delete()
                
            bs = TLM.TestBuild.objects.all()
            for x in bs:
                x.delete()
            
            tps = TLM.TestPlan.objects.all()
            for x in tps:
                x.delete()
            
            self.writeln("Clear Local Test Link DONE!")
                        
        else:
            self.writeln('Command# ')

    def handle_batch_cmd(self, cmd):
        '''
        BATCH command like del/list/report test.
        '''
        m = re.match('^batch\s*(.+)', cmd, re.I)
        if m:
            params = m.group(1)
            if re.match('^(\d+)\s*', params, re.I):
                batch_id = int(params.strip())
                batches = invoker['mgr'].get_batch(batch_id)
                
                if type(batches) is not str:
                    self.writeln(invoker['mgr'].pretty_format(batches))
                    
                else:
                    self.writeln(batches)

            elif re.match('^del\s*(\d+)', params, re.I):
                res = re.match('^del\s*(\d+)', params, re.I)
                batch_id = int(res.group(1))
                (res, info) = invoker['mgr'].del_batch(batch_id)
                self.writeln(info)

            elif re.match('^list', params, re.I):
                batches = invoker['mgr'].list_batches()
                self.writeln(invoker['mgr'].pretty_format(batches))
                
            elif re.match('^report', params, re.I):
                invoker['ctl'].report_data()
                self.writeln('Data has been reported to TL successfully')
                
            else:
                self.writeln('Command# ')
        else:
            batches = invoker['mgr'].list_batches()
            self.wfile.write(invoker['mgr'].pretty_format(batches))
    
    def handle_set_cmd(self, cmd):
        '''
        Update like server_url, dev_key, project, plan, build.
        '''
        res = re.match('^set\s*(\w+)=(.+)', cmd, re.I)
        key = res.group(1)
        value = res.group(2)
        pmgr = invoker['param']
        if key in [pmgr.SERVER_URL, pmgr.DEV_KEY, pmgr.PROJECT, pmgr.PLAN, pmgr.BUILD]:
            try:
                (res, info) = pmgr.set_key_value(key, value)
                invoker['ctl'].update_param(pmgr)
                self.writeln(info)
                
            except Exception, e:
                self.writeln('key [%s] setting is unsuccessful, detail %s' % (key, e))
                
        if key in [pmgr.pmgr.TESTBED_NAME]:
            try:
                (res, info) = pmgr.set_tb_name(value)                
                self.writeln(info)                
            except Exception, e:
                self.writeln('key [%s] setting is unsuccessful, detail %s' % (key, e))
    
    def _clean_rat_thread(self, task = 'rat_task'):
        try:
            if task in invoker and invoker[task]:
                del(invoker[task])
                invoker[task] = None
                
        except:
            logging.debug(traceback.format_exc())
            
    
    
    def handle_daily_build_cmd(self, cmd):
        '''
        Parse daily build command from RD team.
        '''
        res = re.match('^dev\s*(.+)', cmd, re.I)        
        if res:
            params = res.group(1)
            msg = invoker['daily_build'].fire_on(params)
            self.wfile.write(msg)
            
        else:            
            self.writeln('Command# ')
            
    
    def handle_rat_cmd(self, cmd):
        '''
        Parse auto-execution command, like start, stop, reload.
        '''        
        res = re.match('^rat\s*(.+)', cmd, re.I)
        if res:
            params = res.group(1)
            if re.match('^start', params, re.I):
                #load execution list by priority.
                #start qarun.py testing.   
                self._clean_rat_thread()             
                _task = threading.Thread(target=invoker['rat'].start, kwargs = {'writer':self.writeln})
                _task.start()
                invoker['rat_task'] = _task
                
            elif re.match('^stop', params, re.I):
                #stop execution list.
                self._clean_rat_thread()                
                _task = threading.Thread(target=invoker['rat'].stop, kwargs = {'writer':self.writeln})
                _task.start()          
                invoker['rat_task'] = _task  
                                        
            elif re.match('^reload', params, re.I):               
                res = re.match('^reload\s*(\w+)\s*=\s*(.+)', params, re.I)                
                if res:
                    k, v = res.group(1), res.group(2)
                    #reload execution list and stop current task immediately.
                    if k.lower() == 'enforce':
                        kwargs = {'writer':self.writeln,
                                  'enforce': eval(v)
                                  }           
                        self._clean_rat_thread()             
                        _task = threading.Thread(target=invoker['rat'].reload, kwargs = kwargs)
                        _task.start()
                        invoker['rat_task'] = _task
                        
                else:
                    #reload execution list, QARunner will use the latest list to execute till finish current testing.
                    kwargs = {'writer':self.writeln}           
                    self._clean_rat_thread()             
                    _task = threading.Thread(target=invoker['rat'].reload, kwargs = kwargs)
                    _task.start()
                    invoker['rat_task'] = _task
                    
            elif re.match('^get\s+cur', params, re.I):
                info = invoker['rat'].get_cur_tb()
                self.writeln(info)
                
            elif re.match('^get\s+all\s+cur', params, re.I):
                invoker['rat'].get_all_cur_tb(self.writeln)
                
            elif re.match('^report', params, re.I):
                self._clean_rat_thread() 
                _task = threading.Thread(target=invoker['rat'].report, kwargs = {'writer':self.writeln})
                _task.start()
                invoker['rat_task'] = _task      
                       
            else:
                self.wfile.write(help("rat"))
        else:
            self.writeln('Command# ')
                
    
        
           
    def handle(self):
        while True:            
            cmd = self.rfile.readline().strip()
            if len(cmd) == 0:
                self.wfile.write('Command# ')
                
            elif cmd == "p":
                self.wfile.write('INFO: %s\r\nCommand# ' % str(invoker))
                pprint(invoker)
                
            elif cmd == "pp":
                result = mojo_output(pformat(invoker))
                self.wfile.write('INFO:\r\n%s\r\nCommand# ' % result)
                                
            elif re.match('^(close|shutdown)$', cmd, re.I):
                self.wfile.write('SHUTDOWN:')
                invoker['server'].server_close()
                return
            
            elif re.match('^(exit|stop|quit|bye)', cmd, re.I):
                self.wfile.write('BYE.BYE!')
                return
            
            elif re.match('^debug$', cmd, re.I):
                self.wfile.write('\r\nDebug?')
                pdb.set_trace()
                
            elif re.match('^(help)', cmd, re.I):
                res = re.match('^help\s*(.+)', cmd, re.I)
                if res:
                    self.wfile.write(help(res.group(1).lower().strip()))
                    
                else:
                    self.wfile.write(help())
                self.wfile.write('\r\nCommand# ')
                
            elif re.match('^batch', cmd, re.I):
                self.handle_batch_cmd(cmd)
                
            elif re.match('^TL', cmd, re.I):
                self.handle_tl_cmd(cmd)
                   
            elif re.match('^RAT', cmd, re.I):
                self.handle_rat_cmd(cmd)
                
            elif re.match('^DEV', cmd, re.I):
                self.handle_daily_build_cmd(cmd)
                           
            elif re.match('^set\s*(\w+)=(.+)', cmd, re.I):
                self.handle_set_cmd(cmd)
                
            elif re.match('^list param', cmd, re.I):
                self.wfile.write(pretty_print(invoker['param'].get_tl_param()))
                
            else:
                self.wfile.write(help())
                self.wfile.write('\r\nCommand# ')

    def finish(self):
        logging.info('%s%s' % (self.client_address, 'disconnected!'))
        self.request.send('BYE ' + str(self.client_address) + '\r\n')
        try:
            del(CurrClient[self.client_address])
            
        except Exception:
            pass
        
        StreamRequestHandler.finish(self)

if __name__ == '__main__':
#    param = ParamMgr()
#    ctl = RatTLControl(param)
#    ctl.report_data()
    from RuckusAutoTest.common.lib_KwList import as_dict
    _dict = as_dict(sys.argv[1:])
    RatLogger.init_logger('server.sys')
    RatLogger.close_logger()
    RatLogger.next_logger('server', "Invoker_%s" % RatLogger.get_logger_timestr())
    
    try:
        start_server(**_dict)
        
    except Exception, e:        
        logging.debug("\n\n%s" % ('!' * 68))
        ex =  traceback.format_exc()
        logging.debug(ex)
        
    finally:
        RatLogger.close_logger()
