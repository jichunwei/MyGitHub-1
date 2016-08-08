'''
Created on 2011-5-30
@author: cwang@ruckuswireless.com
'''
from datetime import datetime
from django.db import models
from django.utils.html import strip_tags

from RuckusAutoTest.models import (
    Batch as RatBatch,
    TestCase as RatTestCase,
    TestRun as RatTestRun,
)

class TestProject(models.Model):
    """
    tlc22.get_pproject_by_name(project_name)
    tlc22.get_plan_by_name(project_name, plan_name)
    """

    tms_zone = models.CharField(
        "Test Management System",
        max_length = 4,
        default = 'TMS',
        help_text = "Zone of different Test-Management-System. "\
                    "Default is qa-tms.tw.video54.local.",
    )

    project_id = models.IntegerField(
        "Testlink Test Project's ID",
        default = 0,
        help_text = "XMLRPC API header attr: testprojectid",
    )

    project_name = models.CharField(
        "Testlink Test Project's Name",
        unique = True,
        max_length = 72,
        blank = "Zone Director",
        help_text = "XMLRPC API header attr: testprojectname",
    )

    create_ts = models.DateTimeField(
        "Creation Timestamp",
        auto_now = True
    )

    modified_ts = models.DateTimeField(
        "Modification Timestamp",
        null = True
    )


    def __unicode__(self):
        return ("%s %s{%s}" % (self.tms_zone, self.project_name, str(self.project_id),))


    def save(self, *args, **kwargs):
        self.modified_ts = datetime.now()
        super(TestProject, self).save(*args, **kwargs)


    class Meta:
        unique_together = (('tms_zone', 'project_id', 'project_name'),)

class TestPlan(models.Model):
    """
    tlc22.get_plan_by_name(project_name, plan_name)
    """

    project = models.ForeignKey(
        TestProject,
        verbose_name = "Test Project"
    )

    plan_id = models.IntegerField(
        "Testlink Test Plan's ID",
        default = 0,
        help_text = "XMLRPC API header attr: testplanid",
    )

    plan_name = models.CharField(
        "Testlink Test Plan's Name",
        max_length = 72,
        blank = True,
        help_text = "XMLRPC API header attr: testplanname",
    )

    create_ts = models.DateTimeField(
        "Creation Timestamp",
        auto_now = True
    )

    modified_ts = models.DateTimeField(
        "Modification Timestamp",
        null = True
    )


    def __unicode__(self):
        return ("%s{%s %s}"
                % (self.plan_name, str(self.plan_id), str(self.project.project_id),)
                )


    def save(self, *args, **kwargs):
        self.modified_ts = datetime.now()
        super(TestPlan, self).save(*args, **kwargs)


    class Meta:
        unique_together = (('project', 'plan_name', 'plan_id'),)

class TestBuild(models.Model):
    """
    Batch@RAT maps to Plan+Build@Testlink.
    tlc22.get_builds(plan_id)
    tlc22.get_builds_by_plan_name(project_name, plan_name)    
    """

    plan = models.ForeignKey(
        TestPlan,
        verbose_name = "Test Plan",
    )

    batch = models.ForeignKey(
        RatBatch,
        null = True,
        verbose_name = "RuckusAutoTest Batch",
    )

    build_id = models.IntegerField(
        "Testlink Build's ID",
        default = 0,
        help_text = "XMLRPC API header attr: buildid",
    )

    build_name = models.CharField(
        "Testlink Build's ID",
        max_length = 72,
        blank = True,
        help_text = "XMLRPC API header attr: buildname",
    )

    create_ts = models.DateTimeField(
        "Creation Timestamp",
        auto_now = True,
    )

    modified_ts = models.DateTimeField(
        "Modification Timestamp",
        null = True,
    )

    start_ts = models.DateTimeField(
        "Start Timestamp",
        null = True,
    )

    end_ts = models.DateTimeField(
        "End Timestamp",
        null = True,
    )

    #run_seconds = models.BigIntegerField(
    run_seconds = models.IntegerField(
        "Reporting seconds",
        default = 0,
        help_text = "Seconds spent on reporting this batch to TL.",
    )


    def d_title(self):
        return ("%s{%s} on plan:'%s'{%s} on project:'%s'{%s}"
                % (self.build_name, str(self.build_id),
                   self.plan.plan_name, str(self.plan.plan_id),
                   self.plan.project_name, str(self.plan.project_id,)
                   )
                )


    def __unicode__(self):
        return ("%s{%s %s %s}"
                % (self.build_name, str(self.build_id),
                   str(self.plan.plan_id), str(self.plan.project.project_id)
                   )
                )


    def save(self, *args, **kwargs):
        self.modified_ts = datetime.now()
        super(TestBuild, self).save(*args, **kwargs)
        

