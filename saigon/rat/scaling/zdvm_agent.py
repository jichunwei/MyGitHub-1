"""
Examples:

    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.101  zdid_list=range(0,10) cfgonly=True
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.101  zdid_list=range(0,10)
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.101  setid=1
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.101  zdid_list=range(0,10) shutdown_all=True
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.101  setid=1 shutdown_all=True

    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.102  zdid_list=range(10,20)
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.102  setid=2
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.102  zdid_list=range(10,20) shutdown_all=True
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.102  setid=2 shutdown_all=True

    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  zdid_list=range(90,100) cfgonly=True
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  setid=10
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  zdid_list=range(90,100) shutdown_all=True
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  setid=10 shutdown_all=True

    # register 512AP to ZDVM
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  zdid_list=[5121] based_line=china
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  zdid_list=(5121,) based_line=china
    tea.py scaling.zdvm_agent3 ipaddr=192.168.2.110  zdid_list=[5121] shutdown_all=True

""" 
import os
import re
import time
import logging
from RuckusAutoTest.components import LinuxPC
from RuckusAutoTest.components import FtpClient
import simplejson as json
from pprint import pprint, pformat

def getTcfg():
    tcfg = dict(ipaddr='192.168.2.101',
                based_line='odessa',
                zdid_list = range(0,10),
                cfgonly=False,
                user='zdvm',
                passwd='tdcitms',
                asRoot=False,
                root_passwd='!v54!scale',
                debug=False,
                init=False,
                prompt=r"([^@]+)@([^:]+):\s*(~|[^#$]+)[#$] ",
                rs_fname='result.txt',
                shutdown_first=True,
                work_dir='/vmware')
    tcfg['zdid_list'] = range(0,10)
    return tcfg

try:
    if not tcfg.has_key('zdvm'):
        tcfg = getTcfg()
except:
    tcfg = getTcfg()

def touchTcfgWith(_dict):
    tcfg.update(_dict)
    if tcfg.has_key('setid'):
        zd0 = int(tcfg['setid'])
        zd1 = zd0 * 10
        zd0 = (zd0-1) * 10
        tcfg['zdid_list'] = range(zd0,zd1)
    tcfg['target_zd_list'] = getTargetZdidList(tcfg['zdid_list'])
    logging.info("[InitConfig Agent.ZDVM]:\n%s" % (pformat(tcfg, 4, 120)))

def connectTE():
    logging.info('[ConnectTo Agent.ZDVM] with [ipAddr %s] [user %s] [psw %s] [rpsw %s]' \
        % (tcfg['ipaddr'], tcfg['user'], tcfg['passwd'], tcfg['root_passwd']))
    zdvm = LinuxPC.LinuxPC(tcfg)
    zdvm.initialize(dologin=False)
    # LinuxPC login as Root only it detects specific prompt; we do it in our function
    zdvm.login(asRoot=False)
    zdvm.loginAsRoot()
    zdvm.doCmd('cd /vmware')
    print zdvm.doCmd('pwd', 30)
    tcfg['zdvm'] = zdvm
    return zdvm

def getTargetZdidList(zdid_list):
    if type(zdid_list) is list:
        zdstr = ""
        for zd in zdid_list:
            # zdid to ZDVM workstation has base of 1; our input's base is 0; so add 1
            zdstr += str(zd+1) + " "
        return zdstr.strip()
    return zdid_list

