# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Functional testing for 'delete an existing map' option of the Zone Director.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
            - name : name of the existing map that we want to delete.
   Result type: PASS/FAIL
   Results: PASS: If we could detete an existing non-default map.
            FAIL: If we could not detete an existing non-default map.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Check and create an existing maps for test.
   2. Test:
       - Try to detete the expected map.
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

class ZD_MapView_Delete_Map(Test):

    def config(self, conf):
        self.conf = conf
        existed = False
        self.maps_info = self.testbed.components['ZoneDirector'].get_maps_info()
        for map_info in self.maps_info:
            if map_info['name'] == self.conf['name']:
                existed = True
                break

        if not existed:
            self.testbed.components['ZoneDirector'].delete_all_maps()
            existed_map = self.conf['img_path']
            self.testbed.components['ZoneDirector'].create_map(self.conf['name'], existed_map)
            logging.info('Create map for testing successfully')

    def test(self):
        try:
            self.testbed.components['ZoneDirector'].delete_map(self.conf['name'])
            logging.info('Delete map \'%s\' successfully' % self.conf['name'])
            return ('PASS', '')
        except Exception, msg:
            if 'Delete map error' in msg:
                return ('FAIL', msg[1])
            else:
                raise

    def cleanup(self):
        self.testbed.components['ZoneDirector'].delete_all_maps()
        logging.info('Clean up testing environment successfully')


