'''
Copyright (C) 2010 Ruckus Wireless, Inc.
@author: An Nguyen - an.nguyen@ruckuswireless.com
@since: Aug 2012

Monitoring the ZDs status in long life test by:
- ZD Logging
- ZD CPU using
- ZD socket info
'''

import sys, os, time, re, datetime

from pprint import pformat
from ratenv import *

from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common.Ratutils import ping, send_mail
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_zd_by_ip_addr, create_zd_cli_by_ip_addr, clean_up_rat_env


mailcfg = {'mailserver': '172.16.100.20', 
           'sender': 'zd.rat@ruckuswireless.com',
           'report': False, 
           'cc': False,
           'receiver': ['an.nguyen@ruckuswireless.com']}

mycfg = {'testname': 'Long life test monitoring',
         'product': 'Ruckus ZoneDirector',
         }

testcfg = {'gap_duration': 1800,
           'daily_report_time': 8, # 24 hours format
           'num_of_events': 100,
           'interval': 10,
           'ping_timeout': 120,
           'access_retry': 3,
           'access_waiting_gap_time': 30,
           }

result = {}

zdcfg = {'192.168.104.49': {'username': 'admin',
                            'password': 'admin',
                            'shell_key': '!v54! JiEAUmCHZbXvhilRsw5F4xSQHj51C7Rh',
                            'type': 'zd3k',
                           },
         }

socket_warning_value = 10000
cpu_warning_info = {'zd1k': 90,
                    'zd1k1': 90,
                    'zd3k': 50,
                    'zd5k': 8}
potential_issues = ['System cold restarted', 'Lost contact with AP']

log_folder = 'C:\\Automation\\Longlife\\Logs\\'
record_file =  log_folder + '[%s] recording the ZD monitoring status.txt' % time.strftime("%Y%m%d%H%M")
zd_log_file_name = log_folder + '[%s] monitoring log for ZD[%s].txt' 
issue_report_file_name = log_folder + '[%s] issue report.txt'
daily_report_file_name = log_folder + '[%s] daily report.txt'


def _ping_to_zd(zd_ip):
    res = ping(zd_ip)
    return ('Timeout' not in res)

def _verify_zd_info(zd_ip, cfg):
    zdcfg = cfg['zdcfg'][zd_ip]      
    
    zdwebui = _create_zd_webui(zd_ip, zdcfg)
    cfg['result'][zd_ip]['webobj'] = zdwebui
    if not zdwebui:
        msg = '\n[Skip to verify ZD logs/events] Can not access the ZD[%s] WebUI' % zd_ip
        _update_log_files(cfg['result']['logfiles'].values(), msg)
    else: 
        _verify_zd_log(zd_ip, cfg)
    
    zdcli = _create_zd_cli(zd_ip, zdcfg)
    cfg['result'][zd_ip]['cliobj'] = zdcli
    if not zdcli:
        msg = '\n[Skip to verify ZD CPU using and Socket info] Can not access the ZD[%s] CLI' % zd_ip
        _update_log_files(cfg['result']['logfiles'].values(), msg)
    else:
        print '\nVerify the ZD[%s] sockets info' % zd_ip
        _verify_zd_socket(zd_ip, cfg)
        print '\nVerify the ZD[%s] cpu using info' % zd_ip
        _verify_zd_cpu(zd_ip, cfg)
    
    try:
        zdwebui.destroy()
        del zdwebui
        zdcli.close()
        del zdcli
        clean_up_rat_env()
    except:
        pass

def _update_log_files(file_list, msg):
    print pformat(msg, 4, 500)
    for file in file_list:
        file.write(pformat(msg, 4, 500))
    file.write('\n')
    
def _create_zd_webui(zd_ip, zdcfg):
    zdwebui = None
    try:
        zdwebui = create_zd_by_ip_addr(zd_ip,
                                       zdcfg['username'],
                                       zdcfg['password'])
    except:
        pass
    
    return zdwebui

