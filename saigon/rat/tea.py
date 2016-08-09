""" Test Execution Agent:
    A test runner executes a python module that has a main() function
    with kwargs as its only input.

Usage:

    tea.py <module name> [[<key]<=[<value>]] ...]

    where:
        <module name>: a python module file under rat directory.
        <key>: any word that main() of <module name> will accept,
               except te_root, rat_log_id and idebug

        te_root: directory contains <module name> file, default is 'te'
                 if <module name> contains directory name; te_root is ignored.
                 For example: scaling.zdvm_agent
        rat_log_id: Identifier for logging facility
        idebug: step into debug mode when tea.py is launched.

Interactive Examples:

    import tea
    dmk = tea.load_te_module('scaling.dimark_agent')
    dmk.main(dict(debug=True, dm_num_ap=5, initenv=True))
    dmk.main(dict(initenv=True))

CLI examples:

    tea.py zdvm_agent te_root=scaling  ipaddr=172.17.18.122  zdid_list=range(11,21)
    tea.py flexmaster url=172.17.18.101 zd_ip_addr=172.17.18.122 zd_ip_port=range(1011,1021)
    tea.py zdvm_agent te_root=scaling  ipaddr=172.17.18.123  zdid_list=range(21,31)
    tea.py flexmaster url=172.17.18.101 zd_ip_addr=172.17.18.123 zd_ip_port=range(1021,1031)

    tea.py scaling.zd_register_to_fm fm_interval=10
    tea.py scaling.zd_register_to_fm startup_zdvm=False zdid_first=5 zdid_last=6

"""
import sys
import logging
import inspect
import traceback
import pdb
from pprint import pprint, pformat

import ratenv
from RuckusAutoTest.common import lib_KwList as kwlist
from RatLogger import RatLogger

MYNAME = inspect.currentframe().f_code.co_filename


# return module instance
def load_te_module(te_module_name, fromlist = [''], te_root = 'te'):
    if te_module_name.find('.') > 0:
        te_module_path = te_module_name
    elif te_root:
        te_module_path = '%s.%s' % (te_root, te_module_name)
    else:
        te_module_path = te_module_name

    te_module = __import__(te_module_path, fromlist = fromlist)

    return te_module


def main(te_module_name, **kwargs):
    tcfg = dict(idebug = False, rat_log_id = 'tea')
    tcfg.update(kwargs)

    rat_log_id = tcfg['rat_log_id']
    del(tcfg['rat_log_id'])

    if tcfg['idebug']:
        pdb.set_trace()

    del(tcfg['idebug'])

    if tcfg.has_key('te_root'):
        te_root = tcfg['te_root']
        te_module = load_te_module(te_module_name, te_root = te_root)
        del tcfg['te_root']

    elif te_module_name.find('.') > 0:
        te_module = load_te_module(te_module_name, te_root = '')

    else:
        te_module = load_te_module(te_module_name)

    if not hasattr(te_module, 'main'):
        raise Exception('Expected main function in TE module %s' % (te_module_name))

    RatLogger.init_logger(rat_log_id + '_' + te_module_name)

    logging.info("[TEA.Module %s] tcfg:\n%s" % (te_module_name, pformat(tcfg, 4, 120)))

    test_result_tuple = te_module.main(**tcfg)

    logging.info("[TEA.Module %s] Result:\n%s" % (te_module_name, pformat(test_result_tuple, 4, 120)))

    RatLogger.close_logger()

    return test_result_tuple


def usage_02():
    from string import Template
    print Template("""
Usage: ${MYNAME} <module name> [[<key]<=[<value>]] ...]

    where:
        <module name>: a python module file under rat directory.
        <key>: any word that <module name> will accept, except te_root and idebug

        te_root: directory the <module name> resident, default is te
                 if <module name> contains directory name; te_root is ignored.
                 For example: scaling.zdvm_agent
        rat_log_id: Identifier for logging facility
        idebug: step into debug mode when tea.py is launched.

Examples:

   ${MYNAME} zdvm_agent te_root=scaling  ipaddr=172.17.18.122  zdid_list=range(11,21)
   ${MYNAME} flexmaster url=172.17.18.101 zd_ip_addr=172.17.18.122 zd_ip_port=range(1011,1021)
   ${MYNAME} zdvm_agent te_root=scaling  ipaddr=172.17.18.123  zdid_list=range(21,31)
   ${MYNAME} flexmaster url=172.17.18.101 zd_ip_addr=172.17.18.123 zd_ip_port=range(1021,1031)
   ${MYNAME} scaling.zd_register_to_fm zdvm_startup=False zdid_first=3 zdid_last=4

""").substitute(dict(MYNAME = MYNAME))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        usage_02()
        exit(1)

    te_module_name = sys.argv[1]
    kwdict = kwlist.as_dict(sys.argv[2:])

    try:
        test_result_tuple = main(te_module_name, **kwdict)
        try:
            print "[TEA.TESTRESULT %s]" % (test_result_tuple[0])
        except:
            pass

    except Exception, e:
        print "\n\n%s" % ('!' * 68)
        ex = traceback.format_exc()
        print ex
        exit(1)

    exit(0)

