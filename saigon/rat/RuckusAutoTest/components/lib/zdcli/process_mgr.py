'''
Instance is used for get process status and diff those.
Created on Mar 18, 2011
@author: cwang@ruckuswireless.com
'''

import re
NORMAL_STATUS = {'D':'Uninterruptible sleep (usually IO)',
               'R':'Running or runnable (on run queue)',
               'S':'Interruptible sleep (waiting for an event to complete)',               
               'W':'paging (not valid since the 2.6.xx kernel',               
               }
ERROR_STATUS = {'T':'Stopped, either by a job control signal or because it is being traced.',
                'X':'dead (should never be seen)', 
                'Z':'Defunct ("zombie") process, terminated but not reaped by its parent.',               
                }

#----------------------------------#
#    Access Method                 #
#----------------------------------#
def get_process_status_all(zdcli):
    '''
    '''
    cmd = "ps"
    res = zdcli.do_shell_cmd(cmd)
    expr = "(\d+)\s+(\d+)\s+admin\s+(\d+)m?\s+([A-Z]+)\s*(.+)\\r\\n"
    return re.findall(expr, res, re.IGNORECASE)

def get_zombie_process_list(zdcli):
    res = get_process_status_all(zdcli)
    
    zlist=[]
    for info in res:
        if info[3] in ERROR_STATUS.keys():
            zlist.append(info[4])
    
    return zlist

def get_process_status(zdcli, pname):
    '''
     pname-->stamgr
     pname-->apmgr
    '''
    cmd = "ps aux | grep %s | grep -v grep" % pname
    res = zdcli.do_shell_cmd(cmd)
    expr = "(\d+)\s+(\d+)\s+admin\s+(\d+)m?\s+(.*)%s" % pname
    return re.findall(expr, res, re.IGNORECASE)

def get_webs_status(zdcli):
    return get_process_status(zdcli, 'webs')

def get_stamgr_status(zdcli):
    return get_process_status(zdcli, 'stamgr')

def get_apmgr_status(zdcli):
    return get_process_status(zdcli, 'apmgr')


def diff_pid_status(before, after):
    '''
        Input parameters:
            before: initial pid list.
            after : currently pid list.
    '''
    if _chk_root_pid(before, after):
        return (True, "PID doesn't change")
    else:
        return (False, "Before [%s], after [%s], it is different" % (before, after))

def chk_process_status_ok(cur_status):
    '''
        Input:
            cur_status: currently status information of process.            
    '''
    #"(\d+)\s+(\d+)\s+admin\s+(\d+)\s+(.*)%s" % pname
    if cur_status[0][3][0] in ERROR_STATUS.keys():
        return (False, "status %s is %s" % (cur_status, ERROR_STATUS[cur_status[0][3][0]]))
    else:
        return (True, "status %s is %s" % (cur_status, NORMAL_STATUS[cur_status[0][3][0]]))
        
    
#------------------------------------#
# Protected method.                  #
#------------------------------------#
def _chk_root_pid(before, after):
    '''
       Input parameters:
           before: last info of process.
           after : current info of process.
       Just make sure the first root pid number should be same.       
           
    '''
    #"(\d+)\s+(\d+)\s+admin\s+(\d+)\s+(.*)%s" % pname
    return before[0][0] == after[0][0]
     