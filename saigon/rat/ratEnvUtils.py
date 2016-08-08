#!/usr/local/bin/python

import os, sys

#
# setup django environment
#
from django.core.management import setup_environ
import settings
setup_environ(settings)

# import RAT models
from RuckusAutoTest.models    import *
from RuckusAutoTest.testbeds  import *
from RuckusAutoTest.tests      import *
from RuckusAutoTest.components import *

# in case forgetting to get tb instance
ratenvbag = {'tb': None}
def gettb():
    return ratenvbag['tb']

def initRatEnv(testbedname):
    tbi = Testbed.objects.get(name=testbedname)
    print "Running testbed %s (python class %s)\n" % (tbi.name, tbi.tbtype.name)
    tbconfig = eval(tbi.config)
    testbedclass = sys.modules[__name__].__dict__[tbi.tbtype.name].__dict__[tbi.tbtype.name]
    tb = testbedclass(tbi, tbconfig)
    tb.SetDefaultConfig()
    ratenvbag['tbi'] = tbi
    ratenvbag['tb'] = tb
    return tb

def get_testbed_class(tbi):
    ratenvbag['tbclass'] = sys.modules[__name__].__dict__[tbi.tbtype.name].__dict__[tbi.tbtype.name]
    return ratenvbag['tbclass']

### ############### ###
### commom commands ###
### ############### ###
def testbedNames():
    print "The following testbed names were found in the database:"
    for tbi in Testbed.objects.all():
        print "\t%s" % tbi.name
    if not Testbed.objects.count():
        print "\t<none>\n"

def getAvailableTestRun(tb, showTestRun=0, complete=False):
    testquery = TestRun.objects.filter(complete=complete).filter(batch__testbed=tb.testbed_info)
    if showTestRun:
        for tq in testquery: print "TRID %d: %s" % (tq.id, tq)
        print ""
    return testquery

# tq = getTestRunByBid(4, result='FAIL')
# tq.count()
def getTestRunByBid(bid, **kwargs):
    atrs = {'complete': True, 'batch__id': bid,'result': 'ERROR'}
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
    testrun = TestRun.objects.get(id=id)
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
    batch = Batch.objects.get(id=batch_id)
    # tb = Testbed.objects.get(id=batch.testbed_id) <<-- it is Testbed, not TestbedBase
    testquery = TestRun.objects.filter(batch=batch, complete=False)
    # same as
    # testquery = TestRun.objects.filter(complete=False, batch__id=batch_id)
    execOneTestRun(tb, testquery)


# rOnBk(tb, 9)
# rOnBk(tb, 9, result='FAIL')
def rOnBk(tb, batch_id, **keyword_list):
    batch = Batch.objects.get(id=batch_id)
    tq = TestRun.objects.filter(batch=batch)
    dd = {'complete': False}
    dd.update(keyword_list)
    if len(dd) > 1: del(dd['complete'])
    # the dictionary dd can have 1 or 2 items only
    tq = tq.filter(**dd)
    execOneTestRun(tb, tq)


def execOneTestRun(tb, testquery, seq=0):
    if testquery.count():
        testrun = testquery.order_by('order')[seq]
        print ""
        print "### EXEC TestRun id: %i; batch_id: %d; batch: %s" % (testrun.id, testrun.batch_id, testrun.batch)
        print "### test_name: %s; common_name: %s" % (testrun.test_name, testrun.common_name)
        print "### test_params: %s" % testrun.test_params
        print ""
        tb.RunTest(testrun)
    else:
        print "!!! testbed %s has no testrun record matched request." % tb

def getBatchList(tb_name=""):
    """
    - tb_name: if tb_name <> "", the function will list all batch in database
    """
    batch_list = Batch.objects.all()
    if tb_name == "":
        print "Batch list for all testbed in Database"
    else:

        print "Batch list \'%s\' testbed" % tb_name
    return batch_list

