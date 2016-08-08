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

from xlwt import *
from pprint import pformat
from ratenv import *

from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common.Ratutils import ping, send_mail
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_zd_by_ip_addr, create_zd_cli_by_ip_addr, clean_up_rat_env


mailcfg = {'mailserver': '172.16.110.5', 
           'sender': 'fm.reallife@ruckuswireless.com',
           'receiver': ['an.nguyen@ruckuswireless.com', 'ives.liu@ruckuswireless.com']
           }

mycfg = {'testname': 'Reallife test monitoring',
         'product': 'Ruckus ZoneDirector',
         }

testcfg = {'gap_duration': 300,
           'daily_report_time': 16, # 24 hours format
           'num_of_events': 100,
           #'interval': 10,
           #'ping_timeout': 120,
           #'access_retry': 3,
           #'access_waiting_gap_time': 30,
           }

result = {}

zdcfg = {
#         '192.168.0.2': {'username': 'admin',
#                            'password': 'admin',
#                            'shell_key': '!v54! HCoeY6vNaxZ.CtwvEXnd9G6Gl@hSXa@A',
#                            'type': 'zd3k',
#                            },
         '192.168.103.245': {'username': 'admin',
                            'password': 'admin',
                            'shell_key': '!v54! 14c@hJEeVD0a2bb8t9GoTF.zfd6@vd71',
                            'type': 'zd3k',
                            },
        '192.168.104.49':   {'username': 'admin',
                            'password': 'admin',
                            'shell_key': '!v54! JiEAUmCHZbXvhilRsw5F4xSQHj51C7Rh',
                            'type': 'zd3k',
                           },
        '192.168.103.244': {'username': 'admin',
                            'password': 'admin',
                            'shell_key': '!v54! @Zktkv80UZih3O@ycT7wLulTgYSLpzu1',
                            'type': 'zd3k',
                           },
        '192.168.103.250': {'username': 'admin',
                            'password': 'admin',
                            'shell_key': '!v54! Slt2fvBPEe8OMvFqNVaMods49SDBfAah',
                            'type': 'zd1k1',
                           },
      #  '192.168.20.89': {'username': 'admin',
      #                      'password': 'admin',
      #                      'shell_key': '!v54! PLBbeyW8iLH6moKZLd98nLW5nDbWG4yV',
      #                      'type': 'zd1k1',
       #                    },
         }

socket_warning_value = 10000
cpu_warning_info = {'zd1k': 90,
                    'zd1k1': 90,
                    'zd3k': 50,
                    'zd5k': 8}
start_time =  time.strftime("%Y%m%d%H%M")
potential_issues = ['System cold restarted', 'Lost contact with AP']
log_folder = 'C:\\Reallife\\Logs\\'
potential_issues_file_path = log_folder + 'potential_issues.txt'
record_file =  log_folder + '[%s] recording the ZD monitoring status.txt' % start_time
zd_log_file_name = log_folder + '[%s] monitoring log for ZD[%s].txt' 
issue_report_file_name = log_folder + '[%s] issue report.txt'
daily_report_file_name = log_folder + '[%s] daily report.txt'
cpu_info_wb_name = log_folder + '[%s] cpu info.xls' % start_time
cpu_info_bkup_wb_name = log_folder + '[Copy][%s] cpu info.xls' % start_time

date_style = easyxf(num_format_str='YYYY-MM-DD HH:MM:SS')
normal_style = easyxf()
alarm_style = easyxf('borders: left thick, right thick, top thick, bottom thick; pattern: pattern solid, fore_colour red;')
running_style = easyxf('borders: left thick, right thick, top thick, bottom thick; pattern: pattern solid, fore_colour blue;')

cpu_info_wb = Workbook()

cols_map = ['Time', 'Used CPU', 'Used Memory', 'Total Memory', 'Free Memory', 'CPU IDLE']

for key in zdcfg.keys():
    ws = cpu_info_wb.add_sheet('ZD %s' % key, cell_overwrite_ok = True)
    ws.row(0).write(1, 'CPU INFO RECORD FOR ZD %s' % key)
    ws.row(1).write(1, 'Start record')
    structime = time.localtime()
    ws.row(1).set_cell_date(2, datetime.datetime(*structime[:6]), date_style)
    ws.row(1).write(4, 'Last update')
    structime = time.localtime()
    ws.row(1).set_cell_date(5, datetime.datetime(*structime[:6]), date_style)
    
    for col_name in cols_map:
        ws.row(3).write(cols_map.index(col_name), col_name)    
    zdcfg[key].update({'ws': ws})
    
cpu_info_wb.save(cpu_info_wb_name)

#
#
#

def _update_potential_issues():
    try:
        ifile =  open(potential_issues_file_path, 'r')
        contents = ifile.readlines()
        ifile.close()
        return contents
    except:
        return []

