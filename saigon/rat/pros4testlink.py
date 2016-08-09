'''
Settings for RAT-Testlink integration
'''
import os

TESTLINK_CLIENT_PATH = 'C:/rwqaauto/testlink/addon/report'
if os.environ.has_key('TESTLINK_CLIENT'):
    TESTLINK_CLIENT_PATH = os.environ['TESTLINK_CLIENT']

SERVER_URL = 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php'
DEV_KEY = '1846dc07e03200607115fb108183c1d9' #Jacky's

PROJECT = 'Zone Director'
PLAN = 'Toronto 9.1'
BUILD = '9.1.0.0.38'
