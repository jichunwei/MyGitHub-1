# coding:utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Type(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = '问题类别'


class Issue(models.Model):
    seq = models.CharField(max_length=10, unique=None)
    title = models.CharField(max_length=100,
                             help_text="please enter you Issue title")

    description = models.TextField(blank=True, help_text="enter you issue discription")
    type = models.ForeignKey(Type)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = "问题描述"
        ordering = ['title']  # 排序


class Solve(models.Model):
    # title = models.CharField("主题",max_length=100)
    name = models.ForeignKey(Issue)
    result = models.TextField(blank=True,
                              help_text="Here write you solve method of this problem")
    type = models.ForeignKey(Type)


    WJJ = '0'
    YJJ = '1'
    select = (
        (WJJ, 'unslove'),
        (YJJ, 'solve'),
    )
    xtype = models.CharField(max_length=100, choices=select,
                             blank=True, help_text="解决/未解决")


    class Meta:
        verbose_name_plural = "解决方法"

#
# class Status(models.Model):
#     WJJ = '0'
#     YJJ = '1'
#     SUITE_TYPES = (
#         (WJJ, 'unslove'),
#         (YJJ, 'solve'),
#     )
#

