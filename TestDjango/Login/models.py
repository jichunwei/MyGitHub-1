# coding:utf-8

from __future__ import unicode_literals

from django.db import models


# Create your models here.
class TestSuite(models.Model):
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
                             help_text="execution type of this test suite. Default is regression test.")

    def asComboTest(self):
        self.xtype = self.TS_COMBO

    def is_combo_test(self):
        return self.xtype == self.TS_COMBO

    def num_tests(self):
        return TestCase.objects.filter(suite=self).count()

    def __unicode__(self):
        return "%s" % (self.name)


class TestCase(models.Model):
    suite = models.ForeignKey(TestSuite)
    test_name = models.CharField(max_length=60,
                                 help_text="测试用例的名字")
    test_params = models.TextField(blank=True,
                                   help_text="测试传递的参数，用户名和密码")
    seq = models.IntegerField(help_text="Relative ordering of this test case within the test suite")
    # 一个完整测试用例的名字
    common_name = models.CharField(blank=True, max_length=120,
                                   help_text="Common name for this test")
    enabled = models.BooleanField(default=True,
                                  help_text="Will not copied to TestRun if disabled")
    exc_level = models.IntegerField(default=0,
                                    help_text="test case execution level. Test runner, "
                                              "qarun uses it to decide what to do if this test FAIL/ERROR")
    is_cleanup = models.BooleanField(default=False,
                                     help_text="Is a cleanup test case?")

    def __unicode__(self):
        return "%s(%s)" % (self.test_name, self.test_params)

    class Meta:
        ordering = ('seq',)
