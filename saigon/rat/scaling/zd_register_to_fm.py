"""
Examples:

    # show test case's default configuration
    tea.py scaling.zd_register_to_fm cfgonly=True
    tea.py scaling.zd_register_to_fm base_vm_ipaddr=192.168.2.101 base_zd_ipaddr=192.168.2.1 fm_url=192.168.1.101
    tea.py scaling.zd_register_to_fm zdid_first=0 zdid_last=3
    tea.py scaling.zd_register_to_fm zdid_first=3 zdid_last=5
    tea.py scaling.zd_register_to_fm zdid_first=5 zdid_last=10

    # restart all ZDVM's and disable ZD's FlexMaster attributes
    tea.py scaling.zd_register_to_fm fm_enabled=False

    # ZDVM's are UP; not need to start up them; register ZD to FM
    tea.py scaling.zd_register_to_fm fm_url=172.17.18.101 fm_interval=2 startup_zdvm=False 

    # scaling tests
    tea.py scaling.zd_register_to_fm shutdown_all=True
    tea.py scaling.zd_register_to_fm ratLogID=scaling fm_interval=1 fm_url=172.17.18.199
    tea.py scaling.zd_register_to_fm ratLogID=scaling fm_interval=1 fm_rul=172.17.18.101 startup_zdvm=False 

"""
from te import flexmaster as FM
import zdvm_agent as ZDVM
import logging
from pprint import pprint, pformat
import time

def ipv4_incrBy(ipv4_str, incr_by=1):
    ipv4 = int(ipv4_str)
    incr = int(incr_by)
    ipv4 += incr
    if ipv4 > 255:
        return (1, ipv4-256)
    return (0, ipv4)

def hostIpAddr_incrBy(host_ip_addr, incr_by=1):
    ipadr4 = host_ip_addr.split('.')
    idx=3
    while idx > 0:
        ov, nxt_ip = ipv4_incrBy(ipadr4[idx], incr_by)
        ipadr4[idx] = str(nxt_ip)
        if ov == 0:
            return '.'.join(ipadr4)
        incr_by = 1
        idx -= 1
    return '.'.join(ipadr4)

def defaultZDVMConfig(base_vm_ipaddr='192.168.2.101', base_zd_ipaddr='192.168.2.1', zdid_first=0, zdid_last=10, zds_per_vm=10):
    if (zdid_last - zdid_first) < 1:
        raise Exception("No ZDVM will be created! [zdid_first %s] [zdid_last %s]" % (str(zdid_first), str(zdid_last)))
    zdvm_cfg = {}
    for idx in range(zdid_first,zdid_last):
        setid = idx+1
        vm_ipaddr = hostIpAddr_incrBy(base_vm_ipaddr, idx)
        zd_ipaddr = hostIpAddr_incrBy(base_zd_ipaddr, (zds_per_vm*idx))
        zd_ipaddr_list = [hostIpAddr_incrBy(zd_ipaddr, x) for x in range(0,zds_per_vm)]
        zdvm_cfg[vm_ipaddr] = dict(setid=setid, zd_iplist=zd_ipaddr_list)
    return zdvm_cfg

def getTestConfig(_dict={}):
    cfg = dict(startup_zdvm=True,
               base_vm_ipaddr='192.168.2.101',
               base_zd_ipaddr='192.168.2.1',
               based_line='odessa',
               zdid_first=0, zdid_last=10, zds_per_vm=10,
               fm_url='172.17.18.101',
               fm_interval=5,
               fm_enabled=True,
               user='zdvm',
               passwd='tdcitms',
               asRoot=False,
               root_passwd='!v54!scale',
               debug=0,
               init=False)
    cfg.update(_dict)
    cfg['zdvm'] = defaultZDVMConfig(cfg['base_vm_ipaddr'], cfg['base_zd_ipaddr'], cfg['zdid_first'], cfg['zdid_last'])
    cfg['fm'] = dict(url=cfg['fm_url'], interval=cfg['fm_interval'], enabled=cfg['fm_enabled'])
    del cfg['base_vm_ipaddr'], cfg['base_zd_ipaddr'], cfg['zdid_first'], cfg['zdid_last']
    del cfg['fm_enabled'], cfg['fm_url'], cfg['fm_interval']
    return cfg

