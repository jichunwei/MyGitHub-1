import os
import sys
import types
from pprint import pprint

#
# setup django environment
#
def setPythonPath(rat_root_dir):
    for x in sys.path:
        if x == rat_root_dir:
            return None
    sys.path.append(rat_root_dir)

from django.core.management import setup_environ
import settings
setPythonPath(setup_environ(settings))

# import RAT models
from RuckusAutoTest.models import Testbed, TestRun, Batch
from RuckusAutoTest.testbeds import *  
from RuckusAutoTest import components

# in case forgetting to get tb instance
ratenvbag = {'tb': None}
def gettb():
    return ratenvbag['tb']

def initRatEnv(testbedname, **kwargs):
    tbconfig = {'logger_method': 'default'}
    tbconfig.update(kwargs)
    tbi = Testbed.objects.get(name = testbedname)
    
    print "InitRatEnv on [testbed %s] with [python class %s]\n" % (tbi.name, tbi.tbtype.name)
    tbi_config = tbi.config.replace('\n' , '').replace('\r', '')
    tbconfig_00 = eval(tbi_config)
    tbconfig.update(tbconfig_00)
    print "Testbed '%s' starting up with configuration:" % tbi.name
    pprint(tbconfig, indent = 4)
    testbedclass = sys.modules[__name__].__dict__[tbi.tbtype.name].__dict__[tbi.tbtype.name]
    tb = testbedclass(tbi, tbconfig)
    tb.SetDefaultConfig()
    ratenvbag['tbi'] = tbi
    ratenvbag['tb'] = tb
    return tb
   
def getTestbedClass(tbi):
    ratenvbag['tbclass'] = sys.modules[__name__].__dict__[tbi.tbtype.name].__dict__[tbi.tbtype.name]
    return ratenvbag['tbclass']

def getTestClass(test_name):
    if sys.modules['RuckusAutoTest.tests'].__dict__.has_key(test_name):
        test_module = sys.modules['RuckusAutoTest.tests'].__dict__[test_name]
        test_class = test_module.__dict__[test_name]
        return test_class
    instr = """Please enter the following command:
    from RuckusAutoTest.tests import %s""" % test_name
    raise Exception("test class name does not exist.\n%s" % (instr))

def reloadTestClass(test_name):
    if sys.modules['RuckusAutoTest.tests'].__dict__.has_key(test_name):
        test_module = sys.modules['RuckusAutoTest.tests'].__dict__[test_name]
        # actually, reload the module contains the class
        reload(test_module)
        return

    raise Exception("error!")


### ############### ###
### commom commands ###
### ############### ###
def testbedNames():
    print "The following testbed names were found in the database:"
    for tbi in Testbed.objects.all():
        print "\t%s" % tbi.name
    if not Testbed.objects.count():
        print "\t<none>\n"

def getAvailableTestRun(tb, showTestRun = 0, complete = False):
    testquery = TestRun.objects.filter(complete = complete).filter(batch__testbed = tb.testbed_info)
    if showTestRun:
        for tq in testquery: print "TRID %d: %s" % (tq.id, tq)
        print ""
    return testquery

# tq = getTestRunByBid(4, result='FAIL')
# tq.count()
def getTestRunByBid(bid, **kwargs):
    atrs = {'complete': True, 'batch__id': bid, 'result': 'ERROR'}
    atrs.update(kwargs)
    testquery = TestRun.objects.filter(**atrs)
    return testquery

def testrun_is_assign_to_testbed(tb, testrun):
    pass

### ############## ###
### run test cases ###
### ############## ###

#
# execute a testrun; class TestbedBase def TestLoop() on models.py
#
def runtest(tb):
    testquery = getAvailableTestRun(tb)
    execOneTestRun(tb, testquery)   


