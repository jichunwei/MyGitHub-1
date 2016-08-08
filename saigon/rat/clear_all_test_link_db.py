'''
Created on 2011-4-28
@author: lab
'''
from ratenv import *
from Testlink import models as TLM

def del_project_test_cases():
    tcs = TLM.ProjectTestCase.objects.all()
    for tc in tcs:
        tc.delete()


def del_builds():
    bs = TLM.TestBuild.objects.all()
    for x in bs:
        x.delete()


def del_test_plans():
    tps = TLM.TestPlan.objects.all()
    for x in tps:
        x.delete()

if __name__ == "__main__":
    do = True
    if do:
        del_project_test_cases()
        del_builds()
        del_test_plans()
        print 'DONE'
    else:
        print 'please check do param'
    
                          
