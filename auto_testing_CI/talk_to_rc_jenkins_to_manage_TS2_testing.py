#/bin/env python
import jenkins
import time
import re
import os
import sys

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToRCCIForTS2():
	def __init__(self, username, password, build_name, et_rc_version, expect_run_time):
		self.username = username
		self.password = password
		self.build_name = build_name
		self.server = jenkins.Jenkins(RC_Jenkins, self.username, self.password)
		self.et_rc_version = et_rc_version
		self.lastest_build_number = 0
		self.TS2_testing_report_url = ""
		self.TS2_testing_result = ""
		self.console_log_content = ""
		self.expect_run_time = expect_run_time

	def get_ts2_testing_result(self):
		self.TS2_testing_result = self.server.get_build_info(self.build_name, self.lastest_build_number)['result']

	def get_ts2_console_log_url(self):
		self.TS2_testing_console_log_url = RC_Jenkins + "/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/console"

	def get_ts2_report_url(self):
		self.TS2_testing_report_url = RC_Jenkins + "/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/cucumber-html-reports/overview-features.html"

	def get_ts2_console_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

	def run_build(self):
		print "===Start to run the TS2.0 UAT testing==="
		self.server.build_job(self.build_name,  {'RPM_BUILD_JOB_ID': self.et_rc_version})

	def get_lastest_build_number(self):
		self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

	def check_job_finished_or_not(self):
		for i in range(2):
			time.sleep(int(self.expect_run_time) * 60)
			self.get_ts2_testing_result()
			if not self.TS2_testing_result:
				print  "=====The job is still running====="
				continue
			else:
				print "=====The job has been finished======"
				break
		self.get_ts2_testing_result()
		if not self.TS2_testing_result:
			print "The testing is running too long, we would stop the job manually"
			self.server.stop_build(self.build_name, self.lastest_build_number)
			self.TS2_testing_result = "FAILED"


	def check_console_log(self):
		# get the status of all multijobs
		jobs_status_list = re.findall(r'status : [\w+]*', self.console_log_content)
		if len(jobs_status_list) < 5 :
			print "========The Env Preparation meets some problem=========="
			self.TS2_testing_report_url = self.TS2_testing_console_log_url
		elif jobs_status_list[4].find('FAILURE'):
			print "========The Env Preparation has been finished==========="
			print "========The Cucumber TS2.0 UAT Testing FAILED==========="
		elif jobs_status_list[4].find('SUCCESS'):
			print "========The Env Preparation has been finished==========="
			print "========The Cucumber TS2.0 UAT Testing SUCCESSED========"


	def summary_report(self):
		if self.get_ts2_testing_result == "FAILURE":
			self.get_ts2_testing_result = "FAILED"
		else:
			self.get_ts2_testing_result = "PASSED"

		print "=====================Testing Report: Begin=================="
		print "ET RC Version: " + str(self.et_rc_version)
		print "Testing Type: " + "TS2.0 UAT Testing"
		print "Testing Result: " + self.TS2_testing_result
		print "Testing Report URL: " + self.TS2_testing_report_url
		print "=====================Testing Report: End================"

	def run_one_test(self):
		self.run_build()
		self.get_lastest_build_number()
		self.get_ts2_console_log_url()
		self.get_ts2_report_url()
		self.check_job_finished_or_not()
		self.get_ts2_console_content()
		self.check_console_log()
		self.summary_report()



if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	username = sys.argv[1]
	password = sys.argv[2]
	build_name = sys.argv[3]
	et_rc_version = sys.argv[4]
	expect_run_time = sys.argv[5]
	talk_to_rc_jenkins = TalkToRCCIForTS2(username, password, build_name, et_rc_version, expect_run_time)
	talk_to_rc_jenkins.run_one_test()


