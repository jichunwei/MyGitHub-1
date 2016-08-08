"""
Ruckus Automation Test Framework
Copyright (C) 2008 Ruckus Wireless, Inc.
All rights reserved.

See rat/doc/Framework.pdf for static UML model of this framework.

Note that Test classes are not modeled in the database because the implementing python code itself is the authoratative description of a test case.
"""
RAT_MODEL_VER = ('0.2')

import os
#import sys
import datetime
import time

#import traceback
import logging
from pprint import pformat
import re

from django.db import models
from django.db import IntegrityError

from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest import BeautifulSoup
#from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common import lib_DBUtil as dbu
from RuckusAutoTest.components.lib.zdcli import process_mgr
from contrib.download import image_helper as ih
from RatLogger import RatLogger
import ctypes
STD_OUTPUT_HANDLE= -11 
FOREGROUND_YELLOW = 0x06 
FOREGROUND_GREEN = 0x02 
FOREGROUND_RED = 0x04
FOREGROUND_WHITE = 0x7    
BACKGROUND_BLACK = 0x0 
  
handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)  
def set_color_yellow():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_YELLOW|BACKGROUND_BLACK)       
def set_color_red():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_RED|BACKGROUND_BLACK) 
def set_color_green():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_GREEN|BACKGROUND_BLACK)
def set_color_white():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_WHITE|BACKGROUND_BLACK)
 
class BugInfo(models.Model):
    PRODUCT_TYPES = (
        ('AP', 'Ap standalone'),
        ('ZD', 'Zone Director'),
        ('FM', 'Flex Master'),
    )

    BUG_TYPES = (
        ('S', 'Script'),
        ('F', 'Feature'),
        ('N', 'Not known'),
    )
    bug_id = models.IntegerField(help_text="Bug ID which is the same in Bug Zilla (e.g. 1134)")
    product = models.CharField(max_length=2, choices=PRODUCT_TYPES,
                               help_text="Product that this bug belongs to (e.g. Flex Master)")
    type = models.CharField(max_length=2, choices=BUG_TYPES,
                            help_text="Type of this bug(e.g. Script)")
    description = models.TextField(help_text="Brief description of this bug")
    build_stream = models.ForeignKey('BuildStream', help_text="Build Stream that this bug belongs to")
    build = models.ForeignKey('Build', help_text="Build that this bug belongs to")

    def __unicode__(self):
        return self.description
    class Admin:
        list_display = ('bug_id', 'product', 'build_stream', 'build', 'type', 'description')


class BuildStream(models.Model):
    """
    The BuildStream class models a set of related builds from a build server.
    It really corresponds to the combination of a build tree from source control plus
    build configuration (e.g. a build profile). The BuildStream class is responsible for
    creating new Build objects as they become available on the build server.
    """
    name        = models.CharField(max_length=60,
                                   unique=True,
                                   help_text="Verbose name for this build stream,(e.g. AP2825_4.2.0_production)")
    prefix      = models.CharField(max_length=22,
                                   help_text="Short version prefix for this stream (e.g. 4.2.0). Combined with build number to make build name.")
    URL         = models.URLField(blank=True)
    description = models.TextField(blank=True)

    #Updated by cwang@20130627, obsoleted
    def GetK2Builds(self, url):
        """
        Return a list of builds found on K2 from the specified URL.
        (e.g. http://k2.video54.local/cgi-bin/build_info.pl?filename=www_AP2825_4.2.0_production)
        Each list item is a dictionary of 'columns' and values.
        """
        pass 

    #Updated by cwang@20130627, obsoleted
    def CheckNewBuilds(self):
        """
        Create database objects for any new builds found on build server for this BuildStream.
        """
        pass

    #Updated by cwang@20130627, obsoleted
    def CheckNewBuilds_V2(self, buildstream, build_no, version):
        pass

    def __unicode__(self):
        return self.name

class Build(models.Model):
    """
    A unique software image that can be loaded onto a device under test.
    Each build is associated with BuildStream and has a characteristic build number and label.
    """
    build_stream = models.ForeignKey(BuildStream)
    number       = models.IntegerField(help_text="Build number within a build stream.")
    builder      = models.CharField(max_length=20, blank=True,
                                    help_text="Build creator")
    version      = models.CharField(max_length=20,
                                    help_text="short name for this build (e.g. 4.2.0.171)")
    label        = models.CharField(unique=True, max_length=64,
                                    help_text="verbose build label (e.g. lnxbuild_ap_ap2825420_20080116_540p_chg18762_171)")
    timestamp    = models.DateTimeField(help_text="Build Start time")
    URL          = models.URLField()
    def __unicode__(self):
        return "%s" % (self.version)
    class Meta:
        ordering = ['number']

class TestbedComponent(models.Model):
    """
    A physical component of a testbed such as an AP, Laptop, PC, attenuator, etc.
    Classes defined elsewhere implement the interface to config/control the testbed components.
    Test code uses these testbed component interfaces to configure and control the testbed.
    (Ideally those component classes would derive directly from this TestbedComponent base class
    but django doesn't currently allow that...)
    """
    name        = models.CharField(unique=True, max_length=30,
                                   help_text='Name of this component and the python class that implements it')
    description = models.TextField(blank = True, help_text = 'Description of this component.')
    config       = models.TextField(blank=True,
                                    help_text='Basic testbed component configuration parameters (e.g. DUT IP address) as a python dictionary string')
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ('name',)