# Testlink test_project's test_cases mapping to RAT TestCase
# A test case in Testlink is assigned an external_id when it is created.
# The external_id is call internalid when exported to XML file.
#
# We will use this table for RAT test case to locate its external_id.
# There is no xmlrpc method to get a project's test cases, so we
# will update this table when tests being assigned to PlanTestCase table.

class ProjectTestCase(models.Model):
    """
    SQL Statements to be generated by Django against 'sqlite3' DB Engine
    python manage.py sql Testlink
    """
    project = models.ForeignKey(
        TestProject,
        verbose_name = "Test Project",
    )

    external_id = models.IntegerField(
        default = 0,
    )

    version = models.IntegerField(
        default = 1,
    )

    rattestcase = models.ForeignKey(
        RatTestCase,
        null = True,
        verbose_name = "RuckusAutoTest TestCase"
    )

    project_name = models.CharField(
        "Project Name",
        null = True,
        max_length = 120,
    )

    suite_name = models.CharField(
        null = True,
        max_length = 120,
    )

    common_name = models.CharField(
        null = True,
        max_length = 120,
    )

    suite_path = models.TextField(
        blank = True,
        help_text = "python list of tc's full path in Testlink's test project, "\
                    "excluding TC's parent test suite name.",
    )

    create_ts = models.DateTimeField(
        "Creation Timestamp",
        auto_now = True,
    )

    modified_ts = models.DateTimeField(
        "Modification Timestamp",
        null = True,
    )


    def save(self, *args, **kwargs):
        self.modified_ts = datetime.now()
        super(ProjectTestCase, self).save(*args, **kwargs)


    def __unicode__(self):
        return ("XID-%s: %s"
                % (str(self.external_id), str(self.common_name))
                )


    class Meta:
        unique_together = (('project', 'external_id', 'version'),)



class PlanTestCase(models.Model):
    """
    Test Cases assigned to TestPlan.
    This is mapped from get_assigned_tcinfo_brief().
    tc_tree_path = [project_name, suite_path, common_name]
    """

    plan = models.ForeignKey(
        TestPlan,
        verbose_name = "Test Plan",
    )

    testcase = models.ForeignKey(
        ProjectTestCase,
        verbose_name = "Project TestCase",
    )

    tc_id = models.IntegerField(
        default = 0,
    )

    version = models.IntegerField(
        default = 0,
    )

    tcv_id = models.IntegerField(
        default = 0,
    )

    is_open = models.IntegerField(
        default = 0,
    )

    active = models.IntegerField(
        default = 0,
    )

    create_ts = models.DateTimeField(
        "Creation Timestamp",
        auto_now = True,
    )

    modified_ts = models.DateTimeField(
        "Modification Timestamp",
        null = True,
    )


    def save(self, *args, **kwargs):
        self.modified_ts = datetime.now()
        super(PlanTestCase, self).save(*args, **kwargs)


    def __unicode__(self):
        return ("TCID[%s %s]: %s"
                % (str(self.tc_id), str(self.version), self.testcase)
                )


    class Meta:
        unique_together = (('plan', 'testcase'),)

