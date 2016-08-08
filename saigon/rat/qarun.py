"""
This program reflects what QA regression do:

    Every week or two, release captain will request automation team to execute
    targeted release's buildStream [example: ZD3000_8.2.0.0_production]
    with specific build no [example: 277].

    This request to automation is interpreted as:

        QA Run build-stream on-Logical-Testbed with-build-no

    Which in reality for a specific release [say Reading/8.2] can be:

        qarun.py ZD3000_8.2.0.0_production netanya.sys bno=277
        qarun.py ZD3000_8.2.0.0_production mesh.specific bno=277
        qarun.py ZD3000_8.2.0.0_production mesh.fanout.chowchow.dualband bno=277
        qarun.py ZD3000_8.2.0.0_production mesh.fanout.dialmatian.dualband bno=277 [alternate with chowchow]
        qarun.py ZD3000_8.2.0.0_production l3.mesh.fanout bno=277
        qarun.py ZD3000_8.2.0.0_production odessa.sys bno=277
        qarun.py ZD3000_8.2.0.0_production wispr.app bno=277

qarun regression test execution flow:
    1) find the AutotestConfig record using testbed_name and build_stream.
    2) if build_no given in the command line, change AutotestConfig lastbuildnumber, save it.
    3) is AutotestConfig's batch record exist?
    4) if not, call build_stream.CheckNewBuilds(), it creates builds by asking K2.
    5) is AutotestConfig's TestRun records exist?
    6) if not, create them
    7) step through TestRun records, and execute them
    7.1) First pass; only the testrun record not completed yet
    7.2) Second pass; all records not marked as PASS;
    7.3) repeat "2nd pass" until all PASS, or each test executed not more than env(RAT_MAX_RUNPASS)

qarun combo test execution flow:

"""
import os
import logging
import traceback
import datetime
import re
import time
from pprint import pformat

import ratenv
from RuckusAutoTest.models import TestCase, Testbed, TestRun, Batch, Build, BuildStream, AutotestConfig
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zdcli import process_mgr
from RuckusAutoTest.components import clean_up_rat_env
from contrib.download import image_helper as ih
from RatLogger import RatLogger

def logging_info(imsg, toconsole = False):
    if tinf['tb']:
        logging.info(imsg)
        if toconsole:
            print "[INFO] %s" % imsg
    else:
        print "[INFO] %s" % imsg

#
# Get build_stream and its build numbers and create their information in the batch records.
# Each batch record has information of how to get its software build
#
def checkBuildsOnWebSite(build_stream, build_no, version):
    build_stream.CheckNewBuilds_V2(build_stream, build_no, version)
    
def checkBuild(buildstream, build_no):
    try:
        build = Build.objects.filter(build_stream=buildstream, number=build_no)
        if build :
            return True
        else :
            return False      
    except Exception, e:
        raise e
    
def addLocalBuildsInfo(buildstream, build_no):
    prefix = buildstream.name.split('_')[1]
    version = str(prefix) + '.' + str(build_no)
    Build(build_stream=buildstream,
          number=int(build_no),
          builder='',
          version=version,
          label="lnxbuild_ap_%s_p4build2_info_%s_%s" % (buildstream.name.split('_')[0], 
                                                            time.strftime("%Y%m%d", time.localtime()),
                                                            str(version)),
          timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
          URL='http://192.168.0.253').save()
    logging.info("Insert a local build into database. Likely a demo build.")
def checkBuildsOnK2(build_stream):
    build_stream.CheckNewBuilds()

def getTestBuildInfo(build_stream, build_no):
    try:
        build = Build.objects.get(build_stream=build_stream, number=build_no)
    except:
        logging.info("Checking 'Lhotse' or 'Yangming' WebSite, Requested build not found: (%s, %s)" % (build_stream.name, build_no))
        version = str(build_stream.name.split('_')[1]) + '.' + str(build_no)
        checkBuildsOnWebSite(build_stream, build_no, version) #phannt added
        if not checkBuild(build_stream, build_no):
            addLocalBuildsInfo(build_stream, build_no)
        try:
            build = Build.objects.get(build_stream=build_stream, number=build_no)
        except:
            raise Exception("Build no(%s) of stream(%s) does not exist." % (str(build_no), str(build_stream)))
    return build

# create batch which hold the information of how to get software's build
# then create batch's testrun records from TestSuites and their test cases
def makeTargetBatchTestcases(testbed_info, build, suitelist, DUT = 0, email = '', priority = 0, cr_testcases = True):
    """
    Add a new batch to the queue with the specified parameters.
    """
    batchlist = Batch.objects.filter(testbed = testbed_info, build = build)
    if len(batchlist) > 0:
        batch = batchlist[0]
        logging.info("Batch [%s] exists." % str(batch))
        trunlist = TestRun.objects.filter(batch = batch)
        if len(trunlist) < 1 or tinf['rebuildbatch']:
            logging.info("Rebuild [Batch %s]." % str(batch))
            createTargetTestrun(build, batch, suitelist)
    else:
        email = email if email else testbed_info.resultdist
        batch = Batch(testbed = testbed_info,
            build = build,
            seq = priority,
            timestamp = datetime.datetime.now(),
            result_email = email,
            complete = False,
            DUT = DUT)
        batch.save()
        createTargetTestrun(build, batch, suitelist)
    return batch

# Example:
#
#   createTargetTestrun(build, batch, autotest.suites)
#
def createTargetTestrun(build, batch, suitelist):
    # create batch's TestSuite; by definition it is copied from AutotestConfig
    batch.suites = suitelist.all()
    batch.save()
    logging.info("Scheduled Batch #%d %s: %s" % (batch.id, build, batch.suite_list()))
    buildTestrunRecords(batch)

