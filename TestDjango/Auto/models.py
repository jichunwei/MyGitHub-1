from __future__ import unicode_literals

from django.db import models


# Create your models here.
class TestbedType(models.Model):
    """
    TestbedType models a class of testbeds that generally share the same topology, component types, and purpose.
    """
    name = models.CharField(unique=True, max_length=50,
                            help_text='The name of the python class that implements this type of testbed')
    description = models.TextField(blank=True,
                                   help_text="Description of this testbed and description of all configuration parameters")

    # diagram      = models.ImageField(blank=True, upload_to='\\\\192.168.10.2\\rat',
    #                                  help_text="Upload topology for this type of test bed. Support only .JPG, .PNG")
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
    name = models.CharField(unique=True, max_length=50,
                            help_text='Unique name for this physical testbed')
    tbtype = models.ForeignKey(TestbedType)
    location = models.CharField(max_length=100)
    owner = models.EmailField("Owner Email",
                              help_text='Address for reporting testbed problems.')
    resultdist = models.EmailField("Results Email",
                                   help_text='Default address for emailing batch results')
    description = models.TextField(blank=True)
    config = models.TextField(blank=True,
                              help_text='Basic testbed configuration parameters (e.g. DUT IP address) as a python dictionary string')

    def __unicode__(self):
        return self.name