def shutdownAllZdvm(rcfg):
    tm0 = time.time()
    results = []
    fail_cnt = 0
    for zdvm_ip_addr, zdvm_info in rcfg['zdvm'].items():
        r_zdvm = ZDVM.main(ipaddr=zdvm_ip_addr,
                           setid=zdvm_info['setid'],
                           shutdown_all=True)
        if r_zdvm[0] == 'FAIL':
            fail_cnt += 1
        results.append((r_zdvm,))
    tm1 = time.time()
    tc_elapsed_time = tm1 - tm0
    verdict = 'FAIL' if fail_cnt else 'PASS'
    logging.info( "[Tc.Name shutdownAllZdvm] [Result %s] [elapsed_time %d] result detail:\n%s"
                % (verdict, tc_elapsed_time, pformat(results, 4, 120)))
    return (verdict, tc_elapsed_time, results)

def secondsToString(_seconds):
    _seconds = int(_seconds)
    _mins = _seconds / 60
    _seconds = _seconds % 60
    _hours = _mins / 60
    _mins = _mins % 60
    if _hours > 23:
        _days = _hours / 24
        _hours = _hours % 24
        return "%02dd:%02dh:%02dm" % (_days, _hours, _mins)
    elif _hours > 0:
        return "%02dh:%02dm" % (_hours, _mins)
    return "%02dm:%02ds" % (_mins, _seconds)

def getFlexMasterRunConfig(rcfg, zd_iplist):
    fmrcfg = dict( user=rcfg['user'],
                   passwd=rcfg['passwd'],
                   asRoot=rcfg['asRoot'],
                   root_passwd=rcfg['root_passwd'],
                   url=rcfg['fm']['url'],
                   interval=rcfg['fm']['interval'],
                   enabled=rcfg['fm']['enabled'],
                   zd_ip_addr='', zd_ip_port='',
                   zd_ip_addr_list=zd_iplist)
    if rcfg.has_key('debug'):
        fmrcfg['debug'] = rcfg['debug']
    return fmrcfg

#
# Examples:
#
#   tea.py scaling.zd_register_to_fm cfgonly=True
#   tea.py scaling.zd_register_to_fm shutdown_all=True
#   tea.py scaling.zd_register_to_fm ratLogID=scaling fm_interval=1 fm_url=172.17.18.199
#   tea.py scaling.zd_register_to_fm ratLogID=scaling fm_interval=1 fm_rul=172.17.18.101 startup_zdvm=False 
#
def main(**kwargs):
    _dict = dict(kwargs)
    rcfg = getTestConfig(_dict)
    logging.info("[ConfigItem zd_register_to_fm]:\n%s" % pformat(rcfg, 4, 120))
    if rcfg['debug']:
        import pdb
        pdb.set_trace()

    if rcfg.has_key('cfgonly') and rcfg['cfgonly']:
        return ('PASS', 0, rcfg)

    if rcfg.has_key('shutdown_all') and rcfg['shutdown_all']:
        return shutdownAllZdvm(rcfg)

    tm0 = time.time()
    results = []
    fail_cnt = 0
    for zdvm_ip_addr, zdvm_info in rcfg['zdvm'].items():
        r_zdvm = ('PASS', {})
        if rcfg['startup_zdvm']:
            r_zdvm = ZDVM.main(ipaddr=zdvm_ip_addr,
                               based_line=rcfg['based_line'],
                               setid=zdvm_info['setid'])
            if r_zdvm[0] == 'FAIL':
                fail_cnt += 1
        fmrcfg = getFlexMasterRunConfig(rcfg, zdvm_info['zd_iplist'])
        r_fm = FM.main(**fmrcfg)
        if r_fm[0] == 'FAIL':
            fail_cnt += 1
        results.append((r_zdvm, r_fm,))
    tm1 = time.time()
    tc_elapsed_time = int(tm1 - tm0)
    verdict = 'FAIL' if fail_cnt else 'PASS'
    elapsed_time_str = secondsToString(tc_elapsed_time)
    logging.info( "[Tc.Name zd_register_to_fm] [Result %s] [Tc.elapsedTime %s(%d)] result detail:\n%s"
                % (verdict, elapsed_time_str, tc_elapsed_time, pformat(results, 4, 120)))
    return (verdict, tc_elapsed_time, results)