# Original work is method EnqueueTestsForNextBatch() of class TestbedBase
def buildTestrunRecords(batch, init_ord = 0):
    count = init_ord
    logging.info("Enqueue Batch: %s (ID# %d)" % (batch, batch.id))
    if batch.start_time:
        logging.info('Batch %s (ID# %d) was created at %s' % (batch, batch.id, str(batch.start_time)))
    else:
        batch.start_time = datetime.datetime.now()
        batch.save()
    logging.info("From suites: %s" % batch.suites.all())
    xtcinfo_fmt = "Existed TestRun: ID(#%d) BID(#%d) test_name(%s) common_name(%s) seq(%s) id(%s)"
    ntcinfo_fmt = "TestCase(#%d) as TestRun: [ID #%d/%d/%d] test_name(%s) common_name(%s)"
    count_add = 0
    count_exp = 0
    for suite in batch.suites.all():
        logging.info("Creating Suite: %s" % suite)
        tclist = TestCase.objects.filter(suite = suite)
        for tc in tclist:
            trunlist = TestRun.objects.filter(batch = batch, suite = suite,
                                              test_name = tc.test_name, common_name = tc.common_name)
            if len(trunlist) > 0:
                trun = trunlist[0]
                ordlist, idlist = testrunRecordInfo(trunlist)
                if tinf['displevel'] > 0:
                    logging.info(xtcinfo_fmt % (trun.id, batch.id, tc.test_name, tc.common_name, ordlist, idlist))
                    print ""
            elif not tc.enabled:
                logging.info("[TestRun.v2 SKIP]: %s" % tc)
            else:
                logging.info("[TestRun.v2 ADD]: %s" % tc)
                trun = TestRun(batch = batch,
                    suite = suite,
                    test_name = tc.test_name,
                    test_params = tc.test_params,
                    complete = False,
                    common_name = tc.common_name,
                    seq = tc.seq,
                    exc_level = tc.exc_level,
                    is_cleanup = tc.is_cleanup)
                count_add += saveTestRunRecord(trun)
                count += 1
                count_exp += 1
                logging.info(ntcinfo_fmt % (tc.id, batch.id, suite.id, trun.id, tc.test_name, tc.common_name))
                print ""
    logging.info("Queued %d TestRuns for batch [%s]" % (count, batch))
    # SANITY CHECK: sqlite3 said it failed; but it was saved
    tr_total = TestRun.objects.filter(batch = batch).count()
    if count_exp == tr_total:
        if len(tinf['db_testrun_errorlist']) > 0:
            tinf['db_testrun_errorlist'] = {}
            tinf['db_testrun_errorlist'][0] = "DB TestRun records: expect: %s;  created: %s; added_OK: %s" % \
                       (str(count_exp), str(tr_total), str(count_add))
    else:
        logging.info("[DB WARNING] %d TestRun records created for batch %s; expect %d" % (tr_total, batch, count_add))
    if tr_total > 0:
        batch.total_tests = "%s created. %s expected." % (str(tr_total), str(count_add))
        batch.save()
    else:
        logging.info("Empty batch complete")
        batch.complete = True
        batch.end_time = datetime.datetime.now()
        batch.save()

def saveTestRunRecord(trun):
    try:
        trun.save()
        return 1
    except Exception, e0:
        time.sleep(0.5)
        try:
            trun.save()
            logging.info('[DB WARNING] On creating TestRun record id %d :: %s [%s]' % (trun.id, trun, e0.message))
            return 1
        except Exception, e1:
            tinf['ishould']['abort'] = True
            logging.info('[DB ERROR] Unable to create TestRun record id %d :: %s [%s]' % (trun.id, trun, e1.message))
            ex = traceback.format_exc()
            logging.info('[DB ERROR] %s' % ex)
            tinf['db_testrun_errorlist'][trun.seq] = trun
            return 0

def testrunRecordInfo(trunlist):
    idlist = []
    ordlist = []
    for x in trunlist:
        idlist.append(x.id)
        ordlist.append(x.seq)
    return (str(ordlist), str(idlist))


# TODO: sometime the page load timeout. Solution?
def upgradeSoftwareBuild(testbed = None, batch = None):
    # no upgrade checking; just do the testing
    if not tinf['ishould']['chkv']: return ''
    if not testbed: testbed = tinf['tb']
    if not batch: batch = tinf['batch']
    zd_version = ih.server_url_map['cur_build']

    if ih.server_url_map['base_build'] == zd_version:
        logging.info("ZoneDirector has build version %s; no upgrade required" % zd_version)
        #Jacky.Luh update by 2012-06-26
        prepare_tb_config_to_ready(zd_version, batch)
        return None

    logging.info("ZoneDirector has build version %s. Upgrade to build version %s" % (zd_version, batch.build.version))
    #resetBatchLogfile(batch)
    # no need to reset or init logger
    # RatLogger.init_logger(batch.testbed.name)
    # start new batch: upgrade DUT SW, Verify Testbed, Restore Default Config
    # if Testbed fails to verify and restore config, need manual intervention
    if batch.DUT: # override DUT if DUT is specified at batch level
        testbed.dut = testbed.components[batch.DUT.name]
    
    #if the current zd's build is diffrent with batch's build, 
    #and testbed mesh enabled, need enable the switch port of mesh ap.
    cur_batch_ver = re.findall(r'(.*)\.\d', batch.build.version)
    cur_zd_ver = re.findall(r'(.*)\.\d', zd_version)   
        
    # if upgrade failed, let operator know
    #Jacky.Luh update by 2012-06-26
    upgrade_id, factory_id, list_of_connected_aps = testbed.UpgradeDUT(batch.build)
    try:
        testbed.verify_testbed(upgrade_id)
    except Exception, e:
        raise Exception("New build %s broke testbed sanity because %s" % (batch.build, e.message))
    #Jacky.Luh update by 2012-06-26
    try:
        prepare_tb_config_to_ready(zd_version, batch, factory_id)
    except Exception, e:
        raise Exception("New build %s failed to set default config because %s" % (batch.build, e.message))
    

 #Jacky.Luh update by 2012-06-26
def prepare_tb_config_to_ready(zd_version, batch, factory_id = False):
    zd = tinf['tb'].components['ZoneDirector']
    tb_enabled_mesh = tinf['tb'].config['mesh_enabled']
    cur_batch_ver = re.findall(r'(.*)\.\d', batch.build.version)
    cur_zd_ver = re.findall(r'(.*)\.\d', zd_version)
    base_build_version = re.findall(r'^(.*)\.{1}\d', batch.build.version)[0]
    zd_enabled_mesh = zd.verify_mesh_enable()
    list_of_connected_aps = list()
    tb_all_aps_info = tinf['tb'].config['ap_mac_list']
    ap_upgrade_timeout = 1400
    ap_upgrade_start_time = time.time()

    for joined_ap in tb_all_aps_info:
        logging.info("Waiting the ap[%s] join in zd" % joined_ap)
        while(True):
            status = None
            sym_ap_status = None
            if (time.time() -ap_upgrade_start_time) > ap_upgrade_timeout:
                raise Exception("Error: AP upgrading failed. Timeout")
            zd.click_mon_apsummary_refresh()
            ap_info = zd._get_ap_info(joined_ap)
            status =ap_info['status']
            zd.click_mon_apsummary_refresh()
            for sym_ap in tinf['tb'].config['ap_sym_dict'].keys():                
                if joined_ap == tinf['tb'].config['ap_sym_dict'][sym_ap]['mac']:
                    sym_ap_status = tinf['tb'].config['ap_sym_dict'][sym_ap]['status']
                    if ' (' in status and ' (' in sym_ap_status:
                        if status.lower() == sym_ap_status.lower():
                            logging.info("The ap[%s] join in zd" % joined_ap)
                            list_of_connected_aps.append(ap_info)
                            break
                    else:
                        if status.lower().startswith(u"connected"):
                            logging.info("The ap[%s] join in zd" % joined_ap)
                            list_of_connected_aps.append(ap_info)
                            break                             
            
            if status.lower().startswith(u"connected"):
                break
    
    #if no any ap info, throw the exception of "no ap join in zd"       
    if len(list_of_connected_aps) == 0:
        raise Exception("No AP connected")
    
    #check tb config is ready or not.
    check_tb_expect_statement_ready(zd_enabled_mesh, 
                                    tb_enabled_mesh, 
                                    factory_id, 
                                    list_of_connected_aps, 
                                    base_build_version)
      
     
