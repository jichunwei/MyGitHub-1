# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-11 16:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Auto', '0002_testbedcomponent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seq', models.IntegerField(default=0, help_text='Relative ordering of different batches')),
                ('timestamp', models.DateTimeField(help_text='Time that this batch was first scheduled.')),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('result_email', models.EmailField(blank=True, help_text='Email address for batch result report', max_length=254)),
                ('complete', models.BooleanField(default=False, help_text='True if batch has finished running.')),
                ('total_tests', models.CharField(blank=True, max_length=15)),
                ('tests_pass', models.CharField(blank=True, max_length=15)),
                ('tests_fail', models.CharField(blank=True, max_length=15)),
                ('test_errors', models.CharField(blank=True, help_text='Errors encountered that prevented test from completing', max_length=15)),
                ('tests_skip', models.CharField(blank=True, help_text="Tests skipped by test runner because testrun's skip_run is true.", max_length=15)),
                ('test_exceptions', models.CharField(blank=True, help_text='Script errors encountered that prevented test from completing', max_length=15)),
                ('test_other', models.CharField(blank=True, help_text='Other non-categorized test results', max_length=15)),
                ('DUT', models.ForeignKey(blank=True, help_text='The testbed component under test (if testbed has multiple potential DUTS)', null=True, on_delete=django.db.models.deletion.CASCADE, to='Auto.TestbedComponent')),
            ],
            options={
                'ordering': ('seq', 'timestamp'),
            },
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(help_text='Build number within a build stream.')),
                ('builder', models.CharField(blank=True, help_text='Build creator', max_length=20)),
                ('version', models.CharField(help_text='short name for this build (e.g. 4.2.0.171)', max_length=20)),
                ('label', models.CharField(help_text='verbose build label (e.g. lnxbuild_ap_ap2825420_20080116_540p_chg18762_171)', max_length=64, unique=True)),
                ('timestamp', models.DateTimeField(help_text='Build Start time')),
                ('URL', models.URLField()),
            ],
            options={
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='BuildStream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Verbose name for this build stream,(e.g. AP2825_4.2.0_production)', max_length=60, unique=True)),
                ('prefix', models.CharField(help_text='Short version prefix for this stream (e.g. 4.2.0). Combined with build number to make build name.', max_length=22)),
                ('URL', models.URLField(blank=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(help_text='Name of Python class that implements this test', max_length=60)),
                ('test_params', models.TextField(blank=True, help_text='Parameters passed to this test as python dictionary string')),
                ('seq', models.IntegerField(help_text='Relative ordering of this test case within the test suite')),
                ('common_name', models.CharField(blank=True, help_text='Common name for this test', max_length=120)),
                ('enabled', models.BooleanField(default=True, help_text='Will not copied to TestRun if disabled')),
                ('exc_level', models.IntegerField(default=0, help_text='test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR')),
                ('is_cleanup', models.BooleanField(default=False, help_text='Is a cleanup test case?')),
            ],
            options={
                'ordering': ('seq',),
            },
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=80)),
                ('test_params', models.TextField(blank=True)),
                ('common_name', models.CharField(blank=True, max_length=120)),
                ('run_name', models.CharField(blank=True, max_length=120)),
                ('config', models.TextField(blank=True, help_text='Text dictionary of testbed component configs to use for this test case')),
                ('complete', models.BooleanField()),
                ('seq', models.IntegerField()),
                ('exc_level', models.IntegerField(default=0, help_text='test case execution level. Test runner, qarun uses it to decide what to do if this test FAIL/ERROR')),
                ('is_cleanup', models.BooleanField(default=False, help_text='Is a cleanup test case?')),
                ('skip_run', models.BooleanField(default=False, help_text='Enable to skip this test during execution.')),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('result', models.CharField(blank=True, help_text='short result string. Format of this string is specified by result_type', max_length=100)),
                ('result_type', models.CharField(blank=True, help_text='Type of result: passfail, numeric, etc', max_length=30)),
                ('message', models.TextField(blank=True)),
                ('halt_if', models.CharField(blank=True, help_text='keyword list of: begin_combo,begin_t_run,pass,fail,error,t_config,t_test,t_cleanup,after_t_run; or halt_all to halt at all break points.', max_length=100)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auto.Batch')),
            ],
            options={
                'ordering': ('suite', 'seq'),
            },
        ),
        migrations.CreateModel(
            name='TestSuite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('config', models.TextField(blank=True, help_text='Text dictionary of testbed component configs to use for this test suite')),
                ('xtype', models.CharField(blank=True, choices=[('', 'Regression Tests'), ('combo', 'Combination/Composition Tests')], help_text='eXecution type of this test suite. Default is regression test.', max_length=8)),
            ],
        ),
        migrations.AddField(
            model_name='testrun',
            name='suite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auto.TestSuite'),
        ),
        migrations.AddField(
            model_name='testcase',
            name='suite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auto.TestSuite'),
        ),
        migrations.AddField(
            model_name='build',
            name='build_stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auto.BuildStream'),
        ),
        migrations.AddField(
            model_name='batch',
            name='build',
            field=models.ForeignKey(help_text='DUT software build for this test batch', on_delete=django.db.models.deletion.CASCADE, to='Auto.Build'),
        ),
        migrations.AddField(
            model_name='batch',
            name='suites',
            field=models.ManyToManyField(help_text='list of test suites to run for this batch', to='Auto.TestSuite'),
        ),
        migrations.AddField(
            model_name='batch',
            name='testbed',
            field=models.ForeignKey(help_text='Testbed to which this batch belongs', on_delete=django.db.models.deletion.CASCADE, to='Auto.Testbed'),
        ),
    ]