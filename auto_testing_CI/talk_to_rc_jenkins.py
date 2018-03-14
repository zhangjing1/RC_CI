#/bin/env python
import jenkins
import time
import re
import os
import sys

RC_Jenkins = os.environ.get("RC_Jenkins_URL")
class TalkToRCCI():
	def __init__(self, build_name):
		self.build_name = build_name
		self.server = jenkins.Jenkins(RC_Jenkins, username=self.username, password=self.password)
		self.test_report = ""
		self.last_completed_build_number = 0
		self.console_log_content = ""
	

	def get_last_completed_build_number(self):
		self.last_completed_build_number = self.server.get_job_info(self.build_name)['lastCompletedBuild']['number']

	def get_latest_build_console_log_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.last_completed_build_number)

	def get_test_report_from_console_log(self):
		test_type = re.findall(r'Testing Type: [\w+ \.]+', console_log_content)[0].replace("Testing Type: ", "")
		test_result = re.findall(r'Testing Result: [\w+ \.]+', console_log_content)[0].replace("Testing Result: ", "")
		test_result_url = re.findall(r'Testing Report URL: [\w+ \.]+', console_log_content)[0].replace("Testing Reprot URL: ", "")
		self.test_report = test_type + test_result + test_result_url

	def get_test_report_for_build(self):
		self.get_last_completed_build_number()
		self.get_latest_build_console_log_content()
		self.get_test_report_from_console_log()