class TestbedType(models.Model):
    """
    TestbedType models a class of testbeds that generally share the same topology, component types, and purpose.
    """
    name         = models.CharField(unique=True, max_length=50,
                                    help_text='The name of the python class that implements this type of testbed')
    description  = models.TextField(blank=True,
                                    help_text="Description of this testbed and description of all configuration parameters")
    diagram      = models.ImageField(blank=True, upload_to='\\\\192.168.10.2\\rat',
                                     help_text="Upload topology for this type of test bed. Support only .JPG, .PNG")
    # diagram field requires extra libraries and stuff

    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ('name',)

class Testbed(models.Model):
    """
    A testbed info class that encapsulates common info and configuration.
    Real testbed class implementations will contain an instance of this class.
    Ideally this would be implemented as an abstract base class but django models doesn't currently support ABC's.
    """
    name         = models.CharField(unique=True, max_length=50,
                                    help_text='Unique name for this physical testbed')
    tbtype       = models.ForeignKey(TestbedType)
    location     = models.CharField(max_length=100)
    owner        = models.EmailField("Owner Email",
                                     help_text='Address for reporting testbed problems.')
    resultdist   = models.EmailField("Results Email",
                                     help_text='Default address for emailing batch results')
    description  = models.TextField(blank=True)
    config       = models.TextField(blank=True,
                                    help_text='Basic testbed configuration parameters (e.g. DUT IP address) as a python dictionary string')

    def __unicode__(self):
        return self.name

class TestPlan(models.Model):
    """
    Test Plan for execution
    """
    name = models.CharField(unique=True, 
                            max_length=100,
                            help_text="Test plan name, the same as TestLink.")
    
    notes = models.TextField(blank=True, 
                                   help_text="Summary test plan.")
    
    def __unicode__(self):
        return self.name


class TestSuite(models.Model):
    """
    A TestSuite is a mechanism for grouping related TestCases along with any explicit component
    configuration that should be in effect for that set of TestCases.
    """
    TS_REGRESSION = ''
    TS_COMBO = 'combo'
    SUITE_TYPES = (
        (TS_REGRESSION, 'Regression Tests'),
        (TS_COMBO, 'Combination/Composition Tests'),
    )
    name        = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    config      = models.TextField(blank=True,
                                   help_text="Text dictionary of testbed component configs to use for this test suite")
    xtype        = models.CharField(blank=True, max_length=8,
                                    choices=SUITE_TYPES,
                                    help_text="eXecution type of this test suite. Default is regression test.")
    def asComboTest(self):
        self.xtype = self.TS_COMBO
    def is_combo_test(self):
        return self.xtype == self.TS_COMBO
    def num_tests(self):
        return TestCase.objects.filter(suite=self).count()
    def __unicode__(self):
        return "%s" % (self.name)

class AutotestConfig(models.Model):
    """
    This class is used to configure a testbed.
    It is used to specify what test suites are automatically run against
    new Builds from a particular BuildStream.
    """
    testbed      = models.ForeignKey(Testbed)
    build_stream = models.ForeignKey(BuildStream)
    suites       = models.ManyToManyField(TestSuite, null=True,
                                          help_text="list of test suites to run for this batch",
                                          )
    lastbuildnum = models.IntegerField(default=0,
                                       help_text="Last build number autotested; Only test new builds greater than this.")
    seq        = models.IntegerField(default=0,
                                       help_text="Specifies priority of this build_stream if multiple build streams have new builds available")
    DUT          = models.ForeignKey(TestbedComponent, blank=True, null=True,
                                     help_text="The testbed component under test (if testbed has multiple potential DUTS)")

    def suite_list(self):
        """return a list of suites for display purposes"""
        return ','.join([s.__unicode__() for s in self.suites.all()])
    def __unicode__(self):
        return "%s %s" % (self.testbed, self.build_stream)
    def regression_suites(self):
        """return a list of regression suites"""
        return [c for c in self.suites.all() if TestSuite.TS_REGRESSION == c.xtype]
    def combo_suites(self):
        """return a list of combotest suites"""
        return [c for c in self.suites.all() if TestSuite.TS_COMBO == c.xtype]
    class Meta:
        ordering = ('seq',)

