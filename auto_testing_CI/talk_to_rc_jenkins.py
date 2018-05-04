#/bin/env python
import jenkins
import time
import re
import os
import sys

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToRCCI():
	def __init__(self, username, password, build_name):
		self.build_name = build_name
		self.server = jenkins.Jenkins(RC_Jenkins, username=username, password=password)
		self.test_report = []
		self.last_completed_build_number = 0
		self.console_log_content = ""
		self.current_rc_version = ""
	

	def get_last_completed_build_number(self):
		self.last_completed_build_number = self.server.get_job_info(self.build_name)['lastCompletedBuild']['number']

	def get_latest_build_console_log_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.last_completed_build_number)

	def get_test_report_from_console_log(self):
		current_rc_version_list = re.findall(r'ET RC Version: [\w+ \.]+', self.console_log_content)
		if len(current_rc_version_list) > 0:
			self.current_rc_version = current_rc_version_list[0]
			test_type = re.findall(r'Testing Type: [\w+ \.]+', self.console_log_content)[0].replace("Testing Type: ", "")
			test_result = re.findall(r'Testing Result: [\w+ \.]+', self.console_log_content)[0].replace("Testing Result: ", "")
			test_result_url = re.findall(r'Testing Report URL: [^\n]+', self.console_log_content)[0].replace("Testing Report URL: ", "").replace("'", "")
			self.test_report = [test_type, test_result, test_result_url]
		else:
			self.test_report = ["", "", ""]

	def get_test_report_for_build(self):
		self.get_last_completed_build_number()
		# jenkins need some time to create one job
		time.sleep(30)
		self.get_latest_build_console_log_content()
		self.get_test_report_from_console_log()



if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	username = os.environ.get('ET_RC_User')
	password = os.environ.get('ET_RC_User_Password')
	if len(sys.argv) == 2:
		build_name = sys.argv[1]
		talk_to_rc_jenkins = TalkToRCCI(username, password, build_name)
		talk_to_rc_jenkins.get_test_report_for_build()
		print talk_to_rc_jenkins.test_report