def _ping_to_zd(zd_ip):
    res = ping(zd_ip)
    return ('Timeout' not in res)

def _verify_zd_info(zd_ip, cfg):
    zdcfg = cfg['zdcfg'][zd_ip]
    
    zdwebui = _create_zd_webui(zd_ip, zdcfg)
    cfg['result'][zd_ip]['webobj'] = zdwebui
    if not zdwebui:
        msg = '[Skip to verify ZD logs/events] Can not access the ZD[%s] WebUI' % zd_ip
        _update_log_files(cfg['result']['logfiles'].values(), msg)
    else: 
        print '\nVerify the ZD[%s] logging info' % zd_ip
        _verify_zd_log(zd_ip, cfg)
    
    zdcli = _create_zd_cli(zd_ip, zdcfg)
    cfg['result'][zd_ip]['cliobj'] = zdcli
    if not zdcli:
        msg = '[Skip to verify ZD CPU using and Socket info] Can not access the ZD[%s] CLI' % zd_ip
        _update_log_files(cfg['result']['logfiles'].values(), msg)
    else:
        print '\nVerify the ZD[%s] sockets info' % zd_ip
        _verify_zd_socket(zd_ip, cfg)
        print '\nVerify the ZD[%s] cpu using info' % zd_ip
        _verify_zd_cpu(zd_ip, cfg)
    
    try:
        zdwebui.destroy()
        zdcli.close()
        clean_up_rat_env()
    except:
        pass

def _update_log_files(file_list, msg):
    if type(msg) == str:
        print msg
        for rfile in file_list:
            rfile.write(msg)
            rfile.write('\n')
        return
    
    print pformat(msg, 4, 500)
    for rfile in file_list:
        rfile.write(pformat(msg, 4, 500))
        rfile.write('\n')
    
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
    potential_issues.extend(_update_potential_issues())
    
    zdwebui = cfg['result'][zd_ip]['webobj']
    msg = 'Get and verify the last %s events on ZD[%s] WebUI:' % (cfg['testcfg']['num_of_events'], zd_ip)
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    try:
        curr_logs = lib.zd.zd_log.get_events(zdwebui, **{'num_of_events': cfg['testcfg']['num_of_events']})
    except:
        msg = '[ERROR] Can not get the events on ZD[%s] WebUI' % zd_ip
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        return
    
    new_logs = []
    issue_logs = []     
    for log in curr_logs:
        if str(log) in cfg['result'][zd_ip]['last_events']:
            continue
                        
        new_logs.append(str(log))
        for issue in potential_issues:
            if str(issue).strip('\n') in str(log['activities']):
                issue_logs.append(str(log))
    
    cfg['result'][zd_ip]['last_events'].append(new_logs)
    cfg['result'][zd_ip]['all_err_logs'].append(issue_logs)    
    
    if not new_logs:
        msg = '-------- No new event is founded on ZD[%s] ---------' % zd_ip
        _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                           cfg['result']['logfiles']['daily_logfile']],
                          msg)
    else:
        msg = '-------- %s new events are founded on ZD[%s] --------' % (len(new_logs), zd_ip)
        _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                           cfg['result']['logfiles']['daily_logfile']],
                          msg)
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], new_logs)        
            
    if issue_logs:
        msg = '-------- %s potential events are founded on ZD[%s]--------' % (len(issue_logs), zd_ip)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        _update_log_files([cfg['result']['logfiles']['zd_logfile'], 
                           cfg['result']['logfiles']['err_logfile']],
                          issue_logs)
    