def startupZDVM(zdvm=None):
    zdvm = tcfg['zdvm'] if not zdvm else zdvm
    if not tcfg.has_key('target_zd_list'):
        tcfg['target_zd_list'] = getTargetZdidList(tcfg['zdid_list'])
    based_line=tcfg['based_line']
    target_zd_list = tcfg['target_zd_list']
    j_rs_fname, shutdown_first = tcfg['rs_fname'], tcfg['shutdown_first']
    nZD = len(target_zd_list.split())
    if shutdown_first:
        logging.info('[Shutdown zdvm] [zdvmHost %s] [target_zd_list %s]' % (tcfg['ipaddr'], target_zd_list))
        data = zdvm.doCmd('./stopzd.sh %s' % target_zd_list)
        print data
    logging.info('[RemoveResultFile %s]' % (j_rs_fname))
    data = zdvm.doCmd('rm -f %s' % j_rs_fname)
    print data
    logging.info("[StartupNumOfZDVM %s] please wait for completion." % nZD)
    data = zdvm.doCmd('./startzd.sh 300 %s %s | tee autotest_result.log ' % (based_line, target_zd_list))
    print data
    return (nZD, data)

def shutdownAllZdvm(zdvm=None):
    zdvm = tcfg['zdvm'] if not zdvm else zdvm
    if not tcfg.has_key('target_zd_list'):
        tcfg['target_zd_list'] = getTargetZdidList(tcfg['zdid_list'])
    target_zd_list = tcfg['target_zd_list']
    nZD = len(target_zd_list.split())
    logging.info('[Shutdown zdvm] [zdvmHost %s] [target_zd_list %s]' % (tcfg['ipaddr'], target_zd_list))
    data = zdvm.doCmd('./stopzd.sh %s' % target_zd_list)
    print data
    return (nZD, target_zd_list)

def getJsonResult():
    pass

def getResult(zdvm=None):
    zdvm = tcfg['zdvm'] if not zdvm else zdvm
    j_rs_fname, debug = tcfg['rs_fname'], tcfg['debug']
    _haltProcess(debug)
    cPrompt = zdvm.doCmd('').lstrip()
    jdata = zdvm.doCmd('cat %s' % j_rs_fname, 60)
    sPattern = r'[^\{]*(\{.*\})\s*%s' % cPrompt
    m = re.search(sPattern, jdata, re.I)
    if m:
        jdata = m.group(1)
    else:
        _haltProcess(True)
        logging.info("[INTERNAL ERROR] Unable to get JSON data string from results:\n[Pattern %s]\nData: %s" % (sPattern, jdata))
    return jdata

def showPassFail(json_str, expected_pass, presult=1, debug=False):
    _haltProcess(debug)
    jdict = json.loads(json_str)
    if presult:
        logging.info("[NumOfZDVM %s] JsonResult:\n%s" % (str(expected_pass), pformat(jdict, 4, 120)))
    if jdict.has_key('TestSummary'):
        if jdict['TestSummary']['TotalSuccess'] == expected_pass:
            return 'PASS'
    return 'FAIL'

def disconnectTE():
    try:
        logging.info("[DisconnectFrom Agent.ZDVM]")
        tcfg['zdvm'].close()
        del tcfg['zdvm']
    except Exception, e:
        print "** ERROR ** Cannot close ZDVM Server:\n%s" % e.message

def _haltProcess(debug):
    if debug:
        import pdb
        pdb.set_trace()

def main(**kwargs):
    if kwargs.has_key('debug'):
        _haltProcess(kwargs['debug'])
    touchTcfgWith(kwargs)
    if tcfg.has_key('cfgonly') and tcfg['cfgonly']:
        return ('PASS', tcfg)
    zdvm = connectTE()
    if kwargs.has_key('shutdown_all') and kwargs['shutdown_all']:
        (nZD, data) = shutdownAllZdvm()
        disconnectTE()
        return ('PASS', nZD)

    (nZD, data) = startupZDVM()
    jdata = getResult()
    result = showPassFail(jdata, nZD)
    disconnectTE()
    print "\nThis test creates %s ZDs. Test Result is %s" % (nZD, result)
    return (result, nZD)

def Usage():
    pass

if __name__ == "__main__":
    from RuckusAutoTest.common.lib_KwList import *
    _dict = dict(num_ap=10)
    _dict.update(as_dict(sys.argv[1:]))
    main(**_dict)