def _create_zd_cli(zd_ip, zdcfg):
    zdcli = None
    try:
        zdcli =  create_zd_cli_by_ip_addr(zd_ip,
                                          zdcfg['username'],
                                          zdcfg['password'],
                                          zdcfg['shell_key'])
    except:
        pass
    
    return zdcli

def _verify_zd_log(zd_ip, cfg):
    """
    """
    zdwebui = cfg['result'][zd_ip]['webobj']
    msg = '\nGet and verify the last %s events on ZD[%s] WebUI:' % (cfg['testcfg']['num_of_events'], zd_ip)
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    try:
        curr_logs = lib.zd.zd_log.get_events(zdwebui, **{'num_of_events': cfg['testcfg']['num_of_events']})
    except:
        msg = 'Can not get the events'
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        return
    
    new_logs = []
    issue_logs = []     
    for log in curr_logs:
        if log in cfg['result'][zd_ip]['last_events']:
            continue
                        
        new_logs.append(log)
        for issue in potential_issues:
            if issue in log['activities']:
                issue_logs.append(log)
    
    cfg['result'][zd_ip]['last_events'].append(new_logs)
    cfg['result'][zd_ip]['all_err_logs'].append(issue_logs)    
    
    if not new_logs:
        msg = '\n-------- No new event is founded ---------'
        _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                           cfg['result']['logfiles']['daily_logfile']],
                          msg)
    else:
        msg = '\n-------- %s new events are founded --------' % len(new_logs)
        _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                           cfg['result']['logfiles']['daily_logfile']],
                          msg)
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], new_logs)        
            
    if issue_logs:
        msg = '\n-------- %s potential events are founded --------' % len(issue_logs)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        _update_log_files([cfg['result']['logfiles']['zd_logfile'], 
                           cfg['result']['logfiles']['err_logfile']],
                          new_logs)
    
def _verify_zd_socket(zd_ip, cfg):
    """
    When the size over 10000 it keep the system busy
    """
    zdcli = cfg['result'][zd_ip]['cliobj']
    msg = '\nGet and verify the sockets info under ZD[%s] CLI:' % zd_ip
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    
    try:
        info = lib.zdcli.shell.get_netstat_info(zdcli)
        socket_info = info['active_unix_domain_sockets']
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], socket_info)
    except:
        msg = 'Can not get the sockets information'
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        raise
    
    warning_info = []
    warning_value = socket_warning_value
    for info in socket_info:
        if int(info['refcnt']) >= warning_value:
            warning_info.append(info)
    
    if warning_info:
        msg = '\n-------- %s potential events are founded --------' % len(warning_info)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        cfg['result']['logfiles']['zd_logfile'].writelines(warning_info)
        cfg['result']['logfiles']['err_logfile'].writelines(warning_info)
        
def _verify_zd_cpu(zd_ip, cfg):
    """
    zd1k and zd1k1 have 1 core - 90-100% cpu is full use of the core
    zd3k has 2 cores - any thread get 50% cpu is full use of the core
    zd5k has 12 cores - any thread get 8% cpu is full use of the core
    """
    zdcli = cfg['result'][zd_ip]['cliobj']
    msg = '\nGet and verify the CPU using info under ZD[%s] CLI:' % zd_ip
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    try:
        info = lib.zdcli.shell.get_cpu_using_info(zdcli)
        cpu_info = info['detail_set']
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], cpu_info)
    except:
        msg = 'Can not get the CPU using information'
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        return
    
    warning_info = []
    warning_value = cpu_warning_info[cfg['zdcfg'][zd_ip]['type']]
    for info in cpu_info:
        cpu_using = info['cpu_info']
        total_using_cpu = int(cpu_using['usr']) + int(cpu_using['sys']) + int(cpu_using['nic'])\
                          + int(cpu_using['io']) + int(cpu_using['irq']) + int(cpu_using['sirq'])
        if total_using_cpu >= 90:
            msg = '[System is so busy] Total used CPU is %s.' % total_using_cpu
            warning_info.append(msg)
            
        thread_info = info['thread_info']
        for pid in thread_info.keys():
            if thread_info[pid]['stat'] == 'R' and int(thread_info[pid]['cpu']) == warning_value:
                msg = 'The thread %s is full use of the core [%s] !!!' % (pid, thread_info[pid])
                warning_info.append(msg)
    
    if warning_info:
        msg = '\n-------- %s potential events are founded --------' % len(warning_info)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        cfg['result']['logfiles']['zd_logfile'].writelines(warning_info)
        cfg['result']['logfiles']['err_logfile'].writelines(warning_info)