#Jacky.Luh update by 2012-06-26     
def check_tb_expect_statement_ready(zd_enabled_mesh, 
                                    tb_enabled_mesh, 
                                    factory_id, 
                                    list_of_connected_aps, 
                                    base_build_version):
    zd = tinf['tb'].components['ZoneDirector']      
    if zd_enabled_mesh and (not tb_enabled_mesh):
        enable_all_aps_switch_port()
        zd._reset_factory()
        time.sleep(10)
        logging.info("Now navigate to the ZD's Setup_Wizard Page to set default configuration.")
        zd.conf['factory_setup_params'] = zd.feature_update[base_build_version]['info']['factory_setup_params']
        zd.conf['factory_setup_params']['mesh_enabled'] = False
        zd._setup_wizard_cfg_totally_followig_defalut_cfg({}, zd.conf['factory_setup_params'])
        zd.wait_aps_join_in_zd(list_of_connected_aps)
        
    elif tb_enabled_mesh and (not zd_enabled_mesh):
        if factory_id:
            set_aps_to_factory(list_of_connected_aps)
            enable_all_aps_switch_port()
            zd.enable_mesh()
            zd.wait_aps_join_in_zd(list_of_connected_aps)
        else:
            zd.enable_mesh()
            enable_all_aps_switch_port()
            zd.wait_aps_join_in_zd(list_of_connected_aps)
        restart_tb_mesh_ap_for_not_expect_status()
        disable_all_mesh_aps_switch_port()
        zd.wait_aps_join_in_zd(list_of_connected_aps)
        
    elif tb_enabled_mesh and zd_enabled_mesh:
        if factory_id:
            set_aps_to_factory(list_of_connected_aps)
            enable_all_aps_switch_port()
            zd.wait_aps_join_in_zd(list_of_connected_aps)
        restart_tb_mesh_ap_for_not_expect_status()
        disable_all_mesh_aps_switch_port()
        zd.wait_aps_join_in_zd(list_of_connected_aps)
    
 #Jacky.Luh update by 2012-06-26
def set_aps_to_factory(list_of_connected_aps):
    logging.info("ZD upgrade[/downgrade] to a different project, so all aps 'set factroy' to cleanup dirty data.")
    for set_factory_ap in tinf['tb'].components['AP']:
        set_factory_ap.set_factory(login=False)
        
#Jacky.Luh update by 2012-06-26        
def restart_tb_mesh_ap_for_not_expect_status():
    zd = tinf['tb'].components['ZoneDirector']
    become_mesh_ap_timeout = 1400
    for mesh_conn_ap in tinf['tb'].config['mesh_ap_mac_to_port']:
        tb_sym_active_mesh_ap_status = None
        for active_ap in tinf['tb'].config['ap_sym_dict'].keys():
            if tinf['tb'].config['ap_sym_dict'][active_ap]['mac'] == mesh_conn_ap['mac']:
                tb_sym_active_mesh_ap_status = tinf['tb'].config['ap_sym_dict'][active_ap]['status']
        start_time = time.time()
        while True:
            if time.time() - start_time > become_mesh_ap_timeout:
                raise Exception("The ap[%s] can not join in zd" % mesh_conn_ap['mac'])
            mesh_ap_status = zd._get_ap_info(mesh_conn_ap['mac'])['status']
            if mesh_ap_status.lower().startswith(u"connected") and mesh_ap_status.lower() != tb_sym_active_mesh_ap_status.lower():                    
                zd.restart_aps(mesh_conn_ap['mac'])
                break
            elif mesh_ap_status.lower().startswith(u"connected") and mesh_ap_status.lower() == tb_sym_active_mesh_ap_status.lower():
                break
            else:
                pass
            
#Jacky.Luh update by 2012-06-26
def enable_all_aps_switch_port():
    l3switch = tinf['tb'].components['L3Switch']
    for ap_mac in tinf['tb'].config['ap_mac_to_port'].keys():     
        l3switch.enable_interface(tinf['tb'].config['ap_mac_to_port'][ap_mac])

#Jacky.Luh update by 2012-06-26        
def disable_all_mesh_aps_switch_port():
    zd = tinf['tb'].components['ZoneDirector']
    l3switch = tinf['tb'].components['L3Switch']
    conn = True
    logging.info("Disable all switch ports of the testbed mesh aps, and waiting the mesh aps join in zd.")
    for mesh_ap_dict in tinf['tb'].config['mesh_ap_mac_to_port']:
        if 'Connected (Mesh AP' in zd.get_all_ap_info(mesh_ap_dict['mac'])['status']:
            continue
        else:
            conn = False
            break
               
    if conn == False:  
        for mesh_ap_dict in tinf['tb'].config['mesh_ap_mac_to_port']:
            l3switch.disable_interface(mesh_ap_dict['port'])
            
    return ''
    
    
def getSystemVersion_m1(zd = None):
    if not zd:
        zd = tinf['tb'].components['ZoneDirector']

    return zd._get_version()['version']


def getSystemVersion_m2(zd = None):
    version = ''
    if not zd:
        zd = tinf['tb'].components['ZoneDirector']

    zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
    xpath_ver = "//div[@id='portlet-sysinfo']//td[@id='sysversion']"
    if zd.s.is_element_present(xpath_ver, 2):
        data = zd.s.get_text(xpath_ver)
        m = re.match(r'([\d.]+)\s+[^\d]+(\d+)', data)
        if m:
            version = m.group(1) + '.' + m.group(2)

    return version


# TODO: test me
def resetBatchLogfile(batch):
    # remove old handler
    [logging.getLogger('').removeHandler(handler) for handler in logging.getLogger('').handlers
    if isinstance(handler, logging.FileHandler)]

    # new handler logfile
    logfile = "log_%s_%s_%s.txt" % (batch.testbed, batch.build, time.strftime("%Y%m%d%H%M"))
    fHandlr = logging.FileHandler(logfile)
    fHandlr.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    fHandlr.setFormatter(logformat)
    logging.getLogger('').addHandler(fHandlr)

def startupTestbed(testbed_name, init_tb = True):
    if init_tb or not tinf.has_key('tb'):
        tinf['tb'] = None
        tinf['tb'] = ratenv.initRatEnv(testbed_name)
    elif init_tb and tinf.has_key('tb'):
        try:
            del(tinf['tb'])
        except:
            pass
    return tinf['tb']

# Example:
#
#   import testbuild as tbld
#   tbi,bs,autotest,build_default,batch = tbld.getTargetAutotest('mesh.demo', 'ZD1000_7.1.0.0_production')
#   tbi,bs,autotest,build_10,batch = tbld.getTargetAutotest('mesh.demo', 'ZD1000_7.1.0.0_production', 10)
#
def getTargetAutotest(testbed_name, build_name, build_no = 0):
    # tbi is ZD_Stations.testbed_info
    tbi = getLogicTestbed(testbed_name)
    tinf['bs'] = bs = BuildStream.objects.get(name = build_name)
    tinf['autotest'] = autotest = AutotestConfig.objects.get(testbed = tbi, build_stream = bs)
    if build_no:
        autotest.lastbuildnum = build_no
        autotest.save()
    if tinf.has_key('debug') and tinf['debug']:
        bugme.pdb.set_trace()
    tinf['build'] = getTestBuildInfo(bs, autotest.lastbuildnum)
    batch = getTargetBatch()
    testquery = TestRun.objects.filter(batch = batch, complete = True)
    if testquery.count() < 1:
        # if no testrun record being executed; reset the batch start_time
        batch.start_time = datetime.datetime.now()
        batch.save()
    return (tinf['tbi'], tinf['bs'], tinf['autotest'], tinf['build'], batch)

