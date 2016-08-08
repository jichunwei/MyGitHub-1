'''
Testsuite
1.1.10.2 Administration - Users
1.1.10.2.4 Create many user(over 100 user account)


MODELING FOR NORMAL CASES
-------------------------
Inputs
- totalUsers

Internal Variables
- name_prefix: likes 'user_'

Expected Results
- able to create more than a hundred of users


Testscript
+ Config:
  - Initialize the input config
  - Delete all current (delete-able) users

+ Test:
  - Create users (by the given totalUsers)
  - Go through the list make sure the created users are there

+ Clean up:
  - Delete all the users
'''

import os, time, logging, re, random
from datetime import *
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.fm.lib_FM import *


class FM_ManageUsers(Test):
    required_components=['FM', 'APs']
    parameter_description = dict(
        totalUsers = '',
    )


    def config(self, conf):
        self.errmsg = None
        self.aliases = init_aliases(testbed=self.testbed)

        self._cfgTestParams(**conf)
        logging.info('Delete all delete-able users')
        lib.fm.userMgmt.delete_all_users(self.aliases.fm)


    def test(self):
        self._create_users()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testCreatedUsers()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        logging.info('Delete all delete-able users')
        lib.fm.userMgmt.delete_all_users(self.aliases.fm)
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = dict(
            totalUsers = 11,
            prefix = 'user',
            roles = ['Network Administrator', 'Group Administrator',
                     'Group Operator', 'Device Operator'],
        )
        self.p.update(kwa)
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _generateUsers(self, **kwa):
        '''
        kwa:
        - prefix
        - total
        - roles
        return:
        - something likes 'user_015'
        '''
        role_len = int(kwa['total'] / len(kwa['roles']))
        for i in range(1, kwa['total'] + 1):
            role_idx = int(i/role_len)
            if role_idx >= len(kwa['roles']):
                role_idx = len(kwa['roles']) - 1
            yield '%s_%03i' % (kwa['prefix'], i), kwa['roles'][role_idx]


    def _create_users(self):
        '''
        return:
        . self.accounts: a list of (name, role)
        '''
        self.accounts = []
        logging.info('Creating Users: prefix=%s, totalUsers=%s' % \
                     (self.p['prefix'], self.p['totalUsers']))
        for name, role in self._generateUsers(prefix=self.p['prefix'],
                                              total=self.p['totalUsers'],
                                              roles=self.p['roles']):
            self.accounts.append((name, role))
            lib.fm.userMgmt.add_user(self.aliases.fm,
                                       username=name,
                                       password=name,
                                       role=role)


    def _testCreatedUsers(self):
        logging.info('Test the list of created users')
        allAccs = lib.fm.userMgmt.get_all_users(self.aliases.fm)
        for a in self.accounts:
            if not self._find_user(user=a, list=allAccs):
                self.errmsg = 'User created but not found: (name=%s, role=%s)' % a
                return


    def _find_user(self, **kwa):
        '''
        kwa:
        - user: (name, role)
        - list: the list of users from FM Users table
        '''
        for i in kwa['list']:
            if i['username'] == kwa['user'][0]:
                if i['userrole'] == kwa['user'][1]:
                    return True
                return False # same user name, but different role
        return False
