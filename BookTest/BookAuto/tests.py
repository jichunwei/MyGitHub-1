# coding:utf-8
import os
import  django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BookTest.settings")
django.setup()

from django.test import TestCase
from BookAuto.models import *

# Create your tests here.

# import  pdb
# pdb.set_trace()

book = Book.objects.get(title='Book_A')
st = Book.objects.filter(title='BOOK_C') #查询有没有这本书, 有就返回这本书
print st
authors = book.authors.all()   #查询书的所有作者
print 'type(author) is %r' % authors


print book
# print authors