def getLogicTestbed(testbed_name):
    try:
        tinf['tbi'] = Testbed.objects.get(name = testbed_name)
    except:
        tinf['tbi'] = None
    return tinf['tbi']

def getTargetBatch():
    tinf['batch'] = makeTargetBatchTestcases(tinf['tbi'], tinf['build'], tinf['autotest'].suites, tinf['autotest'].DUT)
    return tinf['batch']

# TODO: test me
def runTest1stPass():
    batch = tinf['batch']
    while True:
        # get next eligible test run
        testquery = q1stPass()
        print "There are %d TestRun(s) on batch %s." % (testquery.count(), batch)
        if testquery.count():
            testrun = testquery.order_by('suite', 'seq')[0]
            runTestrun(testrun)
        else:
            testquery = q2ndPass()
            logging.info("Test cases in batch(%s) id(#%d) were executed at least once. Of them %d are not PASS." % (batch, batch.id, testquery.count()))
            evalBatchResult(batch)
            break

def q1stPass():
    testquery = TestRun.objects.filter(batch = tinf['batch'], complete = False, skip_run = False).exclude(result__icontains = 'SKIP')
    testquery = filter_query(testquery)
    return testquery

def qp1():
    return q1stPass()

def runTest2ndPass(**kwargs):
    tcfg = dict(loop_2ndpass = 3)
    if os.environ.has_key('RAT_LOOP_2NDPASS'):
        tcfg['loop_2ndpass'] = int(os.environ['RAT_LOOP_2NDPASS'])
    tcfg.update(kwargs)
    loop_2ndpass = int(tcfg['loop_2ndpass'])
    batch = tinf['batch']
    step = 0
    while loop_2ndpass > step:
        # get next eligible test run
        step += 1
        testquery = q2ndPass()
        if testquery.count() == 0:
            evalBatchResult(batch)
            break
        print "[RETEST %d/%d] There are %d to be reExec'd on batch %s." % (step, loop_2ndpass, testquery.count(), batch)
        testInQueue = testquery.order_by('suite', 'seq')
        idlist = [x.id for x in testInQueue]
        rerunOrd = 0
        for id in idlist:
            testrun = TestRun.objects.get(id = id)
            rerunOrd += 1
            hdrinfo = "[EXEC] 2ndPass.#%d: testrun %d/%d" % (step, rerunOrd, len(idlist))
            runTestrun(testrun, step, hdrinfo)
    logging.info('Completed the 2nd pass for batch(%s), id(#%d)' % (batch, batch.id))
    testquery = q2ndPass()
    if testquery.count() > 0:
        logging.warning("Batch(%s) has %d test cases are not PASS after executing %d times [2ndPass]." % (batch, testquery.count(), loop_2ndpass))

def q2ndPass():
    testquery = TestRun.objects.filter(batch = tinf['batch'], complete = True, skip_run = False).exclude(result = 'PASS').exclude(result__icontains = 'SKIP')
    testquery = filter_query(testquery)
    return testquery

def qp2():
    return q2ndPass()

def filter_query(testquery):
    # only want those test_name and common_name
    if tinf.has_key('test_name') and tinf['test_name']:
        testquery = testquery.filter(test_name__icontains = tinf['test_name'])
    if tinf.has_key('common_name') and tinf['common_name']:
        testquery = testquery.filter(common_name__icontains = tinf['common_name'])
    # DONOT want those test_name and common_name
    if tinf.has_key('x_test_name') and tinf['x_test_name']:
        if type(tinf['x_test_name']) is list:
            for x_tname in tinf['x_test_name']:
                testquery = testquery.exclude(test_name__icontains = x_tname)
        else:
            testquery = testquery.exclude(test_name__icontains = tinf['x_test_name'])
    if tinf.has_key('x_common_name') and tinf['x_common_name']:
        if type(tinf['x_common_name']) is list:
            for x_cname in tinf['x_common_name']:
                testquery = testquery.exclude(common_name__icontains = x_cname)
        else:
            testquery = testquery.exclude(common_name__icontains = tinf['x_common_name'])
    return testquery

# TAK@20081117 When idlist="[...]" provided in command line. Function runTestrunIds()
#              will be called, and phase 1 and 2 will be ignored.
def runTestrunIds(idlist, **kwargs):
    tcfg = dict(maxloop = 1)
    tcfg.update(kwargs)

    step = 0
    while step < tcfg['maxloop']:
        step += 1
        rerunOrd = 0
        for id in idlist:
            try:
                testrun = TestRun.objects.get(id = id)
                if testrun.skip_run or testrun.result.find('SKIP') >= 0:
                    logging.info("[EXEC] idlist.#%d [%d/%d] on id %d SKIPPED." % (step, rerunOrd, len(idlist), id))
                    continue
            except Exception:
                logging.info("[EXEC] idlist.#%d [%d/%d] on id %d does not exist." % (step, rerunOrd, len(idlist), id))
                continue
            rerunOrd += 1
            hdrinfo = "[EXEC] idlist.#%d [%d/%d] on id %d" % (step, rerunOrd, len(idlist), id)
            runTestrun(testrun, 0, hdrinfo)

# TAK@20081103  Will continue execute test cases even fatal errors
#               It then consumes all 2ndPass; and exit out
# TAK@20081107  Because 'EXEC CONTINUE' mechanism, we provide the user
#               to ABORT the testing by touch files 'ABORT_RAT' or 'ABORT-RAT'
#               to stop the execution.
#               Internally, continuous # of errors >= tinf['ishould']['cnt']['cont_error']
#               will abort the execution too.
def runTestrun(testrun, rerun = 0, hdrinfo = ""):
    if os.path.exists('ABORT_RAT') or os.path.exists('ABORT-RAT'):
        tinf['ishould']['abort'] = True
        raise Exception('User request to ABORT testing now!')
    tinf['testrun'] = testrun
    printTestrun(testrun, hdrinfo, '[EXEC]')
    try:
        tinf['tb'].RunComboTest(testrun, tries = 1, rerun = rerun)
        tinf['cnt']['cont_error'] = 0
    except:
        ex = traceback.format_exc()
        logging.info('[ERROR ON EXEC]:\n%s' % ex)
        if tinf['ishould']['abort']: raise Exception(ex)
        tinf['cnt']['cont_error'] += 1
        if tinf['cnt']['cont_error'] >= tinf['ishould']['cnt']['cont_error']: raise Exception(ex)

        # Tu Bui: only for ZD
        if tinf['product'] == 'ZD':
            doRecover()
        pass

def doRecover(zd = None):
    if not zd and tinf.has_key('zd'): zd = tinf['zd']
    logging.info('[EXEC CONTINUE] Jump to ZD Login Page.')
    # need at least changelist 29864
    trycnt = 0
    while trycnt < 30:
        trycnt += 1
        try:
            zd.goto_login_page()
            return
        except Exception:
            print "[EXCEPTION] Not able to access ZD login page. Wait for 2 minutes. [Try #%d]" % (trycnt)
            time.sleep(120)
            pass


