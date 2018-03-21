import re
import sys
import os
import talk_to_rc_jenkins

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class OutputE2EReport():
	def __init__(self, username, password, build_name, et_rc_version):
		self.username = username
		self.password = password
		self.build_name = build_name
		self.rc_jenkins = talk_to_rc_jenkins.TalkToRCCI(username, password, build_name)
		self.et_rc_version = et_rc_version
		self.rc_jenkins.get_last_completed_build_number()
		self.last_completed_build_number = self.rc_jenkins.last_completed_build_number
		self.rc_jenkins.get_latest_build_console_log_content()
		self.console_log_content = self.rc_jenkins.console_log_content
		self.e2e_console_url = RC_Jenkins + "/job/" + self.build_name + "/" + str(self.last_completed_build_number) + "/console"
		self.e2e_testing_result = ""
		self.e2e_testing_result_url = RC_Jenkins + "/job/" + self.build_name  + "/" + str(self.last_completed_build_number) + "/robot"

	def check_console_log(self):
		if not re.search('Done publishing Robot results', self.console_log_content):
			print "====There is someting wrong. please check the log manually"
			print "====console log URL: " + self.e2e_console_url
			self.e2e_testing_result = "FAILED (unexpected error)"
			self.e2e_testing_result_url = self.e2e_console_url
		else:
			print "====E2E has been finished======================="
			failed_cases_number = re.findall(r'[\d+]+ failed', self.console_log_content)[-1].split()[0]
			print failed_cases_number
			if int(failed_cases_number) != 0:
				self.e2e_testing_result = "FAILED(" + failed_cases_number + " cases failed)"
				self.e2e_testing_result_url = self.e2e_testing_result_url
			else:
				self.e2e_testing_result = "PASSED"
				self.e2e_testing_result_url = self.e2e_testing_result_url


	def summary_report(self):
		print "=====================Testing Report: Begin=================="
		print "ET RC Version: " + self.et_rc_version
		print "Testing Type: " + "E2E Testing"
		print "Testing Result: " + self.e2e_testing_result
		print "Testing Report URL: " + self.e2e_testing_result_url
		print "=====================Testing Report: End================"

	def output_e2e_report(self):
		self.check_console_log()
		self.summary_report()


if __name__== "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	build_name = sys.argv[3]
	et_rc_version = sys.argv[4]
	e2e_rc_jenkins = OutputE2EReport(username, password, build_name, et_rc_version)
	e2e_rc_jenkins.output_e2e_report()