def _verify_zd_socket(zd_ip, cfg):
    """
    When the size over 10000 it keep the system busy
    """
    zdcli = cfg['result'][zd_ip]['cliobj']
    msg = 'Get and verify the sockets info under ZD[%s] CLI:' % zd_ip
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    
    try:
        info = lib.zdcli.shell.get_netstat_info(zdcli)
        socket_info = info['active_unix_domain_sockets']
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], socket_info)
    except Exception, e:
        msg = '[ERROR] Can not get the sockets information of ZD[%s]: %s' % (zd_ip, e.message)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        return
    
    warning_info = []
    warning_value = socket_warning_value
    for info in socket_info:
        if int(info['refcnt']) >= warning_value:
            warning_info.append(info)
    
    if warning_info:
        msg = '-------- %s potential events are founded from socket info of ZD[%s] --------' % (len(warning_info), zd_ip)
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
    msg = 'Get and verify the CPU using info under ZD[%s] CLI:' % zd_ip
    _update_log_files([cfg['result']['logfiles']['zd_logfile'],
                       cfg['result']['logfiles']['daily_logfile']],
                      msg)
    try:
        verify_time = time.localtime()
        info = lib.zdcli.shell.get_cpu_using_info(zdcli)
        cpu_info = info['detail_set']
        _update_log_files([cfg['result']['logfiles']['zd_logfile']], cpu_info)
        res = _collect_cpu_mem_info(datetime.datetime(*verify_time[:6]), cpu_info)
        _update_cpu_mem_info_sheet(zd_ip, res)
    except Exception, e:
        msg = '[ERROR] Can not get the CPU using information of ZD[%s]: %s' % (zd_ip, e.message)
        _update_log_files(cfg['result']['logfiles'].values(), msg)
        return
    
    warning_info = []
    warning_value = cpu_warning_info[cfg['zdcfg'][zd_ip]['type']]
    for info in cpu_info:
        cpu_using = info['cpu_info']
        total_using_cpu = int(cpu_using['usr']) + int(cpu_using['sys']) + int(cpu_using['nic'])\
                          + int(cpu_using['io']) + int(cpu_using['irq']) + int(cpu_using['sirq'])
        if total_using_cpu >= 90:
            msg = '[ZD %s is so busy] Total used CPU is %s.' % (zd_ip, total_using_cpu)
            warning_info.append(msg)
            
        thread_info = info['thread_info']
        for pid in thread_info.keys():
            if thread_info[pid]['stat'] == 'R' and int(thread_info[pid]['cpu']) == warning_value:
                msg = '[ZD %s is stress] The thread %s is full used of the core [%s] !!!' % (zd_ip, pid, thread_info[pid])
                warning_info.append(msg)
    
    if warning_info:
        msg = '\n-------- %s potential events are founded from ZD[%s] CPU info--------' % (len(warning_info), zd_ip)
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
        lines = errfile.readlines()
        for line in lines:
            body = body + line
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
        _update_log_files([conf['record_file']], msg)

    except Exception, e:
        msg = 'sendMail failed: %s' % (e.message)
        print msg
        _update_log_files([conf['record_file']], msg)

def _mail_out_the_daily_report(conf):
    subject = '[%s] Daily report' % conf['mycfg']['testname']
    body = 'Dear Testers, \n\n I would like to update the daily status as below:'
    try:
        print 'mail subject:"%s" to %s' % (subject, mailcfg['receiver'])
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nDetail'
        body = body + '\n--------------------------------------------------------------\n'
        errfile = open(conf['result']['daily_logfile_name'], 'r')
        lines = errfile.readlines()
        for line in lines:
            body = body + line
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
        _update_log_files([conf['record_file']], msg)
        
    except Exception, e:
        msg = 'sendMail failed: %s' % (e.message)
        print msg
        _update_log_files([conf['record_file']], msg)

def _mail_out_the_summary_report(conf):
    subject = '[%s] The script is stopped!' % conf['mycfg']['testname']
    body = 'Dear Testers, \n\n Please look at the long life test bed, the script is stop by below summary:'
    try:
        print 'mail subject:"%s" to %s' % (subject, mailcfg['receiver'])
        body = body + '\n--------------------------------------------------------------'
        body = body + '\nDetail'
        body = body + '\n--------------------------------------------------------------\n'
        errfile = open(record_file, 'r')
        lines = errfile.readlines()
        for line in lines:
            body = body + line
        errfile.close()
        body = body + '\n--------------------------------------------------------------'
        body = body + '\n\nThanks :)'
        
        send_mail(mailcfg['mailserver'], mailcfg['receiver'], mailcfg['sender'], subject, body)
        
    except Exception, e:
        msg = 'sendMail failed: %s' % (e.message)
        print msg        

def _monitoring_zds_info(cfg):
    start_time = time.strftime("%Y%m%d%H%M")
    cfg['record_file'].write('\n[%s] Verifying the info of %s\n' % (start_time, cfg['zdcfg'].keys()))
    cfg['result']['err_logfile_name'] = issue_report_file_name % start_time
    
    for zd_ip in cfg['zdcfg'].keys():
        logfiles = dict(zd_logfile = open(cfg['result'][zd_ip]['logfile_name'], 'a'),
                        daily_logfile = open(cfg['result']['daily_logfile_name'], 'a'),
                        err_logfile = open(cfg['result']['err_logfile_name'], 'a'),)
         
        msg = 'Verifying the ZD[%s] at %s ....................' % (zd_ip, time.strftime("%Y%m%d%H%M"))
        _update_log_files([logfiles['zd_logfile'], logfiles['daily_logfile']], msg)
        
        cfg['result']['logfiles'] = logfiles        
        
        try:
            _verify_zd_info(zd_ip, cfg)
        except Exception, e:
            _update_log_files([cfg['record_file']], 'Exception: %s' % e.message)
        finally:
            for lfile in logfiles.values():
                lfile.close()

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
        if os.stat(conf['result']['err_logfile_name']).st_size:
            # send out the email when there is any potential issue
            _mail_out_the_potential_issues(conf)
        else:
            os.remove(conf['result']['err_logfile_name'])
            
        # send out the daily report email    
        now = datetime.datetime.now()
        if now.hour == conf['testcfg']['daily_report_time'] and now.day != last_day_report:
            _mail_out_the_daily_report(conf)
            _update_result_cfg(conf)
            last_day_report = now.day
            
        # waiting (idle) for next verifying
        print('\n\n-------------------------------------------------------------------------------')
        print('\n\t [%s] Waiting for %s seconds to the next verifying !!!') % (time.strftime("%Y%m%d%H%M"), 
                                                                               conf['testcfg']['gap_duration'])
        print('\n-------------------------------------------------------------------------------\n')
        time.sleep(conf['testcfg']['gap_duration'])
     