def get_case_name(common_name):
    case_name = None
    start_pos = common_name.find("[")
    end_pos = common_name.find("]")
    if start_pos>=0 and end_pos > start_pos and common_name.startswith('['):
        case_name = common_name[start_pos:end_pos+1]
    
    return case_name

def check_pass_in_testsuite(suite, case_name):
    objs = TestRun.objects.filter(batch = tinf['batch'], suite=suite) 
    tclist = [obj for obj in objs if obj.common_name.find(case_name) != -1]        
    for obj in tclist:
        if obj.result.lower() != "pass":
            return False
        
    return True

def check_pass_in_rest_testsuite(trid, idlist):
    idx = idlist.index(trid)
    rest_idlist = idlist[idx:]
    for id in rest_idlist:
        result = TestRun.objects.get(id = id).result
        if not re.match(r'pass', result, re.I):
            return False
    
    return True

def check_done_in_batch():
    objs = TestRun.objects.filter(batch = tinf['batch'])
    for obj in objs:
        if obj.result.lower() != "pass":
            return False
    return True

#def runComboTestSuite():
#    TOP_EXC_LEVEL = (0, 1)
#    for csuite in tinf['batch'].combo_suites():
#        ctests = getComboSuiteTestcases(tinf['batch'], csuite)
#        tinf['tb'].initComboTest()
#        find_top_exc_level = False
#        last_failed_level = 0
#        idlist = [x.id for x in ctests]
#        pre_case_name = ""
#        
#        pass_flag = False
#        for trid in idlist:
#            testrun = TestRun.objects.get(id = trid)
#            #@author: Jane.Guo @since: 2013-09
#            testrun.result_type = ""
#            testrun.save()
#        
#            case_name = get_case_name(testrun.common_name)
#            
#            if case_name and not pre_case_name:
#                pre_case_name = case_name
#                pass_flag = check_pass_in_testsuite(csuite, case_name)
#            
#            if case_name and pre_case_name and pre_case_name <> case_name:
#                pre_case_name = case_name
#                pass_flag = check_pass_in_testsuite(csuite, case_name)
#            
#            if case_name and pass_flag:
#                logging.info("[SKIP_Combotest %s]" % (testrun.common_name))
#                continue
#            
#            if find_top_exc_level:
#                if testrun.exc_level in TOP_EXC_LEVEL:
#                    if last_failed_level == 0:
#                        if testrun.exc_level == 0 and testrun.is_cleanup:
#                            find_top_exc_level = False
#                        else:
#                            continue
#                    elif testrun.exc_level == 1:
#                        find_top_exc_level = False
#                else:
#                    if testrun.is_cleanup and last_failed_level != 0:
#                        logging.info("[CLEANUP_Combotest %s]" % (csuite.name))
#                        result = tinf['tb'].RunComboTest(testrun, rerun = 0)
#                    else:
#                        logging.info("[SKIP_Combotest %s]" % (csuite.name))
#                    continue
#            result = tinf['tb'].RunComboTest(testrun, **dict(tries = tinf['ct_try'], rerun = 0))
#                
#            if not re.match(r'pass', result, re.I):
#                # fail/error catched;
#                # looking for next TOP_EXC_LEVEL as next executable test case.
#                logging.info("[Combotest %s] [Result %s] did not complete its task: %s"
#                            % (csuite.name,
#                               tinf['tb'].getComboTestResult(),
#                               tinf['tb'].getComboTestMessage()))
#                #if testrun.exc_level == 0:
#                    # test case designer does not want to excute other test cases; EXIT test suite
#                    # Please refer to class TestCase
#                    #logging.debug("[Abort ComboTest=%s] [exc_level ==0]" % (csuite.name))
#                    # break
#                find_top_exc_level = True
#                last_failed_level = testrun.exc_level 

def runComboTestSuite():
    for csuite in tinf['batch'].combo_suites():
        ctests = getComboSuiteTestcases(tinf['batch'], csuite)
        tinf['tb'].initComboTest()
        idlist = [x.id for x in ctests]
        pre_case_name = ""
        
        level_0_fail = False
        level_1_fail = False
        level_2_fail = False
        pass_flag = False
        
        for trid in idlist:
            testrun = TestRun.objects.get(id = trid)
            #@author: Jane.Guo @since: 2013-09
            testrun.result_type = ""
            testrun.save()
        
            case_name = get_case_name(testrun.common_name)
            level = testrun.exc_level
            
            if case_name:
                if case_name != pre_case_name:
                    pre_case_name = case_name
                    pass_flag = check_pass_in_testsuite(csuite, case_name)
                    level_1_fail = False
                    level_2_fail = False
    
                if pass_flag:
                    continue
            
            if level_0_fail:
                if level > 0:
                    continue
                elif testrun.is_cleanup == False:
                    continue
            elif level_1_fail:
                if level == 1:
                    continue
                elif level > 1 and testrun.is_cleanup == False:
                    continue
            elif level_2_fail:
                if level == 2 and testrun.is_cleanup == False:
                    continue
            else:
                rest_pass = check_pass_in_rest_testsuite(trid, idlist)
                if rest_pass and testrun.is_cleanup == False:
                    continue
            
            result = tinf['tb'].RunComboTest(testrun, **dict(tries = tinf['ct_try'], rerun = 0))
                
            if not re.match(r'pass', result, re.I):
                # fail/error catched;
                logging.info("[Combotest %s] [Result %s] did not complete its task: %s"
                            % (csuite.name,
                               tinf['tb'].getComboTestResult(),
                               tinf['tb'].getComboTestMessage()))
                if level == 0:
                    level_0_fail = True
                elif level == 1:
                    level_1_fail = True
                elif level == 2:
                    level_2_fail = True

    #Commented by Serena Tan. 2010.11.25. To support running regression and combo test suites together in the same batch. 
#    regSuites = tinf['batch'].regression_suites()
#    if len(regSuites) > 0:
#        logging.info('No support of regression and combo test suites together, SKIP test suites:\n%s' % pformat(regSuites))

def getComboSuiteTestcases(batch, ts):
    testquery = TestRun.objects.filter(batch = batch, suite = ts, skip_run = False).order_by('seq')
    passtests = testquery.filter(result__icontains = 'PASS')
    # passtests= TestRun.objects.filter(batch=batch,suite=ts,skip_run=False).filter(result__icontains='PASS')
    if len(testquery) == len(passtests):
        return ()
    return testquery

