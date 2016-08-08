'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to edit the user in ZD GUI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import user


class CB_ZD_Edit_User(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._editUser()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.oldname = conf['old_name']
        self.cfg = conf['cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _editUser(self):
        try:
            user.edit_user(self.zd, self.oldname, self.cfg)
            self.passmsg = 'Edit user [%s] successfully!' % self.oldname
            
        except Exception, ex:
            self.errmsg = ex.message
            
     