class AutotestExecution(models.Model):
    '''
    This class is used to configure execution testbed.
    It is used to layout execution priority for different logical test beds.
    '''
    STATUS_TYPES = (
        ('N', 'Not Start'),
        ('D', '100%'),
        ('U', 'Not Completed'),
        ('R', 'Running'),
    )
    skip_run     = models.BooleanField(default=False,
                                       help_text="Enable to skip this test during execution.")    
    autoconfig = models.ForeignKey(AutotestConfig)
    
    cur_status = models.CharField(default="N", max_length=2, 
                                  choices=STATUS_TYPES,
                                  help_text = "Status of Tasks"
                                  )
     
    build_number = models.PositiveIntegerField(default = 0,
                                               help_text = "Build number of Zone Director")
    
    priority = models.IntegerField(default = 100,                                   
                                   help_text = "Relative ordering of different test beds.")
    
    reboot_station = models.BooleanField(default=True, 
                                     help_text ="Enable to reboot station before perform test bed.")
    
    check_version = models.BooleanField(default=True,
                                        help_text = "Enable to auto-check ZoneDirector version."
                                        )
    
    test_plan = models.ForeignKey(TestPlan)
    top_suite = models.CharField(default="Automation",
                                 help_text = "Top folder of test suites",
                                 max_length=50,
                                )
    
    def __unicode__(self):
        return '%s %d' % (self.autoconfig, self.build_number)
    
        
    def get_auto_config(self):
        return self.autoconfig    
    execution_tasks = get_auto_config
    
    def _get_batch(self):
        objs = Batch.objects.filter(testbed=self.autoconfig.testbed)\
            .filter(build__build_stream=self.autoconfig.build_stream)\
            .filter(build__number = self.build_number)
        item = None
        if objs:
            item = objs[0]
        return item
        
    def get_status_page(self):        
        item = self._get_batch()        
        if item:
            if item.complete:
                cur_status = "D"
                status = "DONE[100%]"
            elif self.cur_status == "R":
                cur_status = "R"
                status = "Running[%s]" % item.total_tests
            else:
                cur_status = "U"
                status = "[Total#%s Pass#%s Fail#%s Error#%s]" % (item.total_tests, 
                                                                  item.tests_pass, 
                                                                  item.tests_fail, 
                                                                  item.test_errors)
                
            if cur_status != self.cur_status:
                self.cur_status = cur_status
                self.save(force_update=True)
                            
            batch_id = item.id
            tbname = self.autoconfig.testbed.name
            return "<a href='/admin/reportdetail/%s?detail=False&tbname=%s' title='Detail Report'>%s</a>" % \
                                                                                    (batch_id, tbname, status)
        else:
            if self.cur_status == "N":
                return "Not Start"
            elif self.cur_status == "R":
                return "Running"
            else:
                return "Unknown"
        
    get_status_page.allow_tags = True
    status = get_status_page
    
    def get_autoconfig_page(self):        
        return "<a href='/admin/RuckusAutoTest/autotestconfig/%s/'>%s</a>" % (self.autoconfig.id, 
                                                                                 self.autoconfig)
    
    get_autoconfig_page.allow_tags = True
    autoconfig_settings = get_autoconfig_page
    
    def clone(self):
        obj = AutotestExecution()
        obj.skip_run = self.skip_run
        obj.autoconfig = self.autoconfig
        obj.test_plan = self.test_plan
        obj.top_suite = self.top_suite
        obj.priority = self.priority
        obj.reboot_station = self.reboot_station
        obj.check_version = self.check_version
        _ll = AutotestExecution.objects.filter(autoconfig = self.autoconfig)
        max_num = max([o.build_number for o in _ll])
        obj.build_number = max_num + 1
        builds = Build.objects.filter(build_stream = self.autoconfig.build_stream).filter(number = obj.build_number)
        if not builds:
            build_prefix_index = 1
            build = Build()
            build.build_stream = self.autoconfig.build_stream
            build.number = obj.build_number            
            build.version = "%s.%s" % (build.build_stream.name.split("_")[build_prefix_index], build.number)
            build.label =  build.version
            build.timestamp = datetime.datetime.now()
            build.URL = "http://nanhu.tw.video54.local"
            build.save(force_insert=True)
        return obj
             
    class Meta:
        ordering = ('priority',)
        unique_together = ("autoconfig", "build_number")
    
        

class Batch(models.Model):
    """
    Batch objects are used to schedule and track test suite runs and (eventually) group test results for reporting purposes.
    """
    testbed      = models.ForeignKey(Testbed,
                                     help_text="Testbed to which this batch belongs")
    build        = models.ForeignKey(Build,
                                     help_text="DUT software build for this test batch")
    suites       = models.ManyToManyField(TestSuite,
                                          help_text="list of test suites to run for this batch",
                                          )
    seq        = models.IntegerField(default=0, help_text="Relative ordering of different batches")
    timestamp    = models.DateTimeField(help_text="Time that this batch was first scheduled.")
    start_time   = models.DateTimeField(blank=True, null=True)
    end_time     = models.DateTimeField(blank=True, null=True)
    result_email = models.EmailField(blank=True,
                                     help_text="Email address for batch result report")
    complete     = models.BooleanField(default=False, help_text="True if batch has finished running.")
    DUT          = models.ForeignKey(TestbedComponent, blank=True,null=True,
                                     help_text="The testbed component under test (if testbed has multiple potential DUTS)")
    total_tests   = models.CharField(max_length=15, blank=True)
    tests_pass    = models.CharField(max_length=15, blank=True)
    tests_fail    = models.CharField(max_length=15,  blank=True)
    test_errors   = models.CharField(max_length=15, blank=True, help_text="Errors encountered that prevented test from completing")
    tests_skip    = models.CharField(max_length=15, blank=True, help_text="Tests skipped by test runner because testrun's skip_run is true.")
    test_exceptions  = models.CharField(max_length=15, blank=True, help_text="Script errors encountered that prevented test from completing")
    test_other    = models.CharField(max_length=15, blank=True, help_text="Other non-categorized test results")
    def suite_list(self):
        """return a test list of suites for display purposes"""
        return ','.join([s.__unicode__() for s in self.suites.all()])
    def combo_suites(self):
        """return a list of combotest suites"""
        return [c for c in self.suites.all() if TestSuite.TS_COMBO == c.xtype]
    def regression_suites(self):
        """return a list of regression suites"""
        return [c for c in self.suites.all() if TestSuite.TS_REGRESSION == c.xtype]
    def __unicode__(self):
        return "%s:%s" % (self.testbed, self.build)
    class Meta:
        ordering = ('seq', 'timestamp',)