def evalBatchResult(batch = None):
    if not batch: batch = tinf['batch']
    if not batch: return
    # Collect Pass/Fail stats
    testpass = 0
    testfail = 0
    testerror = 0
    testexcept = 0
    testother = 0
    totaltests = 0
    # new summary attributes
    testskip = 0
    totalignored = 0
    testquery = TestRun.objects.filter(batch = batch, complete = True)
    if testquery.count():
        for testrun in testquery:
            # Record test pass/fail based statistics
            result = testrun.result.upper()
            if result.startswith("PASS"):
                testpass += 1
            elif result.startswith("FAIL"):
                testfail += 1
            elif result.startswith("ERROR"):
                testerror += 1
            elif result.startswith("EXCEPTION"):
                testexcept += 1
            elif re.search("SKIP", result, re.I) or testrun.skip_run:
                testskip += 1
            else:
                testother += 1
            totaltests += 1
            if re.search(r'(SKIP|IGNORE)', result, re.I):
                totalignored += 1
    batch.complete = True if testpass == testquery.count() else False
    batch.end_time = datetime.datetime.now()
    if totaltests > 0:
        batch.tests_pass = "%s (%.2f%%)" % (testpass, testpass * 100.0 / totaltests)
        batch.tests_fail = "%s (%.2f%%)" % (testfail, testfail * 100.0 / totaltests)
        batch.tests_skip = "%s (%.2f%%)" % (testskip, testskip * 100.0 / totaltests)
        batch.test_errors = "%s (%.2f%%)" % (testerror, testerror * 100.0 / totaltests)
        batch.test_exceptions = "%s (%.2f%%)" % (testexcept, testexcept * 100.0 / totaltests)
        batch.test_other = "%s (%.2f%%)" % (testother, testother * 100.0 / totaltests)
        batch.total_tests = "%s" % totaltests
        batch.save()
        logging.info("Completed a batch run of %s: " % batch)

def printTestrun(testrun, hdrinfo = '', msgid = '[EXEC]'):
    if hdrinfo: print ""
    print hdrinfo
    msgx = "%s TestRun id: #%i; batch_id: #%d; batch: (%s)" % (msgid, testrun.id, testrun.batch_id, unicode(testrun.batch))
    msgx = msgx + "\n" + "%s test_name: (%s)" % (msgid, unicode(testrun.test_name))
    msgx = msgx + "\n" + "%s common_name: (%s)" % (msgid, unicode(testrun.common_name))
    msgx = msgx + "\n" + "%s test_params: %s" % (msgid, unicode(testrun.test_params))
    print msgx
    return msgx

# Example:
#
#   import tesbuild as tbld
#   tb = tbld.testBuild('zd1k.demo', 'ZD1000_7.1.0.0_production', bno=11)
#
def testBuild(testbed_name, build_name, **kwargs):
    tcfg = dict(bno = 0, init_tb = True)
    tcfg.update(kwargs)
    build_no = int(tcfg['bno'])

    # ATTENTION:
    #    The logging mechanism is initialized when ZD_Stations is created.
    #    If not enabled first, you are not going to see logging messages.
    if tinf.has_key('batchonly') and tinf['batchonly']:
        # no need to initialize Testbed; because we only want to create batch
        tbi, bs, autotest, build, batch = getTargetAutotest(testbed_name, build_name, build_no)
        return None
    else:
        tb = startupTestbed(testbed_name, tcfg['init_tb'])

    tbi, bs, autotest, build, batch = getTargetAutotest(testbed_name, build_name, build_no)

    if len(tinf['db_testrun_errorlist']) > 0 and printDbTestrunErrorList():
        return None

    # Tu Bui: only for ZD
    if tinf['product'] == 'ZD':
        tinf['h'] = {}
        tinf['zd'] = zd = tinf['tb'].components['ZoneDirector']
        tinf['zdcli'] = zdcli = tinf['tb'].components['ZoneDirectorCLI']
        #record the zd's base build version in the execution
        ih.set_base_build(build_name, build_no)
        #record the zd's current build version in the execution
        ih.set_cur_build(zd._get_version()['version'])
        
        #upgrade zd to the base build
        upgradeSoftwareBuild()
        #get the even template from zd cli: /bin/messages and /bin/messages_US
        zd.init_messages_bundled(zdcli)
        
        tagTestbedAPsInfo(zd)

    # TAK@20090916 For combotest, we step into different path
    if len(tinf['batch'].combo_suites()) > 0:
        #Modified by Serena Tan. 2010.11.25. To support running regression and combo test suites together in the same batch.     
        #runComboTestSuite()
        if len(tinf['batch'].regression_suites()) > 0:
            runMixTestSuite()
        else:
            #Add by cwang@2011-10-26
            #Add by jluh@2012-12-10
            cnt = tinf['ct_try']
            while cnt:
                logging.info('%d tried' % cnt)
                cnt = cnt -1
                if not check_done_in_batch():      
                    runComboTestSuite()
    else:
        if tinf.has_key('idlist') and tinf['idlist']:
            runTestrunIds(tinf['idlist'], maxloop = int(tinf['idmaxloop']))
            return tb

        if tinf['ishould'].has_key('skip_p1') and tinf['ishould']['skip_p1']:
            logging.info('[ATTN] User requested to skip phase 1 process')
        else:
            runTest1stPass()
        if tinf['ishould'].has_key('skip_p2') and tinf['ishould']['skip_p2']:
            logging.info('[ATTN] User requested to skip phase 2 process')
        else:
            runTest2ndPass()

    #TODO: clean env
    tb.cleanup()

    evalBatchResult()
    #tagTestbedAPsInfo(zd, 'ap.01.end')
    if zd.selenium:
        zd.selenium.stop()
        
    try:
        if tcfg.has_key('reboot_sta') and tcfg['reboot_sta']:
            if tinf['tb'].components['Station']:
                sta_ip_addr_list = []
                for sta in tinf['tb'].components['Station']:
                    sta_ip_addr_list.append(sta.sta_ip_addr)
                    sta.reboot_station()
                    sta.__del__()
                    time.sleep(10)
                for sta_ip in sta_ip_addr_list: 
                    times = 0
                    while True:
                        if 'Timeout exceeded' in utils.ping(sta_ip):
                            time.sleep(10)
                            if 'Timeout exceeded' in utils.ping(sta_ip):
                                logging.info("The staion[%s] is reboot" % sta_ip)
                                break
                            else:
                                continue
                        if times >= 30:
                            raise Exception("The station[%s] can't reboot, please have check." % sta_ip)
                        times += 1
                        time.sleep(2)
                    times = 0
                    while True:
                        if 'Timeout exceeded' not in utils.ping(sta_ip):
                            time.sleep(10)
                            if 'Timeout exceeded' not in utils.ping(sta_ip):
                                logging.info("The staion[%s] is reconnected" % sta_ip)
                                break
                            else:
                                continue
                        if times >= 30:
                            raise Exception("The station[%s] can't reconnected, please have check." % sta_ip)
                        times += 1
                        time.sleep(2)
    except:
        pass
                   
    return tb

#Added by Serena Tan. 2010.11.25. To support running regression and combo test suites together in the same batch. 
def runMixTestSuite():
    if tinf.get('idlist'):
        runTestrunIds(tinf['idlist'], maxloop = int(tinf['idmaxloop']))
        return
    
    else:
        runComboTestSuite()
        
        if tinf['ishould'].get('skip_p1'):
            logging.info('[ATTN] User requested to skip phase 1 process')
        else:
            runReg1stPass()
            
        if tinf['ishould'].get('skip_p2'):
            logging.info('[ATTN] User requested to skip phase 2 process')
        else:
            runReg2ndPass()
            
