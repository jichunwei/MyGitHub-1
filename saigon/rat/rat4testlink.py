'''
action=update project="Zone Director" plan="Toronto 9.1 Automation" \
    server_url="http://qa-poke.video54.local/testlink/lib/api22/xmlrpc.php" \
    dev_key="RAT-Testlink-DevKey-38"

action=associate testbed="odessa.sys" build="9.1.0.0.17" \
    server_url="http://qa-poke.video54.local/testlink/lib/api22/xmlrpc.php" \
    dev_key="RAT-Testlink-DevKey-38"

action=report project="Zone Director" plan="Toronto 9.1 Automation" build="9.1.0.0.9" \
    server_url="http://qa-poke.video54.local/testlink/lib/api22/xmlrpc.php" \
    dev_key="RAT-Testlink-DevKey-38"
'''

import sys
import pros4testlink as settings

if not settings.TESTLINK_CLIENT_PATH in sys.path:
    sys.path.append(settings.TESTLINK_CLIENT_PATH)

import db_env

import update_test_db
import map_test_run
from tlc22.TestlinkClient22 import TestlinkClient22
from TLReportMgr import TLReportMgr


def _upd(cfg):
    '''
    '''
    update_test_db.update_test_db(
        cfg['tlc'], cfg['project'], cfg['plan']
    )


def _assoc(cfg):
    '''
    '''
    map_test_run.main(**cfg)


def _rpt(cfg):
    '''
    '''
    project_id = cfg['tlc'].get_project_by_name(cfg['project'])[0]['id']
    builds = cfg['tlc'].get_builds_by_plan_name(cfg['project'], cfg['plan'])
    for b in builds:
        if b['name'] == cfg['build']:
            build_id = b['id']
            plan_id = b['testplan_id']
            break

    rm = TLReportMgr(cfg['tlc'], project_id, plan_id, build_id)

    rm.main()


def do_action(cfg):
    return {
        'update' : _upd,
        'associate' : _assoc,
        'report' : _rpt,
    }[cfg['action']](cfg)



if __name__ == '__main__':
    '''
    '''
    cfg = {
        'server_url': 'http://qa-poke.video54.local/testlink/lib/api22/xmlrpc.php',
        'dev_key': 'RAT-Testlink-DevKey-38',
        'project': 'Zone Director',
        'plan': 'Toronto 9.1 Automation',
        'build': '9.1.0.0.9',
    }
    from RuckusAutoTest.common import lib_KwList as kwlist
    _cfg = kwlist.as_dict(sys.argv[1:])

    if not _cfg.has_key('action'):
        raise Exception('please provide your action ["update", "associate", "report"]')

    elif not _cfg['action']:
        raise Exception("action's value is empty")

    cfg.update({
        'server_url': settings.SERVER_URL,
        'dev_key': settings.DEV_KEY,
        'project': settings.PROJECT,
        'plan': settings.PLAN,
        'build': settings.BUILD,
    })

    cfg.update(_cfg)

    tlc = TestlinkClient22(cfg['dev_key'], cfg['server_url'])
    cfg.update({'tlc': tlc})

    do_action(cfg)