class TestbedComponent(models.Model):
    """
    A physical component of a testbed such as an AP, Laptop, PC, attenuator, etc.
    Classes defined elsewhere implement the interface to config/control the testbed components.
    Test code uses these testbed component interfaces to configure and control the testbed.
    (Ideally those component classes would derive directly from this TestbedComponent base class
    but django doesn't currently allow that...)
    """
    name = models.CharField(unique=True, max_length=30,
                            help_text='Name of this component and the python class that implements it')
    description = models.TextField(blank=True, help_text='Description of this component.')
    config = models.TextField(blank=True,
                              help_text='Basic testbed component configuration parameters (e.g. DUT IP address) as a python dictionary string')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class BuildStream(models.Model):
    """
    The BuildStream class models a set of related builds from a build server.
    It really corresponds to the combination of a build tree from source control plus
    build configuration (e.g. a build profile). The BuildStream class is responsible for
    creating new Build objects as they become available on the build server.
    """
    name = models.CharField(max_length=60,
                            unique=True,
                            help_text="Verbose name for this build stream,(e.g. AP2825_4.2.0_production)")
    prefix = models.CharField(max_length=22,
                              help_text="Short version prefix for this stream (e.g. 4.2.0). Combined with build number to make build name.")
    URL = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class Build(models.Model):
    """
    A unique software image that can be loaded onto a device under test.
    Each build is associated with BuildStream and has a characteristic build number and label.
    """
    build_stream = models.ForeignKey(BuildStream)
    number = models.IntegerField(help_text="Build number within a build stream.")
    builder = models.CharField(max_length=20, blank=True,
                               help_text="Build creator")
    version = models.CharField(max_length=20,
                               help_text="short name for this build (e.g. 4.2.0.171)")
    label = models.CharField(unique=True, max_length=64,
                             help_text="verbose build label (e.g. lnxbuild_ap_ap2825420_20080116_540p_chg18762_171)")
    timestamp = models.DateTimeField(help_text="Build Start time")
    URL = models.URLField()

    def __unicode__(self):
        return "%s" % (self.version)

    class Meta:
        ordering = ['number']


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
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    config = models.TextField(blank=True,
                              help_text="Text dictionary of testbed component configs to use for this test suite")
    xtype = models.CharField(blank=True, max_length=8,
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
    suite = models.ForeignKey(TestSuite)
    test_name = models.CharField(max_length=60,
                                 help_text="Name of Python class that implements this test")
    test_params = models.TextField(blank=True,
                                   help_text="Parameters passed to this test as python dictionary string")
    seq = models.IntegerField(help_text="Relative ordering of this test case within the test suite")
    common_name = models.CharField(blank=True, max_length=120,
                                   help_text="Common name for this test")
    enabled = models.BooleanField(default=True,
                                  help_text="Will not copied to TestRun if disabled")
    exc_level = models.IntegerField(default=0,
                                    help_text="test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR")
    is_cleanup = models.BooleanField(default=False,
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
    def returnResult(self, result, message):
        return {'result': result, 'message': message, 'carrierbag': self._carrierbag}

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


class Batch(models.Model):
    """
    Batch objects are used to schedule and track test suite runs and (eventually) group test results for reporting purposes.
    """
    testbed = models.ForeignKey(Testbed,
                                help_text="Testbed to which this batch belongs")
    build = models.ForeignKey(Build,
                              help_text="DUT software build for this test batch")
    suites = models.ManyToManyField(TestSuite,
                                    help_text="list of test suites to run for this batch",
                                    )
    seq = models.IntegerField(default=0, help_text="Relative ordering of different batches")
    timestamp = models.DateTimeField(help_text="Time that this batch was first scheduled.")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    result_email = models.EmailField(blank=True,
                                     help_text="Email address for batch result report")
    complete = models.BooleanField(default=False, help_text="True if batch has finished running.")
    DUT = models.ForeignKey(TestbedComponent, blank=True, null=True,
                            help_text="The testbed component under test (if testbed has multiple potential DUTS)")
    total_tests = models.CharField(max_length=15, blank=True)
    tests_pass = models.CharField(max_length=15, blank=True)
    tests_fail = models.CharField(max_length=15, blank=True)
    test_errors = models.CharField(max_length=15, blank=True,
                                   help_text="Errors encountered that prevented test from completing")
    tests_skip = models.CharField(max_length=15, blank=True,
                                  help_text="Tests skipped by test runner because testrun's skip_run is true.")
    test_exceptions = models.CharField(max_length=15, blank=True,
                                       help_text="Script errors encountered that prevented test from completing")
    test_other = models.CharField(max_length=15, blank=True, help_text="Other non-categorized test results")

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
    batch = models.ForeignKey(Batch)
    suite = models.ForeignKey(TestSuite)
    test_name = models.CharField(max_length=80)
    test_params = models.TextField(blank=True)
    common_name = models.CharField(blank=True, max_length=120)
    run_name = models.CharField(blank=True, max_length=120)
    config = models.TextField(blank=True,
                              help_text="Text dictionary of testbed component configs to use for this test case")
    complete = models.BooleanField()
    seq = models.IntegerField()
    exc_level = models.IntegerField(default=0,
                                    help_text="test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR")
    is_cleanup = models.BooleanField(default=False,
                                     help_text="Is a cleanup test case?")
    skip_run = models.BooleanField(default=False,
                                   help_text="Enable to skip this test during execution.")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    result = models.CharField(max_length=100, blank=True,
                              help_text='short result string. Format of this string is specified by result_type')
    result_type = models.CharField(max_length=30, blank=True,
                                   help_text='Type of result: passfail, numeric, etc')
    message = models.TextField(blank=True)
    halt_if = models.CharField(max_length=100, blank=True,
                               help_text="keyword list of: begin_combo,begin_t_run,pass,fail,error,t_config,t_test,t_cleanup,after_t_run; or halt_all to halt at all break points.")

    def __unicode__(self):
        return "%s(%s)" % (self.test_name, self.test_params)

    class Meta:
        ordering = ('suite', 'seq',)


class AutotestConfig(models.Model):
    """
    This class is used to configure a testbed.
    It is used to specify what test suites are automatically run against
    new Builds from a particular BuildStream.
    """
    testbed = models.ForeignKey(Testbed)
    build_stream = models.ForeignKey(BuildStream)
    suites = models.ManyToManyField(TestSuite, null=True,
                                    help_text="list of test suites to run for this batch",
                                    )
    lastbuildnum = models.IntegerField(default=0,
                                       help_text="Last build number autotested; Only test new builds greater than this.")
    seq = models.IntegerField(default=0,
                              help_text="Specifies priority of this build_stream if multiple build streams have new builds available")
    DUT = models.ForeignKey(TestbedComponent, blank=True, null=True,
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
