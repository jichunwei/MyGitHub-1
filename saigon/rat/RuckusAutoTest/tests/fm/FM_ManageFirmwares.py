'''
1.1.9.6    Manage firmware Files Test suite

1.1.9.6.1  Create new fw upload file
1.1.9.6.2  Edit a firmware file
1.1.9.6.3  Delete firmware file

- Firmwares are downloaded from k2
Inputs:
- firmware: is the *.Bl7 file downloaded from k2 by ats_ script
- model: zf2925, ...

Internal Vars:
- firmware_path: is the path to firmware files

DESIGN NOTE:
- Do NOT delete uploaded firmware for other test to be performed faster:
  in the case of edit

Testscript of Case 1: Create new fw file upload
+ Config:
  - make sure it is not in the uploaded list. Otherwise, delete the
    existing one. Make a note, so that the later upload can be kept.

+ Test:
  - create new uploading task
    . select device model
    . select the downloaded firmware file
    . click Ok
  - monitor the uploading, making sure it is uploaded successfully
  - check the list of uploaded firmwares, make sure the newly uploaded one
    is there and all its info are correct

+ Clean up:
  - Do NOT remove the uploaded firmware

Testscript of Case 2: Edit a firmware file
+ Config:
  - is the firmware available? If not, upload it to FM

+ Test:
  - find it on the list of available firmwares
  - click Edit button
  - change something, likes models
  - click Ok
  - verify the change is affected by re-open the details of this firmware

+ Clean up:
  - Do NOT delete the uploaded firmware

Testscript of Case 3: Delete firmware file
+ Config:
  - is this firmware on FM? If yes, mark for re-upload

+ Test:
  - find the firmware on the list
  - delete it
  - make sure it is not in the list anymore

+ Clean up:
  - If test performs successfully, then re-upload this firmware (if it is marked)
'''

import os, time, logging, re, random
from datetime import *
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.fm.lib_FM import *


class FM_ManageFirmwares(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'test_type':  'the type of test: upload, edit, delete',
        'model':      'the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'filename':   'firmware file',
        'test_model': 'change to this model and back', # in edit case
    }


    def config(self, conf):
        self.errmsg = None
        self.aliases = init_aliases(testbed=self.testbed)
        self._cfgTestParams(**conf)
        if self.steps['config']: self.steps['config']()


    def test(self):
        self.steps['configTest']()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.steps['testTheResults']()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        '''
        - clean up (if required)
        - log out FM
        '''
        if self.steps['cleanUp']: self.steps['cleanUp']()
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'test_type':   'upload',
            'model':       'zf2925',
            'filename':    '',
            'test_model':  'zf7942', # for edit case
        }
        self.p.update(kwa)
        self._cfgSteps(test_type=self.p['test_type'])

        logging.debug('Test Configs:\n%s' % pformat(self.p))
        self.fm_uploaded = False


    def _cfgSteps(self, **kwa):
        '''
        kwa:
        - test_type: this will be used to define function
        '''
        self.steps = {
            'upload': {
                'configTest': self._upload_firmware,
                'testTheResults': self._testUploadedFw,
                'config': self._cfgUploadCase,
                'cleanUp': None,
            },
            'edit': {
                'configTest': self._edit_firmware,
                'testTheResults': self._testEditedFw,
                'config': self._cfgEditnDeleteCases,
                'cleanUp': self._cleanupEditCase,
            },
            'delete': {
                'configTest': self._delete_firmware,
                'testTheResults': self._testDeletedFw,
                'config': self._cfgEditnDeleteCases,
                'cleanUp': self._cleanupDeleteCase,
            },
        }[kwa['test_type']]


    def _cfgUploadCase(self):
        # delete existing firmware (if any)
        lib.fm.fw.delete_firmware(self.aliases.fm, name=self.p['filename'])


    def _cfgEditnDeleteCases(self):
        self._uploadFwIfNotExist()


    def _cleanupEditCase(self):
        '''
        - restore the old config of edited firmware
        '''
        self._edit_firmware(key='model')


    def _cleanupDeleteCase(self):
        '''
        - re-upload the firmware, if it is on the server before testing
        '''
        if not self.fm_uploaded: self._upload_firmware()


    def _delete_firmware(self):
        '''
        - delete the firmware
        '''
        r = lib.fm.fw.delete_firmware(self.aliases.fm, name=self.p['filename'])
        if not r:
            self.errmsg = 'Unable to delete the firmware'
            return


    def _edit_firmware(self, **kwa):
        '''
        kwa:
        - key: what model should be used for testing?
               this should be 'model' or 'test_model'
        '''
        _kwa = {'key': 'test_model'}
        _kwa.update(kwa)
        try:
            lib.fm.fw.edit_firmware(self.aliases.fm,
                                          name=self.p['filename'],
                                          models=[self.p[_kwa['key']]])
        except Exception, e:
            self.errmsg = str(e)
            return


    def _uploadFwIfNotExist(self):
        # is this firmware exist on server?
        r, i, t = lib.fm.fw.find_firmware(self.aliases.fm,
                                                criteria={'firmwarename': self.p['filename']})
        if not r: self._upload_firmware()


    def _upload_firmware(self):
        logging.info('Create new Firmware Upload for model %s' % self.p['model'])
        lib.fm.fw.upload_firmware(self.aliases.fm,
                filepath=os.path.join(init_firmware_path(), self.p['filename']),
                models=[self.p['model']])
        self.fm_uploaded = True


    def _testUploadedFw(self, **kwa):
        '''
        kwa:
        - test_model
        '''
        _kwa = {'test_model': self.p['model']}
        _kwa.update(kwa)

        logging.info('Retrieve and compare uploaded firmware for model %s' % self.p['model'])
        models = None
        try: models = lib.fm.fw.get_firmware(self.aliases.fm, name=self.p['filename'])
        except Exception, e:
            if str(e) == 'Firmware cannot be found: %s' % self.p['filename']:
                self.errmsg = 'Could not found the uploaded firmware on firmware list: %s' % self.p['filename']
                return
            raise Exception(str(e))

        # check the models for in-consistencies
        if not _kwa['test_model'].lower() in models:
            self.errmsg = 'Could not found the expected model "%s" in models "%s"' % \
                          (_kwa['test_model'], models)
            return

        for m in models:
            if not _kwa['test_model'].lower() == m:
                self.errmsg = 'Un-expected model is selected: %s. List of models "%s"' % \
                              (m, models)
                return


    def _testEditedFw(self):
        self._testUploadedFw(test_model=self.p['test_model'])


    def _testDeletedFw(self):
        '''
        - find the deleted firmware on FM firmware list
        '''
        a = self.aliases
        logging.info('Check to make sure the firmware is deleted for model %s' % self.p['model'])
        r, i, t = lib.fm.fw.find_firmware(self.aliases.fm, criteria={'firmwarename': self.p['filename']})
        if r:
            self.errmsg = 'Firmware deletion fails. Fw is still on FM: %s' % self.p['filename']
            return