class TestRun(models.Model):
    """
    The result of running an individual Test case.
    Note that parameters are purposely copied here from TestCases at runtime. This was a concious design decision
    (instead of referencing TestCase objects with a ForeignKey()) that prevents historical TestRun confusion if individual
    TestCases changes in the database.
    VERSION 2: added
        suite and skip_run, and by default they are ordered by suite+order
        exc_level: refer to class TestCase
    SQLITE3 command to add column exc_level:
        alter table RuckusAutoTest_testrun add column exc_level integer default 0;
    """
    batch        = models.ForeignKey(Batch)
    suite        = models.ForeignKey(TestSuite)
    test_name    = models.CharField(max_length=80)
    test_params  = models.TextField(blank=True)
    common_name  = models.CharField(blank=True, max_length=120)
    run_name     = models.CharField(blank=True, max_length=120)
    config       = models.TextField(blank=True,
                                    help_text="Text dictionary of testbed component configs to use for this test case")
    complete     = models.BooleanField()
    seq        = models.IntegerField()
    exc_level    = models.IntegerField(default=0,
                                       help_text="test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR")
    is_cleanup   = models.BooleanField(default=False,
                                       help_text="Is a cleanup test case?")
    skip_run     = models.BooleanField(default=False,
                                       help_text="Enable to skip this test during execution.")
    start_time   = models.DateTimeField(blank=True, null=True)
    end_time     = models.DateTimeField(blank=True, null=True)
    result       = models.CharField(max_length=100, blank=True,
                                    help_text='short result string. Format of this string is specified by result_type')
    result_type  = models.CharField(max_length=30,  blank=True,
                                    help_text='Type of result: passfail, numeric, etc')
    message      = models.TextField(blank=True)
    halt_if      = models.CharField(max_length=100, blank=True,
                                    help_text="keyword list of: begin_combo,begin_t_run,pass,fail,error,t_config,t_test,t_cleanup,after_t_run; or halt_all to halt at all break points.")
    def __unicode__(self):
        return "%s(%s)" % (self.test_name, self.test_params)
    class Meta:
        ordering = ('suite', 'seq',)


class TestCase(models.Model):
    """
    A TestCase is part of a TestSuite
    A TestCase references a python Test by name and also specifies any optional
    parameters to that test.  Finally the order attribute may be used to specify
    execution ordering of this test case relative to the others within the same test suite.
    Version 2: added
        enabled:     if False, test case will not be copied to TestRun.
        exc_level:   test case execution level:
                     ==0 : qarun abort the combotest if return result is ERROR or FAIL
                     ==1 : qarun looks for next test case exc_level < 2
                     >1  : test cases associate to their upper level 1 tests
                           if they return FAIL/ERROR, qarun looks for next test case with exc_level < 2
        is_cleanup:  if true, test case is a cleanup class.
    SQLITE3 command to add column exc_level:
        alter table RuckusAutoTest_testcase add column exc_level integer default 0;
    """
    suite        = models.ForeignKey(TestSuite)
    test_name    = models.CharField(max_length=60,
                                    help_text="Name of Python class that implements this test")
    test_params  = models.TextField(blank=True,
                                    help_text="Parameters passed to this test as python dictionary string")
    seq        = models.IntegerField(help_text="Relative ordering of this test case within the test suite")
    common_name  = models.CharField(blank=True, max_length=120,
                                    help_text="Common name for this test")
    enabled      = models.BooleanField(default=True,
                                       help_text="Will not copied to TestRun if disabled")
    exc_level    = models.IntegerField(default=0,
                                       help_text="test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR")
    is_cleanup   = models.BooleanField(default=False,
                                       help_text="Is a cleanup test case?")
    def __unicode__(self):
        return "%s(%s)" % (self.test_name, self.test_params)
    class Meta:
        ordering = ('seq',)


class Test(object):
    """
    Base class for all test code.  This does not exists in database (beyond
    a class name reference) as the implementing class itself is the authoratative
    description of a Test.

    required_components is a list of component names that this test case requires.
    parameter_description is a dictionary of parameter names and text descriptions.
    """
    required_components = []
    parameter_description = {}
    def __init__(self, testbed, params={}, carrierbag={}):
        self.testbed = testbed
        self.params = params
        self._carrierbag = carrierbag
    def config(self):
        pass
    def test(self):
        pass
    def cleanup(self):
        pass
    #
    # ComboTest should call returnResult() to return its test result,
    # Example:
    #   return self.returnResult(res, msg)
    #
    def returnResult(self,result, message):
        return {'result':result, 'message':message, 'carrierbag':self._carrierbag}
    #
    # On your test case, you should use the property/variable carrierbag to
    # set/get/del information/data-structure during the ComboTest[a TestSuite]
    #
    # For Example:
    #
    #   self.carrierbag['tc1'] = {'result':'PASS', 'time':200}
    #   ct_wlangroup = self.carrierbag['wg']
    #   del(self.carrierbag['tc2'])
    #
    def getBag(self):
        return self._carrierbag
    def setBag(self, carrierbag):
        self._carrierbag = carrierbag
    def delBag(self):
        self._carrierbag = {}
    carrierbag = property(getBag, setBag, delBag)

