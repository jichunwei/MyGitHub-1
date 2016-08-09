# coding:utf-8
from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "作者"


class Book(models.Model):
    title = models.CharField(max_length=100 )
    genre = models.CharField(max_length=100)
    num_pages = models.IntegerField()
    # author = models.ForeignKey(Author)
    authors = models.ManyToManyField(Author)  # 多对多

    def __unicode__(self):
        return self.title

    def authors_list(self):
        """return a test list of authors for display purposes"""
        return ','.join([s.__unicode__() for s in self.authors.all()])  # 返回作者列表

    class Meta:  # Meta 类处理的是关于模型的各种元数据的使用和显示
        # abstract = True  # 指明了Book 是一个抽象基础类，只是用来为他实际的模型子类提供属性而存在的
        ordering = ['title']  # 排序
        verbose_name_plural = '书籍'


class SmithBook(Book):
    author = models.ForeignKey(Author, limit_choices_to={'name_endswith': 'Smith'})
    # authors = models.ManyToManyField(Author)  # 多对多

    class Meta:
        verbose_name_plural = '史密斯的书'


class Person(models.Model):
    first = models.CharField(max_length=100)
    last = models.CharField(max_length=100)
    middle = models.CharField(max_length=100)

    class Meta:
        ordering = ['last', 'first', 'middle']
        unique_together = ['first', 'last', 'middle']
        verbose_name_plural = '人'


'''

class Book(models.Model):
    title = models.CharField(max_length=100)

    authors = models.ManyToManyField(Author, through='Authoring')  # 多对多

    def __unicode__(self):
        return self.title

    def authors_list(self):
        """return a test list of authors for display purposes"""
        return ','.join([s.__unicode__() for s in self.authors.all()])  # 返回作者列表


class Authoring(models.Model):
    c_type = models.CharField(max_length=100)
    book = models.ForeignKey(Book)
    author = models.ForeignKey(Author)
'''
