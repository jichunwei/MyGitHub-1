# 
#Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Functional testing for 'create new map' option of the Zone Director.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
            - option: which 'multi' to create multiple maps.
                            'diff' to create maps using different formats.
                            'maxsize' try to create maximum maps size.
            - img_list: the list of full path of image files that will be use to create maps.

   Result type: PASS/FAIL
   Results: PASS: If we could create the maps if they matched with requirement.
            FAIL: If we could not create the maps if they matched with requirement
            or could create maps if they did not match with the requirement.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Check and detete all non-defaulf maps.
   2. Test:
       - Create the new maps by use the parameters that we have.
   3. Cleanup:
       - Clean up test environment.

   How it is tested?
       -
"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_MapView_Download_Map(Test):

    def config(self, conf):
        self.conf = conf
        self.format_list = ['.PNG', '.JPG', '.GIF']
        self.testbed.components['ZoneDirector'].delete_all_maps()
        logging.info('Delete all Maps on Zone Director successfully')

        # Get the size of the Default map.
        self.default_map_size = self.testbed.components['ZoneDirector'].get_maps_info()[0]['size']
        if 'K' in self.default_map_size.upper():
            self.default_map_size = float(self.default_map_size.upper().split('K')[0])
        elif 'M' in self.default_map_size.upper():
            self.default_map_size = float(self.default_map_size.upper().split('M')[0]) * 1024
        else:
            self.default_map_size = float(self.default_map_size) / 1024

    def test(self):
        if not self.conf.has_key('option'):
            self.option = 'multi'
        else:
            self.option = self.conf['option'].lower()

        if self.option not in ['diff', 'maxsize']:
            return self._testMultiMap()

        if self.option == 'diff':
            return self._testDiffType()

        if self.option == 'maxsize':
            return self._testMaxSize()

    def cleanup(self):
        self.testbed.components['ZoneDirector'].delete_all_maps()
        logging.info('Clean up testing environment successfully')

    def _testMultiMap(self):
        logging.info('Test to download multiple maps')
        totalsize = self.default_map_size
        totalmap = 1
        for img in self.conf['img_list']:
            totalsize = totalsize + float(os.path.getsize(img) / 1024)
            if totalsize < 2 * 1024:
                if os.path.splitext(img)[1].upper() not in self.format_list:
                    raise Exception('The file extension is not in %s.' % repr(self.format_list))
                else:
                    try:
                        self.testbed.components['ZoneDirector'].create_map('Test_Map_%d' % totalmap, img)
                        totalmap += 1
                    except Exception, e:
                        if 'Create map error' in e.message:
                            return ('FAIL', e.message)
                        else:
                            raise

        return ('PASS', '')

    def _testDiffType(self):
        logging.info('Test to download maps using different formats')
        if self.conf.get('max_size'):
            maxsize = int(self.conf['max_size'])
        else:
            maxsize = 2

        in_of_support = 0
        out_of_support = 0
        for img in self.conf['img_list']:
            totalsize = self.default_map_size
            totalsize = totalsize + float(os.path.getsize(img) / 1024)
            if totalsize < maxsize * 1024:
                if os.path.splitext(img)[1].upper() in self.format_list:
                    in_of_support += 1
                    expect_result = True
                else:
                    out_of_support += 1
                    expect_result = False

                try:
                    self.testbed.components['ZoneDirector'].create_map('Test_Map', img)
                    result = True
                except Exception, msg:
                    if 'Create map error' in msg:
                        result = False
                        mess = msg[1]
                    else:
                        result = False
                        #raise
                self.testbed.components['ZoneDirector'].delete_all_maps()

                if result != expect_result:
                    if expect_result == False:
                        mess = 'ZD could create a map from file \'%s\'. Which\'s extension not in %s.' \
                             % (img, repr(self.format_list))

                    return ('FAIL', mess)

        if in_of_support > 0 and out_of_support > 0:
            return ('PASS', '')
        else:
            raise Exception('This test request there are both of support and non-support formats of map to complete')

    #JLIN@20081112 add maxsize can be changed by test parameter
    def _testMaxSize(self):
        logging.info('Test maximum maps size')
        maxsize = int(self.conf['max_size'])
        test_img = ''
        if len(self.conf['img_list']) >= 1:
            for img in self.conf['img_list']:
                if os.path.splitext(img)[1].upper() in self.format_list:
                    test_img = img
                    break
            if not test_img:
                raise Exception('ERROR', 'There is no image\'s format in %s.' % repr(self.format_list))

        image_size = float(os.path.getsize(test_img) / 1024)
        expect_maps_num = int((maxsize * 1024 - self.default_map_size) / image_size)

        logging.info('Try to create %d maps using the image with size of %0.2f' % (expect_maps_num, image_size))
        for i in range(expect_maps_num):
            try:
                self.testbed.components['ZoneDirector'].create_map('Test_Map_%d' % (i + 1), test_img)
            except Exception, msg:
                if 'Create map error' in msg:
                    return ('FAIL', msg[1])
                else:
                    raise

        logging.info('Try to create an extra map that makes the total maps size larger than %s MB' % maxsize)
        try:
            self.testbed.components['ZoneDirector'].create_map('Test_Map_%d' % (expect_maps_num + 1), test_img)
            return ('FAIL', 'ZD could create a map which makes the total maps size larger than %s MB' % maxsize)
        except:
            return ('PASS', '')