class TestRunMap(models.Model):
    """
    SQL Statements to be generated by Django against 'sqlite3' DB Engine
    python manage.py sql Testlink
    """
    testrun = models.ForeignKey(
        RatTestRun,
        verbose_name = "RuckusAutoTest TestRun",
    )

    plantestcase = models.ForeignKey(
        PlanTestCase,
        verbose_name = "Plan TestCase",
    )


    def get_testrun_common_name(self):
        return self.testrun.common_name


    def get_testrun_id(self):
        return self.testrun.id


    def get_testrun_result(self):
        return 'p' if self.testrun.result == 'PASS' else 'f'


    def get_testrun_message(self):
        return self.testrun.message


    def get_testrun_lastest_message(self):
        msgs = self.get_testrun_message()
        if not type(msgs) is dict:
            return strip_tags(msgs)

        lastest_timerun = max(msgs.keys())
        return strip_tags(msgs[lastest_timerun][1])


    def get_plantestcase_tc_id(self):
        return self.plantestcase.tc_id if self.plantestcase else ''


    def get_plantestcase_plan_id(self):
        return self.plantestcase.plan.plan_id if self.plantestcase else ''


    def get_plantestcase_plan_name(self):
        return self.plantestcase.plan.plan_name if self.plantestcase else ''


    def get_plantestcase_version(self):
        return self.plantestcase.plan.version if self.plantestcase else ''


    def get_plantestcase_common_name(self):
        return self.plantestcase.testcase.common_name if self.plantestcase else ''


    def get_testbuild(self):
        all_builds = TestBuild.objects.all()
        for build in all_builds:
            if build.build_name == self.testrun.batch.build.version \
            and build.plan.plan_name == self.plantestcase.plan.plan_name:
                return build

        return None


    def get_testbuild_build_id(self):
        build = self.get_testbuild()
        return build.build_id if build else ''


    def get_testbuild_build_name(self):
        build = self.get_testbuild()
        return build.build_name if build else ''


    get_testbuild_build_name.short_description = 'Build'

    get_testrun_common_name.short_description = 'Common name'

    get_testrun_id.short_description = 'Testrun ID'

    get_testrun_result.short_description = 'Result'

    get_plantestcase_plan_name.short_description = 'Test Plan'

    get_plantestcase_tc_id.short_description = 'Plan TCID'


    def save(self, *args, **kwargs):
        self.testrun.help_text = 'Common name: %s' % self.get_testrun_common_name()
        if self.plantestcase:
            self.plantestcase.help_text = 'Common name: %s' % self.get_plantestcase_common_name()

        super(TestRunMap, self).save(*args, **kwargs)


    def __unicode__(self):
        return ("Rat test run ID[%s] - Map to Testlinks plan test case ID [%s]" %
                (self.get_testrun_id(), self.get_plantestcase_tc_id())
                )


    class Meta:
        unique_together = (('testrun', 'plantestcase'),)



class Execution(models.Model):
    """
    Execution from Testlink execution table
    """

    testrunmap = models.ForeignKey(
        TestRunMap,
        verbose_name = "TestRun Map",
    )

    exec_id = models.IntegerField(
        "Testlink Execution's ID",
        default = 0,
        help_text = "XMLRPC API header attr: executionid",
    )

    status = models.CharField(
        max_length = 2,
    )

    execution_ts = models.DateTimeField(
        "Execution Timestamp",
        null = True,
    )

    tcversion_id = models.IntegerField(
        default = 0,
    )

    tcversion_number = models.IntegerField(
        default = 0,
    )

    notes = models.TextField(
        blank = True,
    )


    def save(self, *args, **kwargs):
        '''
        '''
        super(Execution, self).save(*args, **kwargs)


    def get_testrun_id(self):
        return self.testrunmap.get_testrun_id()


    def get_plantestcase_tc_id(self):
        return self.testrunmap.get_plantestcase_tc_id()


    def get_testbuild_build_id(self):
        return self.testrunmap.get_testbuild_build_id()


    def get_testbuild_build_name(self):
        return self.testrunmap.get_testbuild_build_name()


    def get_plantestcase_plan_id(self):
        return self.testrunmap.get_plantestcase_plan_id()


    def get_plantestcase_plan_name(self):
        return self.testrunmap.get_plantestcase_plan_name()


    get_testrun_id.short_description = 'Testrun ID'

    get_plantestcase_tc_id.short_description = 'TCID'

    get_testbuild_build_name.short_description = 'Build'

    get_testbuild_build_id.short_description = 'Build ID'

    get_plantestcase_plan_id.short_description = 'Test Plan ID'

    get_plantestcase_plan_name.short_description = 'Test Plan'


    def __unicode__(self):
        return ("[exec_id=%s; status=%s; tc_id=%s] of plan: [%s]"
                % (str(self.exec_id), str(self.status),
                   str(self.get_plantestcase_tc_id()),
                   self.get_plantestcase_plan_name(),
                   )
                )
        
