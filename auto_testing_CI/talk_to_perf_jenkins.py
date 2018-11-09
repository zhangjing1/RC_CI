#/bin/env python
'''
The script is used to talk to perf jenkins, then run the test and show the report.
I guess the parameters and functions are intelligible. So no more introduction for it.

Prerequisite:
1. If you would like to run the script locally, make sure python package 'python-jenkins' has
been installed. Otherwise, you can try the command 'pip install python-jenkins'
2. Set the 'ET_Perf_User' and 'ET_Perf_User_Password' which should be your perf jenkins account.

Usage:
to run smoke testing: python script_name.py  smoke
to run full testing:  python script_name.py  full_testing
to run both smoke & full testing: python script_name.py all
'''

import jenkins
import time
import re
import os
import sys

ET_Perf_Server = os.environ.get("ET_Perf_Server") or "errata-stage-perf.host.stage.eng.bos.redhat.com"
ET_Stub_Server = os.environ.get("ET_Perf_Stub_Server") or "10.8.248.96"
ET_DB_Server = os.environ.get("ET_Perf_DB_Server") or "errata-stage-perf-db.host.stage.eng.bos.redhat.com"
Perf_Jenkins = os.environ.get('ET_Perf_URL') or "https://perfci.eng.pek2.redhat.com"

class TalktoPerfCI():
	global ET_Perf_Server, ET_Stub_Server, ET_DB_Server, Perf_Jenkins
	def __init__(self, username, password, build_name, expected_run_time, check_loop_time, et_rc_version):
		self.username = username
		self.password = password
		self.server = jenkins.Jenkins(Perf_Jenkins, username=self.username, password=self.password)
		self.build_name = os.environ.get('Perf_Build_Name') or build_name
		self.expected_run_time = expected_run_time
		self.check_loop_time = check_loop_time
		self.default_build_number_to_compare = 342
		self.lastest_build_number = 0
		self.last_completed_build_number = 0
		self.console_log_content = ""
		self.perf_testing_result = ""
		self.perf_testing_comparison_url = ""
		self.perf_testing_console_url = ""
		self.et_rc_version = et_rc_version

	def get_latest_build_console_log_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

	def get_console_log_url(self):
		self.perf_testing_console_url = Perf_Jenkins + "/view/ET/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/console"

	def get_last_completed_build_number(self):
		self.last_completed_build_number = self.server.get_job_info(self.build_name)['lastCompletedBuild']['number']
		#print "last completed build number:"
		#print self.last_completed_build_number

	def run_build(self):
		print "===Start to run the perf testing==="
		self.server.build_job(self.build_name,  {'ET_SERVER': ET_Perf_Server, 'Stub_Server': ET_Stub_Server, 'ET_DB': ET_DB_Server})

	def get_lastest_build_number(self):
		self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

	def summary_the_result(self):
		print "=====================Testing Report: Begin=================="
		print "ET RC Version: " + self.et_rc_version
		print "Testing Type: " + "Performance Baseline Testing"
		print "Testing Result: " + self.perf_testing_result
		if self.perf_testing_result == "FAILED":
			print "Testing Report URL: " + self.perf_testing_console_url
			print "=====================Testing Report: End================"
			quit()
		if self.perf_testing_result == "FINISHED":
			print "Testing Report URL: " + self.perf_testing_comparison_url
		print "=====================Testing Report: End================"

	def check_console_log(self):
		print "=====Checking the console log to make sure the testing is running well===="
		error_item = re.findall(r'Err:    [\d+\.]+', self.console_log_content)
		for error in error_item:
			if error.split()[1] > 20 :
				self.perf_testing_result = "FAILED"
				print "====There is something wrong shown in the console log, please check manually===="
				break
			else:
				continue
		if self.perf_testing_result != "FAILED":
			self.perf_testing_result = "FINISHED"
		print "=====The perf testing has been done======"

	def check_job_finished_or_not(self):
		for i in range(int(self.check_loop_time)):
			time.sleep(int(self.expected_run_time) * 60)
			if not self.server.get_build_info(self.build_name, self.lastest_build_number)['result']:
				print  "=====The job is still running====="
				continue
			else:
				print "=====The job has been finished======"
				break
		if not self.server.get_build_info(self.build_name, self.lastest_build_number)['result']:
			print "The testing is running too long, we would stop the job manually"
			self.server.stop_build(self.build_name, self.lastest_build_number)
			self.perf_testing_result = "FAILED"

	def get_comparision_report_url(self):
		# get the latest job to do the comparison with the fix build et 3.16.4
		self.perf_testing_comparison_url = Perf_Jenkins + "/view/ET/job/" + self.build_name + "/" + str(self.lastest_build_number) \
                      + "/performance-report/comparisonReport/" + str(self.default_build_number_to_compare) +"/monoReport#!/report/_/Perf-build_" \
                      + str(self.lastest_build_number) + "_vs_" + str(self.default_build_number_to_compare) +"/perfcharts-simple-perfcmp"
		#print self.perf_testing_comparison_url

	def run_one_test(self):
		self.get_last_completed_build_number()
		self.run_build()
		# before get the build number, sleep some seconds to make sure the build is running
		time.sleep(30)
		self.get_lastest_build_number()
		self.get_comparision_report_url()
		self.get_console_log_url()
		self.check_job_finished_or_not()
		self.get_latest_build_console_log_content()
		self.check_console_log()
		self.summary_the_result()

if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	testing_type = sys.argv[1]
	perf_expect_run_time = sys.argv[2]
	username = os.environ.get('ET_Perf_User') or sys.argv[3]
	password = os.environ.get('ET_Perf_User_Password') or sys.argv[4]
	et_rc_version = sys.argv[-1]
	#print et_rc_version
	if testing_type == "smoke":
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI_MIN", 5, 2, et_rc_version)
		talk_to_jenkinks_smoke.run_one_test()
	if testing_type == "full_perf":
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI", perf_expect_run_time, 2, et_rc_version)
		talk_to_jenkinks_smoke.run_one_test()
	if testing_type == "all":
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI_MIN", 5, 2, et_rc_version)
		talk_to_jenkinks_smoke.run_one_test()
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI", 80, 2, et_rc_version)
		talk_to_jenkinks_smoke.run_one_test()
