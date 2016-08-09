'''
@author: phan.nguyen@ruckuswireless.com
'''
import logging
import Queue
import threading
import db_env
from Testlink import models as TLM
from tlc22.TestlinkClient22 import TestlinkClient22


# Queue for mapped test runs' tc_id
testrunmap_queue = Queue.Queue()

# Queue for local Execution write
exec_write_queue = Queue.Queue()

# Queue for test cases to report to Testlink
report_queue = Queue.Queue()

# Reported test cases
reported_testcases = []

# mapped_keys = {'last_exec key' : 'local key/method'}
mapped_keys = {
    'testplan_id': 'plan_id',
    'build_id': 'build_id',
    'status': 'status',
#    'notes': 'notes',
}

'''
  > For each record in TestRunMap table that matches the given criterial,
    get its testcase_tc_id plus other information and put it into testrunmap_queue.

  > With each tc_id in testrunmap_queue, get its last execution result and process it.
    > If exec_id = -1 (not yet executed), put the testcase to report into report_queue.
    > If exec_id != -1 (reported at least once):
      > Put exec_id in exec_read_queue and check tc_id in Execution table.
        a. If no matched record found in Execution (means that not yet reported), then:
           1. Put test case to report into report_queue.
           2. Report test case to Testlink
           3. Update the Execution table.
        b. If a matched record is found in Execution, ONLY report to Testlink if they
        two are not identical to each other.
'''
import time

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(name)s: %(message)s',
)


class RemoteExecCheck(threading.Thread):
    '''
    Threaded Testlink's Execution Checks
    --- tlc.get_tc_exec_result() ---
    '''

    def __init__(self, testrunmap_queue, report_queue, tlc, project_id):
        '''
        '''
        self.logger = logging.getLogger('RemoteExecCheck')
        threading.Thread.__init__(self)
        self.testrunmap_queue = testrunmap_queue
        self.report_queue = report_queue

        self.tlc = tlc
        self.project_id = project_id


    def run(self):
        '''
        '''
        while True:            
            # gets mapped test run from testrunmap_queue
            testrunmap = self.testrunmap_queue.get()
            
            # prepares params for tlc.report_case_result()
            tc_result = {
                'testrunmap': testrunmap,
                'plan_id': str(testrunmap.get_plantestcase_plan_id()),
                'tc_id': str(testrunmap.get_plantestcase_tc_id()),
                'build_id': str(testrunmap.get_testbuild_build_id()),
                'status': testrunmap.get_testrun_result(),
#                'notes': testrunmap.get_testrun_lastest_message(),
            }

            # gets TC last execution result
            self.logger.debug(
                'Trying to get Last Execution Result with (project_id=%s, plan_id=%s, tc_id=%s)'
                %(self.project_id, tc_result['plan_id'], tc_result['tc_id'])
            )
            
#            if not self._is_reported(tc_result):
            
             
            cnt = 3
            while cnt>0:                    
                last_exec = self.tlc.get_tc_exec_result(
                    self.project_id, tc_result['plan_id'],
                    tc_result['tc_id']
                )
                if last_exec[0]['id'] != -1:
                    break
                
                cnt = cnt - 1
                time.sleep(0.5)
                
            if last_exec:                           
                if -1 == last_exec[0]['id'] or \
                not self._is_mached_record(last_exec[0], tc_result):                    
                    self.report_queue.put(tc_result)

            # signals to testrunmap_queue job is done
            self.testrunmap_queue.task_done()

    
    def _is_reported(self, tc_result):
        '''
        Checking status test case if change.
         True: Haven't change
         False: Updated. 
        '''
        if len(reported_testcases) == 0:
            return False
        
        ll = ['plan_id', 'build_id', 'status']
        for tc in reported_testcases:            
            for k, v in tc.items():
                if k in ll and tc_result[k] != v:
                    return False
        
        
        return True
                    

    def _is_mached_record(self, last_exec, tc_result):
        '''
        '''
        for (k_exec, k_local) in mapped_keys.iteritems():
            if last_exec[k_exec] != tc_result[k_local]:
                return False

        return True



class TestcaseReport(threading.Thread):
    '''
    Threaded Testlink's Result Reports
    --- tlc.report_case_result() ---
    '''

    def __init__(self, report_queue, exec_write_queue,
                 tlc, project_id):
        '''
        '''
        self.logger = logging.getLogger('LocalExecCheck')
        threading.Thread.__init__(self)
        self.report_queue = report_queue
        self.exec_write_queue = exec_write_queue

        self.tlc = tlc
        self.project_id = project_id


    def run(self):
        '''
        '''
        while True:
            tc_result = self.report_queue.get()

