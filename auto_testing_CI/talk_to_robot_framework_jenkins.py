import jenkins
import time
import re
import os
import sys

RobotFramework_Jenkins = os.environ.get("RobotFrameWork_Jenkins_URL") or "https://jenkins.engineering.redhat.com"
class TalkToRobotFrameworkCI():
	def __init__(self, username, password, build_name, expected_run_time, check_loop_time, et_rc_version):
		self.username = username
		self.password = password
		self.server = jenkins.Jenkins(RobotFramework_Jenkins, username=self.username, password=self.password)
		self.build_name = os.environ.get('RobotFramework_') or build_name
		self.expected_run_time = expected_run_time
		self.check_loop_time = check_loop_time
		self.lastest_build_number = 0
		self.console_log_content = ""
		self.robotframework_console_url = ""
		self.tcms_run_url = ""
		self.tcms_run_id = 0
		self.robotframework_testing_result = ""
		self.robotframework_testing_result_url = ""
		self.et_rc_version = et_rc_version

	def get_latest_build_console_log_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

	def get_console_log_url(self):
		self.robotframework_console_url = RobotFramework_Jenkins + "/view/Errata Tool/job/Errata-QE-BasicAuth/" + str(self.lastest_build_number) + "/console/"

	def run_build(self):
		print "===Start to run the robotframework UAT testing==="
		self.server.build_job(self.build_name, {'PROJECT_NAME':"Errata"})

	def get_lastest_build_number(self):

		self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

	def summary_the_result(self):
		print "=====================Testing Report: Begin=================="
		print "ET RC Version: " + self.et_rc_version
		print "Testing Type: " + "RobotFramework UAT Testing"
		print "Testing Result: " + self.robotframework_testing_result
		print "Testing Report URL: " + self.robotframework_testing_result_url.rstrip()
		print "=====================Testing Report: End================"

	def check_console_log(self):
		#print self.console_log_content
		print re.search("AUTOMATION DONE", self.console_log_content)
		if not re.search('AUTOMATION DONE', self.console_log_content):
			print "====There is someting wrong. please check the log manually"
			print "====console log URL: " + self.robotframework_console_url
			self.robotframework_testing_result = "FAILED (unexpected error)"
			self.robotframework_testing_result_url = self.robotframework_console_url
		else:
			print "====Automation has been finished======================="
			self.tcms_run_id = re.findall(r'New Run ID: [\d+\.]+', self.console_log_content)[0].split(':')[1]
			self.tcms_run_url = "https://tcms.engineering.redhat.com/run/" + str(self.tcms_run_id)
			failed_cases_number = re.findall(r'[\d+]+ failed', self.console_log_content)[-1].split()[0]
			#print failed_cases_number
			if failed_cases_number != '0':
				self.robotframework_testing_result = "FAILED(" + failed_cases_number + " cases failed)"
				self.robotframework_testing_result_url = self.tcms_run_url
			else:
				self.robotframework_testing_result = "PASSED"
				self.robotframework_testing_result_url = self.tcms_run_url

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
			self.robotframework_testing_result = "FAILED: Aborted"
			self.robotframework_testing_result_url = self.robotframework_console_url


	def run_one_test(self):
		self.run_build()
		# jenkins need some time to create one job
		time.sleep(30)
		self.get_lastest_build_number()
		self.get_console_log_url()
		self.check_job_finished_or_not()
		self.get_latest_build_console_log_content()
		self.check_console_log()
		self.summary_the_result()

if __name__== "__main__":
	if len(sys.argv) == 6:
		username = sys.argv[1]
		password = sys.argv[2]
		jenkins_build_name = sys.argv[3]
		jenkins_build_expect_time = sys.argv[4]
		et_rc_version = sys.argv[5]
		talk_to_robotframework_jenkinks = TalkToRobotFrameworkCI(username, password, jenkins_build_name, jenkins_build_expect_time, 2, et_rc_version)
		talk_to_robotframework_jenkinks.run_one_test()
