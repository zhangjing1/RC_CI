import re
import sys
import os
import time
import jenkins

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToRCCIForE2E():
	def __init__(self, username, password, build_name, et_rc_version, expect_run_time):
		self.username = username
		self.password = password
		self.build_name = build_name
		self.server = jenkins.Jenkins(RC_Jenkins, self.username, self.password)
		self.et_rc_version = et_rc_version
		self.e2e_testing_console_log_url = ""
		self.lastest_build_number = 0
		self.e2e_testing_report_url = ""
		self.e2e_testing_result = ""
		self.console_log_content = ""
		self.expect_run_time = expect_run_time

	def get_e2e_testing_result(self):
		self.e2e_testing_result = self.server.get_build_info(self.build_name, self.lastest_build_number)['result']

	def get_e2e_console_log_url(self):
		self.e2e_testing_console_log_url = RC_Jenkins + "/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/console"

	def get_e2e_report_url(self):
		self.e2e_testing_report_url = RC_Jenkins + "/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/cucumber-html-reports/overview-features.html"

	def get_e2e_console_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

	def run_build(self):
		print "===Start to run the e2e.0 UAT testing==="
		self.server.build_job(self.build_name, {})

	def get_lastest_build_number(self):
		self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

	def check_job_finished_or_not(self):
		for i in range(2):
			time.sleep(int(self.expect_run_time) * 60)
			self.get_e2e_testing_result()
			if not self.e2e_testing_result:
				print  "=====The job is still running====="
				continue
			else:
				print "=====The job has been finished======"
				break

		self.get_e2e_testing_result()
		if not self.e2e_testing_result:
			print "The testing is running too long, we would stop the job manually"
			self.server.stop_build(self.build_name, self.lastest_build_number)
			self.e2e_testing_result = "FAILED(Timeout)"

	def check_console_log(self):
		# When the job is 'SUCCESS', we consider the testing result is shown as 'PASSED'
		# When the job is 'FAILED', we show the failure details
		if self.e2e_testing_result == "SUCCESS":
			print "=====E2E testing has been PASSED====="
			self.e2e_testing_result = "PASSED"
		elif self.e2e_testing_result == "FAILED" and self.console_log_content.find('[CucumberReport] Preparing Cucumber Reports') < 0:
			print "====There is someting wrong. please check the log manually"
			print "====console log URL: " + self.e2e_testing_console_log_url
			self.e2e_testing_result = "FAILED (unexpected error)"
			self.e2e_testing_report_url = self.e2e_testing_console_log_url
		else:
			print "====E2E has been finished======================="
			failed_cases_number = re.findall(r'[\d+]+ failed', self.console_log_content)[-1].split()[0]
			if int(failed_cases_number) != 0:
				print "=====E2E testing has been FAILED====="
				self.e2e_testing_result = "FAILED(" + failed_cases_number + " cases failed)"

	def summary_report(self):
		print "=====================Testing Report: Begin=================="
		if self.et_rc_version == "EMPTY" :
			print "Testing Type: " + "E2E Testing"
			print "RC Type: CD RC"
			print "Testing Result: " + self.e2e_testing_result
			print "Testing Report URL: " + self.e2e_testing_report_url
		else:
			print "ET RC Version: " + str(self.et_rc_version)
			print "Testing Type: " + "E2E Testing"
			print "Testing Result: " + self.e2e_testing_result
			print "Testing Report URL: " + self.e2e_testing_report_url
		print "=====================Testing Report: End================"

	def run_one_test(self):
		self.run_build()
		# jenkins need some time to create one job
		time.sleep(30)
		self.get_lastest_build_number()
		self.get_e2e_console_log_url()
		self.get_e2e_report_url()
		self.check_job_finished_or_not()
		self.get_e2e_console_content()
		self.check_console_log()
		self.summary_report()


if __name__== "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	build_name = sys.argv[3]
	et_rc_version = ""
	expect_run_time = ""
	if len(sys.argv) == 5:
		print "== This is the testing for Pub RC build =="
		print "== Would set the ET rc build id as EMPTY manually"
		et_rc_version = "EMPTY"
		expect_run_time = sys.argv[4]

	if len(sys.argv) == 6:
		print "== This is the testing for ET RC build =="
		et_rc_version = sys.argv[4]
		expect_run_time = sys.argv[5]

	e2e_rc_jenkins = TalkToRCCIForE2E(username, password, build_name, et_rc_version, expect_run_time)
	e2e_rc_jenkins.run_one_test()