#Added by Serena Tan. 2010.11.25. To support running regression and combo test suites together in the same batch.    
def runReg1stPass():
    batch = tinf['batch']
    for rsuite in tinf['batch'].regression_suites():
        while True:
            testquery = TestRun.objects.filter(batch = batch, suite = rsuite, complete = False, skip_run = False).exclude(result__icontains = 'SKIP')
            testquery = filter_query(testquery)
            print "There are %d TestRun(s) not completed on suite %s." % (testquery.count(), rsuite)
            if testquery.count():
                testrun = testquery.order_by('seq')[0]
                runTestrun(testrun)
                
            else:
                testquery = TestRun.objects.filter(batch = batch, suite = rsuite, complete = True, skip_run = False).exclude(result = 'PASS').exclude(result__icontains = 'SKIP')
                testquery = filter_query(testquery)
                logging.info("Test cases in suite(%s) id(#%d) were executed at least once. Of them %d are not PASS." % (rsuite, batch.id, testquery.count()))
                break
            
#Added by Serena Tan. 2010.11.25. To support running regression and combo test suites together in the same batch.         
def runReg2ndPass():    
    loop_2ndpass = 3
    if os.environ.has_key('RAT_LOOP_2NDPASS'):
        loop_2ndpass = int(os.environ['RAT_LOOP_2NDPASS'])
    
    batch = tinf['batch']
    step = 0
    while loop_2ndpass > step:
        step += 1
        for rsuite in batch.regression_suites():
            testquery = TestRun.objects.filter(batch = batch, suite = rsuite, complete = True, skip_run = False).exclude(result = 'PASS').exclude(result__icontains = 'SKIP')
            testquery = filter_query(testquery)
            if testquery.count() == 0:
                continue
            
            print "[RETEST %d/%d] There are %d to be reExec'd on suite %s." % (step, loop_2ndpass, testquery.count(), rsuite)
            testInQueue = testquery.order_by('seq')
            idlist = [x.id for x in testInQueue]
            rerunOrd = 0
            for id in idlist:
                testrun = TestRun.objects.get(id = id)
                rerunOrd += 1
                hdrinfo = "[EXEC] 2ndPass.#%d: testrun %d/%d" % (step, rerunOrd, len(idlist))
                runTestrun(testrun, step, hdrinfo) 
                
            testquery = TestRun.objects.filter(batch = batch, suite = rsuite, complete = True, skip_run = False).exclude(result = 'PASS').exclude(result__icontains = 'SKIP')
            testquery = filter_query(testquery)
            if testquery.count() > 0:
                logging.warning("Suite(%s) has %d test cases not PASS after executing %d times [2ndPass]." % (rsuite, testquery.count(), loop_2ndpass))

def tagTestbedAPsInfo(zd, tagid = ''):
    tb = tinf['tb']
    zd = tb.components['ZoneDirector']

    if not tinf.has_key('h'): tinf['h'] = {}
    if not tagid:
        tagid = 'ap.00.start'
        tinf['h'][tagid] = tb.aps_info_list
    else:
        tm0 = time.time()
        apinfo = zd.get_all_ap_info()
        tm1 = time.time()
        asctime = time.asctime(time.localtime(tm0))
        tinf['h'][tagid] = [asctime, tm0, int(tm1 - tm0), apinfo]
    logging.debug("[FetchAPs %s] Take %d seconds to walk through %d APs' Info"
                 % (tagid, tinf['h'][tagid][2], len(tinf['h'][tagid][3])))

try:
    if tinf: pass
except:
    tinf = {'batchonly': False, 'rebuildbatch': False, 'displevel': 0, 'idmaxloop': 1, 'ct_try': 1}
    tinf['ishould'] = {'chkv': True, 'abort': False, 'cnt': {'cont_error': 10}, 'email': True}
    tinf['cnt'] = {'cont_error': 0}
    tinf['db_testrun_errorlist'] = {}
    tinf['tb'] = None

def printDbTestrunErrorList():
    print "\n\nDB TestRun Creation ErrorList:\n"
    noc = 0
    for trid in sorted(tinf['db_testrun_errorlist']):
        if trid == 0:
            print "\n\n\n%s\n" % ('!' * 68)
            print "TestRun created with cavets:\n\t%s" % (tinf['db_testrun_errorlist'][trid])
            print "\n%s\n\n\n" % ('!' * 68)
            continue
        try:
            trun_00 = tinf['db_testrun_errorlist'][trid]
            trun = TestRun.objects.get(id = trun_00.id)
            print "TestRun %d exists: %s" % (trun.id, trun)
        except Exception, e:
            print "TestRun not exist: %s" % (tinf['db_testrun_errorlist'][trid])
            noc += 1
    if noc > 0:
        print "\n[DB ERROR] There are %d TestRun records not created" % (noc)
    else:
        print "\n[DB WARNING] All TestRun records are actually created"

    tinf['db_testrun_errorlist'] = {}
    return noc

# make _topts as object which should have function to get the key in the order enterred
def touchTinf(_topts):
    if _topts.has_key('debug') and _topts['debug']:
        tinf['debug'] = _topts['debug']
        bugme.pdb.set_trace()
    # Tu Bui: figure out which product is being tested
    if _topts.has_key('product') and _topts['product']:
        tinf['product'] = _topts['product']
    else:
        tinf['product'] = 'ZD'
    _optGetIdlist(_topts)
    # _optGetTargetTestCommonName(_topts)
    _optGetOptions(_topts)



def _optGetIdlist(_topts):
    if _topts.has_key('idlist'):
        if type(_topts['idlist']) in (list,):
            tinf['idlist'] = _topts['idlist']
        else:
            tinf['idlist'] = eval(_topts['idlist'])

def _optGetTargetTestCommonName(_topts):
    for key in ['test_name', 'common_name']:
        if _topts.has_key(key):
            pk1 = 'p1_' + key
            pk2 = 'p2_' + key
            tinf[pk2] = tinf[pk1] = _topts[key]

def _optGetOptions(_topts):
    for key in ['chkv', 'skip_p1', 'skip_p2', 'email']:
        if _topts.has_key(key):
            tinf['ishould'][key] = _topts[key]
    tinf['testrun'] = None
    for key in ['batchonly', 'rebuildbatch', 'displevel', 'idmaxloop',
                'test_name', 'common_name', 'x_test_name', 'x_common_name',
                'ct_try']:
        if _topts.has_key(key):
            tinf[key] = _topts[key]
    tinf['displevel'] = int(tinf['displevel'])
    tinf['ct_try'] = int(tinf['ct_try'])
    tinf['ct_try'] = 1 if tinf['ct_try'] < 1 else tinf['ct_try']