def _mail_out_the_potential_issues(conf):
    subject = '[%s] Potential issues alarm!' % conf['mycfg']['testname']
    body = 'Dear Testers, \n\n Please look at the long life test bed, there are some potential issues have just pop up:'
    try:
        print 'mail subject:"%s" to %s' % (subject, mailcfg['receiver'])
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nDetail'
        body = body + '\n--------------------------------------------------------------'
        errfile = open(conf['result']['err_logfile_name'], 'r')
        body = body + errfile.read()
        errfile.close()
        body = body + '\n--------------------------------------------------------------\n'
        body = body + '\nPlease also review the files below for more detail:'
        body = body + '\n\t%s' % conf['result']['err_logfile_name']
        body = body + '\n\t%s' % conf['result']['daily_logfile_name']
        for zd_ip in conf['zdcfg'].keys():
            body = body + '\n\t%s' % conf['result'][zd_ip]['logfile_name']
        body = body + '\n\nThanks :)'
        
        send_mail(mailcfg['mailserver'], mailcfg['receiver'], mailcfg['sender'], subject, body)
        
        msg = '\n[%s] An email is sent out for the issues stored in file: %s' % (time.strftime("%Y%m%d%H%M"),
                                                                               conf['result']['err_logfile_name'])
        _update_log_files([cfg['record_file']], msg)

    except Exception, e:
        print 'sendMail failed: %s' % (e.message)

def _mail_out_the_daily_report(conf):
    subject = '[%s] Daily report' % conf['mycfg']['testname']
    body = 'Dear Testers, \n\n I would like to update the daily status as below:'
    try:
        print 'mail subject:"%s" to %s' % (subject, mailcfg['receiver'])
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nDetail'
        body = body + '\n--------------------------------------------------------------\n'
        errfile = open(conf['result']['daily_logfile_name'], 'r')
        body = body + errfile.read()
        errfile.close()
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nPlease also review the files below for more detail:'
        body = body + '\n\t%s' % conf['result']['daily_logfile_name']
        for zd_ip in conf['zdcfg'].keys():
            body = body + '\n\t%s' % conf['result'][zd_ip]['logfile_name']
        body = body + '\n\nThanks :)'
        
        send_mail(mailcfg['mailserver'], mailcfg['receiver'], mailcfg['sender'], subject, body)
        
        msg = '\n[%s] An email is sent out for daily report which detail is in file: %s' % (time.strftime("%Y%m%d%H%M"),
                                                                                          conf['result']['daily_logfile_name'])
        _update_log_files([cfg['record_file']], msg)
        
    except Exception, e:
        print 'sendMail failed: %s' % (e.message)

def _mail_out_the_summary_report(conf):
    subject = '[%s] The script is stopped!' % conf['mycfg']['testname']
    body = 'Dear Testers, \n\n Please look at the long life test bed, the script is stop by below summary:'
    try:
        print 'mail subject:"%s" to %s' % (subject, mailcfg['receiver'])
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nDetail'
        body = body + '\n--------------------------------------------------------------\n'
        errfile = open(record_file, 'r')
        body = body + errfile.read()
        errfile.close()
        body = body + '\n--------------------------------------------------------------'
        body = body + '\n\nThanks :)'
        print body
        send_mail(mailcfg['mailserver'], mailcfg['receiver'], mailcfg['sender'], subject, body)

    except Exception, e:
        print 'sendMail failed: %s' % (e.message)