class ComponentBase:
    """
    Base class for all testbed components.  This does not exists in database (beyond
    a class name reference)
    """
    component_info = 0  # subclasses should define this as well

    def __init__(self, component_info, config):
        self.component_info = component_info
        self.config = config

    def verify_component(self):
        # Perform sanity check on the component: bare minimum check to
        # make sure test engine can access the component
        # Subclass must implement this function
        raise Exception ("ComponentBase subclass '%s' didn't implement verify_component" % self.component_info.name)


class TestbedBase:
    """
    Base class from which all specific testbed implementations derive.
    This contains the core RAT logic and control loop.
    Ideally this would be the same class as Testbed but currently django
    doesn't support model inheritance.

    See TestLoop() docstring for description of general runtime flow.
    """
    dut = 0           # subclasses should define this to be the primary DUT
    testbed_info = 0  # subclasses should define this as well
    components = {}   # dict mapping component names to component objects

    def __init__(self, testbedinfo, config):
        self.testbed_info = testbedinfo
        self.config = config
        #if not (config.has_key('initlog') and config['initlog'].lower() == 'qa'):
        #    self.initTestbedLogger(testbedinfo.name)
        # self.VerifyTestbed() cannot run VerifyTestbed now since components haven't been initiated.
        self.initComboTest()
        
    def cleanup(self):
        pass

    def initTestbedLogger(self, testbed_name):
        # configure logging to use log file
        log_file = "log_" + testbed_name + "_" + time.strftime("%Y%m%d%H%M") + ".txt"
        logformat = '%(asctime)s %(levelname)-8s %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=logformat,
                            filename=log_file,
                            filemode='w')
        # send log to stdout as well
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(logformat)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        logging.info("[Testbed %s] [Logger started]" % testbed_name)

    def initComboTest(self):
        self._msgbag = dict(result='', message='', carrierbag={})


    def getComboTestResult(self):
        return self._msgbag['result']


    def getComboTestMessage(self):
        return self._msgbag['message']


    def getComboTestMsgBag(self):
        return self._msgbag


    def SetDefaultConfig(self):
        """
        Restore testbed to default config; Implemented in subclass.
        """
        pass


    def VerifyTestbed(self):
        """
        Perform sanity check on testbed components; Must be implemented by subclasses
        """
        pass


    def UpgradeDUT(self, build):
        """
        Upgrade the primary testbed DUT to the specified software build.
        This relies on the DUT class upgrade function to only return after
        the upgrade has successfully completed.
        """
        filename = build.saveLocal()
        self.dut.upgrade_sw(filename)


    def RunComboTest(self, testrun, **kwargs):
        fcfg = dict(tries=1, rerun=0, carrierbag=self._msgbag['carrierbag'])
        fcfg.update(kwargs)
        HALT_IF(testrun.halt_if, "begin_combo")
        return self.RunTest(testrun, **fcfg)


    def RunTest(self, testrun, tries=2, rerun=0, **kwargs):
        """
        Execute the specified testrun, updating the testrun record in the database
        """
        # in case TCID is not available, use the Test Suite name instead
        logid = testrun.suite.name
        try:
            m = re.search("TCID:([0-9.]+).*", testrun.common_name)
            logid = m.group(1)
        except:
            pass

        RatLogger.next_logger(testrun.batch.build.version, logid)
        fcfg = dict(carrierbag={})
        fcfg.update(kwargs)
        HALT_IF(testrun.halt_if, "begin_t_run", bugme.RAT_TRACE_RUNTEST)

        # get Test class by name... gotta love python!
        #testclass = sys.modules['RuckusAutoTest.tests.zd'].__dict__[testrun.test_name].__dict__[testrun.test_name]

        # no need to add testscript class name to __init__.py/__all__ anymore
        # loved python already!
        testclass = __import__('RuckusAutoTest.tests.%s' % testrun.test_name,
                               fromlist=['']).__dict__[testrun.test_name.split('.')[-1]]

        #
        # instantiate the test object and run the test
        testobj = testclass(self, testrun.test_params, fcfg['carrierbag'])
        testrun.start_time = datetime.datetime.now()
        testrun.save()

        # Strip CR & LF from paramater text.
        # This makes it easier to enter nice looking parameters into the database,
        # but it does reclude the use of these characters in the parameter data itself.
        params = testrun.test_params.replace('\n' , '').replace('\r', '')
        logging.info("RunTest (%s) (%s) (ID# %d)" % (testrun.common_name, testrun.test_name, testrun.id))
        test_param = eval(params)

        tc_start_time = time.time()
        if tries < 1: tries = 1
        result = ""
        message = ""
        testResult=dict(result='', message='')
        while tries:
            try:
                set_color_yellow()
                logging.debug("[onConfig] (ID#%d) (%s) (%s) " % (testrun.id, testrun.common_name, testrun.test_name))
                set_color_white()
                HALT_IF(testrun.halt_if, 't_config', bugme.RAT_TRACE_TEST_CONFIG)
                self.touchTestParam(test_param, rerun)
                fix_testrun_test_param(testrun, test_param)
                testobj.config(test_param)
            except Exception, e:
                log_trace()
                result = 'ERROR'
                message = "[OnConfig] %s" % e.message
                testResult = testobj.returnResult(result, message)
                logging.warning(message)
                HALT_IF(testrun.halt_if, "error", bugme.RAT_TRACE_ON_ERROR)
                testobj.cleanup()
                tries = tries - 1
                # Tu Bui: don't need to login ZD page anymore
                #self.gotoZDLoginPage(testobj)
                continue

            try:
                set_color_yellow()
                logging.debug("[onTest] (ID#%d) (%s) (%s) " % (testrun.id, testrun.common_name, testrun.test_name))
                set_color_white()
                HALT_IF(testrun.halt_if, 't_test', bugme.RAT_TRACE_TEST_TEST)
                #result, message = testobj.test()
                testResult = testobj.test()
                if type(testResult) is dict:
                    result, message = testResult['result'], testResult['message']
                    self._msgbag['carrierbag'] = fcfg['carrierbag'] = testResult['carrierbag']
                else:
                    # old format; return value is a tuple of 2 elements
                    result = testResult[0]
                    message = testResult[1]
                    testResult = testobj.returnResult(result, message)
                HALT_IF(testrun.halt_if, "fail|error")
            except Exception, e:
                log_trace()
                result = 'ERROR'
                message = "[OnTest] %s" % e.message
                testResult = testobj.returnResult(result, message)
                logging.warning(message)
                HALT_IF(testrun.halt_if, "error", bugme.RAT_TRACE_ON_ERROR)
                try:
                    testobj.cleanup()
                except Exception, e:
                    log_trace()
                    message = "[OnCleanup] %s" % e.message
                    testResult = testobj.returnResult(result, message)
                    logging.warning(message)
                    HALT_IF(testrun.halt_if, "error")
                tries = tries - 1
                # Tu Bui: don't need to login ZD page anymore
                #self.gotoZDLoginPage(testobj)
                continue

            HALT_IF(testrun.halt_if, "t_cleanup", bugme.RAT_TRACE_TEST_CLEANUP)
            set_color_yellow()
            logging.debug("[onCleanup] (ID#%d) (%s) (%s) " % (testrun.id, testrun.common_name, testrun.test_name))
            set_color_white()
            testobj.cleanup()

            if result == "PASS":
                if testrun.halt_if != "after_t_run" or testrun.halt_if != "":
                    testrun.halt_if = ""
                break
            tries = tries - 1
        if result == "PASS":
            set_color_green()
        else:
            set_color_red()
        HALT_IF(testrun.halt_if, "after_t_run")
        # test complete
        logging.info("RESULT (%s) (%s) (ID# %d): %s, %s" % (testrun.common_name, testrun.test_name, testrun.id, result, message))
        set_color_white()
        testrun.complete = True
        testrun.end_time = datetime.datetime.now()
        #@author: Jane.Guo @since: 2013-09
        testrun.result_type = "RUN"
        testrun.result  = result
        # testrun.message = dbu.text_field_as_struct(testrun.message, message)
        testrun.message = dbu.text_field_as_dict(testrun.message, message, tc_start_time)
        testrun.save()
        if fcfg['carrierbag']:
            self._msgbag['result'], self._msgbag['message'] = result, message
            from RuckusAutoTest.components import ZoneDirector
            from RuckusAutoTest.components import ZoneDirectorCLI
            from RuckusAutoTest.components import RuckusAP
            set_color_yellow()
            msg = ''
            for x in fcfg['carrierbag'].keys():
                if isinstance(fcfg['carrierbag'][x], ZoneDirectorCLI.ZoneDirectorCLI):
                    msg = msg + "%s: %s [IP:%s]" % (x,pformat(fcfg['carrierbag'][x], 4, 120), fcfg['carrierbag'][x].zdcli.ip_addr) + "\n"
                elif isinstance(fcfg['carrierbag'][x], ZoneDirector.ZoneDirector):
                    msg = msg + "%s: %s [IP:%s]" % (x, pformat(fcfg['carrierbag'][x], 4, 120), fcfg['carrierbag'][x].ip_addr) + "\n"
                elif isinstance(fcfg['carrierbag'][x], RuckusAP.RuckusAP):
                    msg = msg + "%s: %s [IP:%s]" % (x, pformat(fcfg['carrierbag'][x], 4, 120), fcfg['carrierbag'][x].ip_addr) + "\n"
                else:
                    msg = msg + "%s: %s" % (x, pformat(fcfg['carrierbag'][x], 4, 120)) + "\n"
            logging.debug("ComboTest CarrierBag:\n%s" % msg)        
            set_color_white()
        return result

    def _bugmeOnResult(self, result):
        if result == "PASS":
            bugme.do_trace(bugme.RAT_TRACE_ON_PASS)
        elif result == 'FAIL':
            bugme.do_trace(bugme.RAT_TRACE_ON_FAIL)
        else:
            bugme.do_trace(bugme.RAT_TRACE_TEST_CLEANUP)


    # test_param is passed by reference
    def touchTestParam(self, test_param, rerun=0):
        """
        change test_param value when rerun RunTest() is re-executed.
        """
        if rerun > 0:
            cs_timeout = test_param['check_status_timeout'] if test_param.has_key('check_status_timeout') else 300
            test_param['check_status_timeout'] = rerun * cs_timeout

    def gotoZDLoginPage(self, testobj):
        try:
            zd = testobj.testbed.components['ZoneDirector']
            if zd.s.is_element_present(zd.info['loc_login_ok_button']):
                return
            zd.goto_login_page()
        except Exception, e:
            logging.debug("Cannot set to ZD's login page: %s" % e.message)

    def ScheduleBatch(self, build, suitelist, email="", priority=0, DUT=0):
        """
        Add a new batch to the queue with the specified parameters.
        """
        if not email:
            email = self.testbed_info.resultdist
        batch = Batch(testbed=self.testbed_info,
                      build=build,
                      seq=priority,
                      timestamp=datetime.datetime.now(),
                      result_email=email,
                      complete=False,
                      DUT=DUT)
        batch.save()
        batch.suites = suitelist.all()
        batch.save()
        logging.info("Scheduled Batch: %s: %s" % (build, batch.suite_list()))


    def BatchCompleteNotify(self, batch):
        """
        Batch complete notification (e.g. email)
        """
        pass