def _update_cpu_mem_info_sheet(zd_ip, infos, **kwargs):
    print 'Updating the info to the excel file'
    for info in infos:
        last_row = int(max(zdcfg[zd_ip]['ws'].rows.keys()))
        last_col_idx = len(cols_map)
        infokeys = info.keys()
        infokeys.sort()
        for key in infokeys:
            if key in cols_map:
                col_idx = cols_map.index(key)
            else:
                col_idx = last_col_idx
                last_col_idx += 1       
                
            if key == 'Time':
                zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key], date_style)
            elif key == 'Used CPU':
                if info[key] > cpu_warning_info[zdcfg[zd_ip]['type']]:
                    zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key], alarm_style)
                else:                    
                    zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key], normal_style)
            elif key in ['CPU IDLE', 'Used Memory', 'Total Memory', 'Free Memory']:
                zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key])
            elif key.startswith('R'):
                zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key], running_style)
            elif key.startswith('X') or key.startswith('Z'):
                zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, '[%s] DEAD process!!!' % info[key], alarm_style)
            else:
                zdcfg[zd_ip]['ws'].row(last_row+1).write(col_idx, info[key])   
    
    ws.row(1).set_cell_date(5, datetime.datetime(*structime[:6]), date_style)
    _save_cpu_info_wb()

def _update_cpu_mem_info(zd_ip, infos, **kwargs):
    for info in infos:
        rdata = ''
        for colname in cols_map:
            rdata = rdata + '%s\t' % info[colname]
                
        for key in info.keys():
            if key not in cols_map:
                rdata = rdata + '%s\t' % info[key]
                
    zdcfg[zd_ip]['txt'].write(rdata)

def _collect_cpu_mem_info(time, info):
    print 'Collecting the expected info ...'
    res_info = []
    for i in info:
        update_val = {}
        update_val['Time'] = time
        update_val['Used CPU'] = 0
        update_val['CPU IDLE'] = i['cpu_info']['idle']        
        update_val['Total Memory'] = float(i['mem_info']['used']) + float(i['mem_info']['free'])
        update_val['Free Memory'] = float(i['mem_info']['free'])
        update_val['Used Memory'] = float(i['mem_info']['used'])*100/(float(i['mem_info']['used']) + float(i['mem_info']['free']))
        
        for thread in i['thread_info'].values():
            key = '%s %s' % (thread['stat'], thread['pid'])
            value = '%s CPU: %s MEM: %s - Stat: %s Command: %s' % (thread['pid'], thread['cpu'] + ' %', thread['mem'] + ' %', 
                                                                   thread['stat'], thread['command'])
            update_val[key] = value
            update_val['Used CPU'] +=  float(thread['cpu'])
            
        res_info.append(update_val)
        
    return res_info
    
def _draw_the_cpu_charts():
    pass

def _save_cpu_info_wb(copy_file_name = ''):
    try:
        cpu_info_wb.save(cpu_info_wb_name)
    except:
        if copy_file_name:
            try:
                cpu_info_wb.save(copy_file_name)
            except:
                pass
        print 'The file can not access to write as this time please make sure the file is close'

if __name__ == "__main__":
    # Get the params from the execution command
    if len(sys.argv) < 2:
        print "The test will use the default configuration to forming the test"
        kwargs = {}
    else:
        kwargs = kwlist.as_dict(sys.argv[1:])

    conf = do_config(**kwargs)
    
    # Initial the log machine
    msg = 'Monitoring ZDs by below configuration: \n %s' % pformat(conf, 4, 120)
    print msg
    conf['record_file'].write(msg)
    
    try:
        # Run the monitoring
        do_monitor(conf)
    except Exception, e:
        conf['record_file'].write(e.message)        
    finally:
        conf['record_file'].close()
        _save_cpu_info_wb(cpu_info_bkup_wb_name)
        _mail_out_the_summary_report(conf)