# run a testcase of id on testbed tb
# rTestrunID(tb, 804)
def rTestrunID(tb, id):
    testrun = TestRun.objects.get(id = id)
    # tb.testbed_info.name == testrun.batch.testbed.name
    print ""
    print "### EXEC TestRun id: %i; batch_id: %d; batch: %s" % (testrun.id, testrun.batch_id, testrun.batch)
    print "### test_name: %s; common_name: %s" % (testrun.test_name, testrun.common_name)
    print "### test_params: %s" % testrun.test_params
    if tb.testbed_info.id == testrun.batch.testbed.id:
        print ""
        tb.RunTest(testrun)
    else:
        xmsg = "### This record is not registered to run at Testbed %s, not %s"
        print xmsg % (testrun.batch.testbed.name, tb.testbed_info.name)

# rIDs(tb, 911, 917, 915)
def rIDs(tb, *testrun_id_list):
    for trid in testrun_id_list:
        rTestrunID(tb, trid)

# rOnB(tb, 9)
def rOnB(tb, batch_id):
    batch = Batch.objects.get(id = batch_id)
    # tb = Testbed.objects.get(id=batch.testbed_id) <<-- it is Testbed, not TestbedBase
    testquery = TestRun.objects.filter(batch = batch, complete = False)
    # same as
    # testquery = TestRun.objects.filter(complete=False, batch__id=batch_id)
    execOneTestRun(tb, testquery)


# rOnBk(tb, 9)
# rOnBk(tb, 9, result='FAIL')
def rOnBk(tb, batch_id, **keyword_list):
    batch = Batch.objects.get(id = batch_id)
    tq = TestRun.objects.filter(batch = batch)
    dd = {'complete': False}
    dd.update(keyword_list)
    if len(dd) > 1: del(dd['complete'])
    # the dictionary dd can have 1 or 2 items only
    tq = tq.filter(**dd)
    execOneTestRun(tb, tq)


def execOneTestRun(tb, testquery, seq = 0):
    if testquery.count():
        testrun = testquery.order_by('seq')[seq]
        print ""
        print "### EXEC TestRun id: %i; batch_id: %d; batch: %s" % (testrun.id, testrun.batch_id, testrun.batch)
        print "### test_name: %s; common_name: %s" % (testrun.test_name, testrun.common_name)
        print "### test_params: %s" % testrun.test_params
        print ""
        tb.RunTest(testrun)
    else:
        print "!!! testbed %s has no testrun record matched request." % tb


def Usage():
    u = [ "######### ATTN #########"
    , "#"
    , "# You can not run me (%s) from command line." % os.path.basename(sys.argv[0])
    , "# Maybe inside IDLE in the future."
    , "# "
    , "# You need to create the TestRun records using runrat.py first."
    , "###############################################################"
    , ""
    , "To run test cases (instances of class TestRun) following these steps:"
    , ""
    , "1. startup the python program in interative mode."
    , ""
    , "2. >>> from ratenv import *"
    , ""
    , "3. >>> tb = initRatEnv ('z01')"
    , "    # 'z01' is the testbed name when importing test suits"
    , "    # This command initiates the rat environment to execute test cases"
    , "    # assigned to testbed 'z01'"
    , "    # ATTN: the tb will initialize its environment. "
    , ""
    , "4. Display the test run records can be executed at testbed 'z01'"
    , ""
    , "  >>> testquery = getAvailableTestRun(tb, 1)"
    , "    # return all testrun's not completed; to see completed's, enter:"
    , "  >>> testquery = getAvailableTestRun(tb, 1, True)"
    , ""
    , "5. Execute test cases use any of the following commands:"
    , ""
    , "  >>> runtest(tb)"
    , "    # the first availble testrun record in order of col 'seq'"
    , "  >>> rIDs(tb, 801)"
    , "    # run testrun id 801; you can rerun a test this way "
    , "  >>> rIDs(tb, 801, 901, 300)"
    , "    # run testrun records 801, 901 then 300"
    , "  >>> rIDs(tb, *range(800,809))"
    , "    # run testrun id from 800 to 808 (not 809)"
    ]
    for x in u: print x
    print ""


if __name__ == "__main__":
    Usage()
    exit(1)