##        if batch.result_email:
##            body = "Your scheduled batch %s has completed.\n\n" % batch
##            body += "Total tests run: %s\nTotal tests passed: %s\n" % (batch.total_tests, batch.tests_pass)
##            body += "Total tests failed: %s\n" % batch.tests_fail
##            # For some reason Outlook wouldn't take the \n that I used, but it would take the double \n.
##            if batch.test_exceptions != "0 (0.00%)":
##                body += "\nExceptions encountered during testing: %s\n" % batch.test_exceptions
##            if batch.test_errors != "0 (0.00%)":
##                body += "\nErrors encountered during testing: %s\n" % batch.test_errors
##            if batch.test_other != "0 (0.00%)":
##                body += "\nOther (non-categorized) test results encountered during testing: %s" % batch.test_other
##            try:
##                Ratutils.send_mail("172.16.100.20", batch.result_email, "RAT <rat@ruckuswireless.com>", "Batch %s complete" % batch, body)
##            except:
##                print "Unable to send mail"

    def BatchNewBuilds(self):
        """
        Check configured build streams for new builds and create batches for any that have new builds available.
        """
        # checking build server for new builds is relatively expensive
        # so never check more than once a minute or so
        BUILD_SERVER_SECONDS = 60
        check_build_server = True
        try:
            if (datetime.datetime.now() - self.lasttime < datetime.timedelta(0, BUILD_SERVER_SECONDS, 0)):
                check_build_server = False
        except:
            pass  # first time through
        self.lasttime = datetime.datetime.now()

        # get AutotestConfigs relevant to this testbed
        configs = AutotestConfig.objects.filter(testbed=self.testbed_info)
        for conf in configs:
            if check_build_server:
                logging.debug("Checking Build Server for build_stream: %s" % conf.build_stream)
                conf.build_stream.CheckNewBuilds()
            # get builds matching this build stream and greater than lastbuildnum
            newbuilds = Build.objects.filter(build_stream=conf.build_stream).filter(number__gt=conf.lastbuildnum)
            for build in newbuilds:
                self.ScheduleBatch(build,
                                   conf.suites,
                                   self.testbed_info.resultdist,
                                   conf.seq,
                                   conf.DUT)
                conf.lastbuildnum = build.number
                conf.save()



    def EnqueueTestsForNextBatch(self):
        """
        Get the next eligible batch (if any) and enqueue all of the individual test cases associated with that batch's test suites.
        """
        # ensure that the run queue is empty before we queue stuff into it
        if TestRun.objects.filter(complete=False).filter(batch__testbed=self.testbed_info).count():
            raise Exception("TestRun queue not empty")

        count = 0
        # get next batch (ordered by 'order' then timestamp in Batch class Meta spec)
        for batch in Batch.objects.filter(testbed=self.testbed_info).filter(complete=False):
            logging.info("Enqueue Batch: %s (ID# %d)" % (batch, batch.id))
            batch.start_time = datetime.datetime.now()
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
                            seq=count).save()
                    count += 1
            logging.info("Queued %d TestRuns" % count)
            if not count:
                logging.info("Empty batch complete")
                batch.complete = True
                batch.end_time = datetime.datetime.now()
                batch.save()
                continue
            else:
                # no need to reset or init logger
                # RatLogger.init_logger(batch.testbed.name)
                # # remove old handler
                # [logging.getLogger('').removeHandler(handler) for handler in logging.getLogger('').handlers
                # if isinstance(handler, logging.FileHandler)]

                # # new handler log_file
                # log_file = "log_%s_%s_%s.txt" % (batch.testbed, batch.build, time.strftime("%Y%m%d%H%M"))
                # fHandlr = logging.FileHandler(log_file)
                # fHandlr.setLevel(logging.DEBUG)
                # logformat = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
                # fHandlr.setFormatter(logformat)
                # logging.getLogger('').addHandler(fHandlr)

                # start new batch: upgrade DUT SW, Verify Testbed, Restore Default Config
                # if Testbed fails to verify and restore config, need manual intervention
                if batch.DUT: # override DUT if DUT is specified at batch level
                    self.dut = self.components[batch.DUT.name]
                try:
                    self.UpgradeDUT(batch.build)
                except Exception: # We can move on if testbed sanity is not violated
                    pass
                try:
                    self.verify_testbed()
                except Exception, e:
                    raise Exception ("New build %s broke testbed sanity because %s" % (batch.build, e.message))
                try:
                    self.SetDefaultConfig()
                except Exception, e:
                    raise Exception ("New build %s failed to set default config because %s" % (batch.build, e.message))
                return count
    # EnqueueTestsForNextBatch

    def TestLoop(self):
        """
        Run incomplete TestRuns if any are present.
        Otherwise, look for new builds and if any are found schedule corresponding Batch.
        """
        batch = 0
        while True:
            # get next eligible test run
            testquery = TestRun.objects.filter(complete=False).filter(batch__testbed=self.testbed_info)
            print "Testbed found %d queued TestRuns." % testquery.count()
            if testquery.count():
                testrun = testquery.order_by('seq')[0]
                self.RunComboTest(testrun)

                if batch:
                    assert(batch == testrun.batch)
                else:
                    batch = testrun.batch
            else:
                if batch:
                    logging.info("Batch %s (ID# %d) COMPLETE." % (batch, batch.id))

                    # Collect Pass/Fail stats
                    testpass = 0
                    testfail = 0
                    testerror = 0
                    testexcept = 0
                    testother = 0
                    totaltests = 0
                    testquery = TestRun.objects.filter(complete=True).filter(start_time__gt=batch.start_time)
                    if testquery.count():
                        for testrun in testquery:
                            # Record test pass/fail based statistics
                            if testrun.result.upper() == "PASS":
                                testpass += 1
                            elif testrun.result.upper() == "FAIL":
                                testfail += 1
                            elif testrun.result.upper() == "ERROR":
                                testerror += 1
                            elif testrun.result.upper() == "EXCEPTION":
                                testexcept += 1
                            else:
                                testother += 1
                            totaltests += 1

                    batch.complete = True
                    batch.end_time = datetime.datetime.now()
                    batch.tests_pass = "%s (%.2f%%)" % (testpass, testpass * 100.0 / totaltests)
                    batch.tests_fail = "%s (%.2f%%)" % (testfail, testfail * 100.0 / totaltests)
                    batch.test_errors = "%s (%.2f%%)" % (testerror, testerror * 100.0 / totaltests)
                    batch.test_exceptions = "%s (%.2f%%)" % (testexcept, testexcept * 100.0 / totaltests)
                    batch.test_other = "%s (%.2f%%)" % (testother, testother * 100.0 / totaltests)
                    batch.total_tests = "%s" % totaltests
                    batch.save()
                    # send notification email
                    self.BatchCompleteNotify(batch)
                    logging.info("Finished batch %s: " % batch)
                    batch = 0

                # Check for new builds
                self.BatchNewBuilds()

                # unleash the next batch
                worktodo = self.EnqueueTestsForNextBatch()
                if not worktodo:
                    time.sleep(1) # catch breath