def main(build_name, testbed_name, **kwargs):
    """
    Main entry to the test run QA style:
        Find the AutotestConfig record that define a testbed's execution target,
        build_name and build_no. The user can overwrite the build_no using the
        keyword bno.
        Example:

            main('ZD1000_7.1.0.0_production','mesh.f.fanout',bno=12')
    """
    _topts = {}
    _topts.update(kwargs)

    touchTinf(_topts)
    try:
        RatLogger.init_logger(testbed_name)
        tb = testBuild(testbed_name, build_name, **kwargs)
        if not tb:
            return None

        batch = tinf['batch']
        body = "Batch %s completed:\n" % str(batch)
        subject = 'Batch %s completed its execution.' % str(batch)
        mailBatchExecStatus(subject, body)

    except:
        # print "\n\n%s" % ('!' * 68)
        ex = traceback.format_exc()
        logging.info('EXCEPTION\n%s' % ex)
        msgx = '### NO TESTRUN RECORDS ###'
        if tinf['testrun']:
            msgx = printTestrun(tinf['testrun'], 'The TestCase(testrun) in EXCEPTION:', '[EXCEP]')
        elif not tinf.has_key('tb'):
            print ex
        tinf['db_testrun_errorlist'] = "There are %d records at db_testrun_errorlist" % len(tinf['db_testrun_errorlist'])
        print '\nInternal processing instruction:\n%s' % pformat(tinf)
        if not tinf.has_key('tbi'):
            getLogicTestbed(testbed_name)
        if tinf.has_key('tbi') and tinf['tbi']:
            batch = tinf['batch'] if tinf.has_key('batch') else 'UNKNOWN'
            body = msgx + "\n\n" + ex + "\n\n" + pformat(tinf)
            subject = 'Batch %s aborted its execution due to exceptions.' % str(batch)
            mailBatchExecStatus(subject, body)
        iQuit(2)        
    finally:
        RatLogger.close_logger(testbed_name)
        


def mailBatchExecStatus(subject = 'Test completed', body = '', **kwargs):
    if not tinf['ishould']['email']: return
    tcfg = dict(mailserver = '172.16.100.20', sender = 'zd.rat@ruckuswireless.com')
    tcfg.update(kwargs)
    TE_info = getHostInfo()
    try:
        recver = tinf['tbi'].owner
        print 'mail subject:"TE:%s %s" to:"%s"' % (TE_info, subject, recver)
        if tinf.has_key('batch'):
            batch = tinf['batch']
            evalBatchResult(batch)
            body = body \
                 + "\n\n[Batch Autotest Summary on TestEngine:%s]" % TE_info \
                 + "\n    PASS: %s" % str(batch.tests_pass) \
                 + "\n    FAIL: %s" % str(batch.tests_fail) \
                 + "\n   ERROR: %s" % str(batch.test_errors) \
                 + "\n   TOTAL: %s" % str(batch.total_tests)
        subject = 'TE:%s completed batch %s.' % (TE_info, str(batch))
        utils.send_mail(tcfg['mailserver'], recver, tcfg['sender'], subject, body)
    except Exception, e:
        print 'sendMail failed: %s' % (e.message)

def getHostInfo():
    import socket
    hostname = socket.gethostname()
    slist = socket.getaddrinfo(hostname, 80)
    hinfo = [x for x in slist if x[4][0].startswith('172')]
    hinfo = hinfo[0] if hinfo else slist[0]
    if not hinfo: return '[%s 0.0.0.0]' % (hostname,)
    return '[%s %s]' % (hostname, hinfo[4][0])

def iQuit(exit_code = 0):
    if not os.environ.has_key('LAUT_SIGNATURE'):
        import sys
        sys.exit(exit_code)

    # TAK@20090116 -- When testbuild.py started up using CMD:START command
    #                 launched by laut.py; exit() command does not terminate
    #                 the program. So we resolve to call the pskill program to
    #                 terminated testbuild.py itself.

    #Updated by cwang@2012/7/19
    #Do cleanup before kill current PID, make sure selenium_mgr has been destoried.
    clean_up_rat_env()

    import subprocess
    pid = os.getpid()
    psKill = r'c:\bin\win\pskill'
    try:
        msg = "I, pid=%s, ask %s to terminate me because Python would not exit(), if launched using START!" % (str(pid), psKill)
        aha = "+%s+" % ('-' * (2 + len(msg)))
        print "%s\n| %s |\n%s" % (aha, msg, aha)
        time.sleep(2)
    except:
        pass
    subprocess.call('%s -t %s' % (psKill, str(pid)))

def testBuild_Usage():
    print """
    QA regression execution statement:

        QA runs [build-stream ZD3000_8.2.0.0_production] [on-logic-testbed mesh.fanout] [with-build-no 277]

    Usage: qarun.py <build-stream> <logical-testbed> [<args>]

    Where <args> are keyword=[value] pair:
        Keyword        What is represent
        -------        ---------------------------------------------------
        product        default='ZD'; define which product is being tested
        bno            build no, overwrite lastbuildnum of AutotestConfig
        chkv           default=True; check ZD version
        email          default=True; send test result to testbed's owner
        debug          default=False; step into debug mode
        idlist         testrun id list to be executed; only once
                       Example: idlist="[34,130,56,40]"
                                idlist="range(100,121)"
                                idlist="[34,40]+range(100,121)"
        test_name      only testrun's test_name contains test_name executed
        common_name    only testrun's common_name contains common_name executed
        x_test_name    exclude x_test_name from testrun queried to be executed
        x_common_name  exclude x_common_name from testrun queried to be executed
        batchonly      default=False; create a autotest's batch only
                       test execution skipped
        rebuildbatch   rebuild AutotestConfig's batch's testrun record from
                       its Autotestconfig's suits; it means you can add test
                       suites to Autotestconfig and rebuild it.
        displevel      default=0; if true display existing testrun record
                       when rebuilding batch's test suites.

    Examples:

        qarun.py ZD1000_7.1.0.0_production netanya.sys bno=12

        # run for product FM
        qarun.py FM_8.1.0.0_production fm_saigon bno=12 product=FM
        # skip phase 2 process
        qarun.py ZD1000_7.1.0.0_production mesh.specific bno=12 skip_p2=True
        # skip phase 1 process; go ahead and redo FAIL/ERROR tests
        qarun.py ZD1000_7.1.0.0_production mesh.f.fanout bno=12 skip_p1=True
        # no need to check version; and goes into debug mode ASAP
        qarun.py ZD1000_7.1.0.0_production mesh.f.fanout bno=12 chkv=False debug=True

        # create AutotestConfig's batch only; no software upgrade, or running tests
        qarun.py ZD1000_7.1.0.0_production mesh.f.fanout bno=12 batchonly=True
        # only run testrun ids = [23, 89, 65, 153] which should be enclosed by double quote
        qarun.py ZD1000_7.1.0.0_production mesh.f.fanout bno=12 idlist="[23,89,65,153]"
        qarun.py ZD1000_7.1.0.0_production mesh.f.fanout bno=12 idlist="range(101,103)"

        # run test case's common name contains ROOT, but not 2942
        qarun.py ZD3000_8.1.1.0_production mesh.f.fanout bno=12 common_name="ROOT" x_common_name="2942"
    """

if __name__ == "__main__":
    import sys
    from RuckusAutoTest.common.lib_KwList import as_dict
    if len(sys.argv) < 3:
        testBuild_Usage()
        iQuit(1)

    else:
        _dict = as_dict(sys.argv[3:])
        try:
            main(sys.argv[1], sys.argv[2], **_dict)

        except:
            print "\n\n%s" % ('!' * 68)
            ex = traceback.format_exc()
            print ex

            if tinf['testrun']:
                printTestrun(tinf['testrun'], 'The TestCase(testrun) in EXCEPTION:', '[EXCEP]')

            iQuit(1)

    iQuit(0)