#            hdr = ['plan_id', 'tc_id', 'build_id', 'status', 'notes', ]
            hdr = ['plan_id', 'tc_id', 'build_id', 'status',]
            report_attrs = dict((key, tc_result[key]) for key in hdr)

            self.logger.debug(
                'Trying to report TC Result: %s' % report_attrs
            )

            result = self.tlc.report_case_result(**report_attrs)            

            if result and -1 != result[0]['id']:
                self.exec_write_queue.put(tc_result)
                reported_testcases.append(tc_result)

            self.report_queue.task_done()



class LocalExecWrite(threading.Thread):
    '''
    Threaded RAT-Testink Integration's Execution Writes
    --- Execution(models.Model) save ---
    '''

    def __init__(self, exec_write_queue, tlc, project_id):
        '''
        '''
        self.logger = logging.getLogger('LocalExecWrite')
        threading.Thread.__init__(self)
        self.exec_write_queue = exec_write_queue

        self.tlc = tlc
        self.project_id = project_id


    def run(self):
        '''
        '''
        while True:
            tc_result = self.exec_write_queue.get()

            # gets TC last execution result
            self.logger.debug(
                'Trying to get Last Execution Result with (project_id=%s, plan_id=%s, tc_id=%s)'
                %(self.project_id, tc_result['plan_id'], tc_result['tc_id'])
            )
            last_exec = self.tlc.get_tc_exec_result(
                self.project_id, tc_result['plan_id'], tc_result['tc_id']
            )
            record = {
                'testrunmap': tc_result['testrunmap'],
                'exec_id': last_exec[0]['id'],
                'status': last_exec[0]['status'],
                'execution_ts': last_exec[0]['execution_ts'],
                'tcversion_id': last_exec[0]['tcversion_id'],
                'tcversion_number': last_exec[0]['tcversion_number'],
#                'notes': last_exec[0]['notes'],
            }

            result = TLM.Execution(**record)
            result.save()
            self.logger.debug('Saved Execution with exec_id=%s to local with id=%s' %(record['exec_id'], result.id))

            self.exec_write_queue.task_done()



class TLReportMgr(object):
    '''
    '''

    def __init__(self, tlc, project_id, plan_id, build_id):
        '''
        '''
        self.logger = logging.getLogger('TLReportMgr')
        self.tlc = tlc
        self.project_id = project_id
        self.plan_id = plan_id
        self.build_id = build_id


    def main(self):
        '''
        '''
        remote_exec = RemoteExecCheck(
            testrunmap_queue, report_queue, self.tlc, self.project_id
        )
        remote_exec.setDaemon(True)
        remote_exec.start()


        result = self._get_mapped_test_runs()
        self.logger.debug('There are %s mapped test runs' % len(result))

        if 0 == len(result):
            return

        for testrunmap in result:
            if str(testrunmap.get_testbuild_build_id()) != self.build_id:
                continue

            testrunmap_queue.put(testrunmap)


        tc_report = TestcaseReport(
            report_queue, exec_write_queue,
            self.tlc, self.project_id
        )
        tc_report.setDaemon(True)
        tc_report.start()


        exec_write = LocalExecWrite(
            exec_write_queue,
            self.tlc, self.project_id
        )
        exec_write.setDaemon(True)
        exec_write.start()


        testrunmap_queue.join()
        report_queue.join()
        exec_write_queue.join()

        self.logger.debug('There are %s TCs reported to Testlink' %
                          len(reported_testcases))


    def _get_mapped_test_runs(self):
        '''
        '''
        # filters by test build
        self.logger.debug(
            'Trying to get Test Run Map records'
        )
        matched_list = TLM.TestRunMap.objects.all()
        plancase_set = set()  
            
        for tc in matched_list:
            plancase_set.add(tc.plantestcase)
                    
        check_list = []
        for plancase in plancase_set:               
            exec_tcs = TLM.TestRunMap.objects.filter(plantestcase=plancase)
            fail = False 
            for tc in exec_tcs:
                res = tc.get_testrun_result()
                if res == 'f':
                    fail = True
                    check_list.append(tc)
                    break
            
            if not fail:         
                check_list.append(exec_tcs[len(exec_tcs)-1])                            
        
        return check_list
        
#        return TLM.TestRunMap.objects.all()


if __name__ == '__main__':
    '''
    '''
    
    conf = {
        'server_url': 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php',
        'dev_key': '014ea04869a6bd4faa691dbab7589891',
        'project': 'Zone Director',
        'plan': 'Sandbox Automation',
        'build': '9.3.0.0.60',
    }

    tlc = TestlinkClient22(conf['dev_key'], conf['server_url'])
    
    project_id = tlc.get_project_by_name(conf['project'])[0]['id']
    builds = tlc.get_builds_by_plan_name(conf['project'], conf['plan'])
    from pprint import pformat
    print pformat(builds)
    for b in builds:
        if b['name'] == conf['build']:
            build_id = b['id']
            plan_id = b['testplan_id']

#    rm = TLReportMgr(tlc, project_id, plan_id, build_id)

#    rm.main()