## end of class TestbedBase

###
### Utility
###
def HALT_IF(target_str, match_str, bugme_str=''):
    tpattern = r"(^|\s+|,|;)\s*(halt_all|%s)\s*(;|,|\s+|$)" % match_str
    if re.search(tpattern, target_str, re.I):
        bugme.pdb.set_trace()
    elif bugme_str:
        bugme.do_trace(bugme_str)


###
### User Exit Functions
###
try:
    _RAT_UserExit['exit.cnt'] += 1
except:
    _RAT_UserExit = {}
    _RAT_UserExit['exit.cnt'] = 1
    try:
        from RuckusAutoTest.userexit import fix_test_param as fixtp
        _RAT_UserExit['fix.testparams'] = getattr(fixtp, 'fix_test_param')
        if _RAT_UserExit.has_key('fix.testparams') and _RAT_UserExit['fix.testparams']:
            if not _RAT_UserExit.has_key('fix.time'):
                _RAT_UserExit['fix.time'] = time.time()
                print '[UserExit] model fix_test_param exists and is loaded at [%s].' % (time.asctime())
        else:
            print '[UserExit] model fix_test_param DOES exist, function ignored at [%s].' % (time.asctime())
    except Exception, e:
        print '[UserExit] model fix_test_param DOES not exist, function ignored at [%s].' % (time.asctime())
        _RAT_UserExit['fix.testparams'] = False

def fix_testrun_test_param(testrun = None, test_param = None):
    if not testrun:
        import pprint
        pprint.pprint(_RAT_UserExit)
        return _RAT_UserExit
    if _RAT_UserExit['fix.testparams']:
        # logging.debug('Fixing test_param of testrun ID=%d' % testrun.id)
        fixtp.fix_test_param(testrun, test_param)
    return test_param

