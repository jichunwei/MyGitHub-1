'''
    Check countries table consistency between ZD and AP.
'''
import logging
import os
import csv

from RuckusAutoTest.models import Test

txt_file = 'C:\\tmp\\countries'
csv_file = 'C:\\tmp\\country-codes.csv'

class CB_ZD_Check_Country_Table(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        try:
            ifile = open(txt_file, "rb")
            tlist = ifile.readlines()
            tlen  = len(tlist)
        except:
            self.errmsg = 'Open and read local file failed'
            return 'FAIL',self.errmsg
        finally:
            ifile.close()
        
        tlist = [tlist[i].strip(',\n') for i in range(tlen)]
#        for i in range(tlen):
#            tlist[i] = tlist[i].strip(',\n')
        
        clist = self.get_colnum_by_value(16, 'TRUE', 2, csv_file)
        clen = len(clist)
        
        if tlen != clen:
            self.errmsg = 'Country code name list length not consistent'
        else:
            for idx in range(tlen):
                if tlist[idx] != clist[idx]:
                    self.errmsg = 'Country code name list member not consistent between countries(%s) and country-codes.csv(%s)' % (tlist[idx], clist[idx])
                    break
                
        if self.errmsg:
            return 'FAIL',self.errmsg
        return "PASS", self.passmsg

    def get_colnum_by_value(self, in_colnum, value, out_colnum, file_name):
        ifile  = open(file_name, "rb")
        reader = csv.reader(ifile)
        
        res_list=[]
        try:
            for row in reader:
                if row[in_colnum-1] == value:
                    res_list.append(row[out_colnum-1])
        except:
            pass
        finally:
            ifile.close()
            return res_list

    def cleanup(self):
        self._update_carrier_bag()

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):
        self.conf={}
        self.conf.update(conf)

        self.errmsg = ''
        self.passmsg = ''