def loadBatch(batch_id):
    """
    This function will help to load testsuites from a batch to Test Run
    - batch_id: batch ID in database
    *** Note ***: batch_id can be get by call getBatchList
    """
    batch = Batch.objects.get(id = batch_id)
    count = 0
    print "Enqueue Batch: %s (ID# %d)" % (batch, batch.id)
    batch.start_time=datetime.datetime.now()
    batch.save()
    for suite in batch.suites.all():
        print "\t Suite: %s" % suite
        tclist = TestCase.objects.filter(suite=suite)
        for tc in tclist:
            print "\t\t TestCase: %s" % tc
            TestRun(batch=batch,
                    test_name=tc.test_name,
                    test_params=tc.test_params,
                    config=suite.config,
                    complete=False,
                    common_name=tc.common_name,
                    order=count).save()
            count += 1
    logging.info("Queued %d TestRuns" % count)

def loadTest(tb_name, build_stream):
    """
    Create Autotest Config for a build stream for all testsuite available in testsuite list
    """
    # Create AutoTest Config
    bs_list = BuildStream.objects.all()
    for bs in bs_list:
        if bs.name == build_stream:
            at = AutotestConfig(testbed=Testbed.objects.get(name=tb_name),
                            build_stream = BuildStream.objects.get(name=bs.name),
                            lastbuildnum = 1, order=1)
            at.save()
            for ts in TestSuite.objects.all():
                at.suites.add(ts)
            at.save()
            break

    # Create Batch from AutoTest Config
    configs = AutotestConfig.objects.filter(testbed=Testbed.objects.get(name=tb_name))
    for config in configs:
        for build in Build.objects.filter(build_stream = config.build_stream):
            batch = Batch(testbed=config.testbed,
                          build= build,
                          order=0,
                          timestamp=datetime.datetime.now(),
                          result_email="",
                          complete=False)
            batch.save()
            batch.suites = config.suites.all()
            batch.save()
            logging.info("Scheduled Batch: %s: %s" % (build, batch.suite_list()))

    count = 0
    print "Enqueue Batch: %s (ID# %d)" % (batch, batch.id)
    batch.start_time=datetime.datetime.now()
    batch.save()
    for suite in batch.suites.all():
        print "\t Suite: %s" % suite
        tclist = TestCase.objects.filter(suite=suite)
        for tc in tclist:
            print "\t\t TestCase: %s" % tc
            TestRun(batch=batch,
                    test_name=tc.test_name,
                    test_params=tc.test_params,
                    config=suite.config,
                    complete=False,
                    common_name=tc.common_name,
                    order=count).save()
            count += 1
    logging.info("Queued %d TestRuns" % count)

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
    , "    # the first availble testrun record in order of col 'order'"
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
    if len(sys.argv) >1:
       tb_name = sys.argv[1]
    else:
       tb_name = raw_input("Testbed Name: ")
    if tb_name == "":
        sys.exit(1)
    tb = initRatEnv(tb_name)

    # Load TCs to run test
    if not getBatchList(tb_name):
        loadTest(tb_name, "Null")

    cont = True
    while cont:
        print "\033[0;35m[ Run Option ]\033[m"
        print "\033[0;35m1 - runtest(tb)                     # the first available testrun record in order of the col 'order'\033[m"
        print "\033[0;35m2 - rIDs(tb, TC_ID)                 # run testrun TC_ID; you can rerun a test this way\033[m"
        print "\033[0;35m3 - rIDs(tb, *tc_id_list)            # run testrun with multiple TC_IDs\033[m"
        print "\033[0;35m4 - Quit the debug\033[m"
        option = raw_input("\033[0;32mYour choice? \033[m")
        if option == "1":
            runtest(tb)
        elif option == "2":
            tc_id = raw_input("Testrun ID: ")
            rIDs(tb,int(tc_id))
        elif option == "3":
	    tc_list = []
	    tc_id = raw_input("Choose individual TC_IDs (Enter if not choose): ")
	    if tc_id:
		tc_list = [id.strip() for id in tc_id.split(',')]
            tc_range = raw_input("Choose range of TC_IDs (start,end) (Enter if not choose): ")
	    if tc_range:
		tc_list = tc_list + range(int(tc_range.split(',')[0]), int(tc_range.split(',')[1]))
	    print tc_list
	    rIDs(tb,*tc_list)
        elif option == "4":
            cont = False
        else:
            print "Invalid option!!! Please try again."
