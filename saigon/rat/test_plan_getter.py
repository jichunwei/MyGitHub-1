'''
Created on 2012-6-19
@author: cwang
'''

from ratenv import *
from RuckusAutoTest.models import TestPlan

from tlc22 import TestlinkClient22


def set(_plans):
    for plan in _plans:
        name = plan['name']
        notes = plan['notes']
        objs = TestPlan.objects.filter(name=name)
        if not objs:
            tp = TestPlan()
            tp.name = name
            tp.notes = notes
            tp.save()
            print 'Add Test Plan %s' % name
        else:
            obj = objs[0]
            obj.notes = notes
            obj.save()
            print 'Update Test Plan %s' % name
    
    print 'DONE'

def get():
    _cfg = {
        'server_url': 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php',
        'dev_key': '014ea04869a6bd4faa691dbab7589891',
        'project': 'Zone Director',        
    }
    tlc = TestlinkClient22.tlc22(devKey=_cfg['dev_key'], 
                                 server_url= _cfg['server_url'])
    _plans = tlc.get_plans_by_project_name(_cfg['project'])
    return _plans


if __name__ == '__main__':
    set(get())    