def _monitoring_zds_info(cfg):
    start_time = time.strftime("%Y%m%d%H%M")
    cfg['record_file'].write('\n[%s] Verifying the info of %s\n' % (start_time, cfg['zdcfg'].keys()))
    cfg['result']['err_logfile_name'] = issue_report_file_name % start_time
    
    for zd_ip in cfg['zdcfg'].keys():
        logfiles = dict(zd_logfile = open(cfg['result'][zd_ip]['logfile_name'], 'a'),
                        daily_logfile = open(cfg['result']['daily_logfile_name'], 'a'),
                        err_logfile = open(cfg['result']['err_logfile_name'], 'a'),)
         
        msg = '\n\nVerifying the ZD[%s] at %s ....................' % (zd_ip, time.strftime("%Y%m%d%H%M"))
        _update_log_files([logfiles['zd_logfile'], logfiles['daily_logfile']], msg)
        
        cfg['result']['logfiles'] = logfiles        
        
        try:
            _verify_zd_info(zd_ip, cfg)
        finally:
            for file in logfiles.values():
                file.close()        

def _update_result_cfg(cfg):
    start_test_time = time.strftime("%Y%m%d%H%M")
    for zd_ip in cfg['zdcfg'].keys():
        zd_result = {'logfile_name': zd_log_file_name % (start_test_time, zd_ip),
                     'all_err_logs': [],
                     'last_events': [],
                    }
        cfg['result'][zd_ip] = dict(zd_result)
    
    cfg['result']['daily_logfile_name'] = daily_report_file_name % start_test_time

def do_config(**kwarg):
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        if testcfg.has_key(k):
            testcfg[k] = v
            
    cfg = {'mycfg': mycfg,
           'testcfg': testcfg,
           'zdcfg': zdcfg,
           'result': {},
           'record_file': open(record_file, 'a')
          }
            
    return cfg

def do_monitor(conf):
    last_day_report = ''
    _update_result_cfg(conf)
    while True:
        _monitoring_zds_info(conf)
        errfile = open(conf['result']['err_logfile_name'], 'r')
        # send out the email when there is any potential issue
        if errfile.read():
            errfile.close()
            _mail_out_the_potential_issues(conf)
        else:
            errfile.close()
            #os.remove(conf['result']['err_logfile_name'])            
            
        # send out the daily report email    
        now = datetime.datetime.now()
        if now.hour == conf['testcfg']['daily_report_time'] and now.day != last_day_report:
            _mail_out_the_daily_report(conf)
            _update_result_cfg(conf)
            
        # waiting (idle) for next verifying
        print('\n\n-------------------------------------------------------------------------------')
        print('\n\t [%s] Waiting for %s seconds to the next verifying !!!') % (time.strftime("%Y%m%d%H%M"), 
                                                                               conf['testcfg']['gap_duration'])
        print('\n-------------------------------------------------------------------------------\n')
        time.sleep(conf['testcfg']['gap_duration'])


if __name__ == "__main__":
    # Get the params from the execution command
    if len(sys.argv) < 2:
        print "The test will use the default configuration to forming the test"
        kwargs = {}
    else:
        kwargs = kwlist.as_dict(sys.argv[1:])

    conf = do_config(**kwargs)    
    
    # Initial the log machine
    msg = 'Monitoring ZDs by below configuration: \n %s' % pformat(conf['testcfg'], 4, 120)
    print msg
    conf['record_file'].write(msg)
    
    try:
        # Run the monitoring
        do_monitor(conf)
        
    finally:
        conf['record_file'].close()
        _mail_out_the_summary_report(conf)
       
