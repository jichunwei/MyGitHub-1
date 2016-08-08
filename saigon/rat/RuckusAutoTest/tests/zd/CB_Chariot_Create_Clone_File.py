'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.common import chariot


class CB_Chariot_Create_Clone_File(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._makeCloneFile()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.endpoint_pair_list = conf['endpoint_pair_list']
        for i in range(len(self.endpoint_pair_list)):
            if not self.endpoint_pair_list[i].has_key('endpoint2_ip'):
                endpoint2_ip = self.carrierbag[self.endpoint_pair_list[i]['sta_tag']]['wifi_ip_addr']
                self.endpoint_pair_list[i]['endpoint2_ip'] = endpoint2_ip
            
        self.output_filename = conf['output_filename']
        self.errmsg = ''
        self.passmsg = ''

    def _makeCloneFile(self):
        try:
            chariot.create_clone_file(self.endpoint_pair_list, self.output_filename)
            self.passmsg = "Create chariot clone file: %s successfully" % self.output_filename
            
        except Exception, e:
            self.errmsg = e.message
            
            
            