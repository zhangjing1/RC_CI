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
ET_Stub_Server = os.environ.get("ET_Perf_Stub_Server") or "10.8.248.96/RPC2"
ET_DB_Server = os.environ.get("ET_Perf_DB_Server") or "errata-stage-perf-db.host.stage.eng.bos.redhat.com"
Perf_Jenkins = os.environ.get('ET_Perf_URL') or "https://perfci.eng.pek2.redhat.com"
Perf_Comparesion_Report_Url = ""
Perf_Console_Log_Url = ""
class TalktoPerfCI():
	global ET_Perf_Server, ET_Stub_Server, ET_DB_Server, Perf_Jenkins, Perf_Console_Log_Url, Perf_Comparesion_Report_Url
	def __init__(self, username, password, build_name, expected_run_time, check_loop_time):
		self.username = username
		self.password = password
		self.server = jenkins.Jenkins(Perf_Jenkins, username=self.username, password=self.password)
		self.build_name = os.environ.get('Perf_Build_Name') or build_name
		self.expected_run_time = expected_run_time
		self.check_loop_time = check_loop_time
		self.lastest_build_number = 0
		self.last_completed_build_number = 0
		self.console_log_url = ""
		self.console_log_content = ""

	def get_latest_build_console_log_content(self):
		self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

	def get_console_log_url(self):
		Perf_Console_Log_Url = Perf_Jenkins + "/view/ET/job/" + self.build_name + "/" + str(self.lastest_build_number) + "/console"

	def get_last_completed_build_number(self):
		self.last_completed_build_number = self.server.get_job_info(self.build_name)['lastCompletedBuild']['number']

	def run_build(self):
		print "===Start to run the perf testing==="
		self.server.build_job(self.build_name,  {'ET_SERVER': ET_Perf_Server, 'Stub_Server': ET_Stub_Server, 'ET_DB': ET_DB_Server})

	def get_lastest_build_number(self):
		self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

	def check_console_log(self):
		print "=====Checking the console log to make sure the testing is running well===="
		error_item = re.findall(r'Err:    [\d+\.]+', self.console_log_content)
		for error in error_item:
			if error.split()[1] > 20 :
				print "There is something wrong with run, FAILED"
				print "Please check the console log:", Perf_Console_Log_Url
				quit()
			else:
				continue
		print "=====Congrats, the perf testing has been done======"

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
			self.server.stop_build(self.build_name, self.lastest_build_number)
			print "=====The job run costs too long time! I guess something is wrong. please check:", Perf_Console_Log_Url
			quit()

	def run_one_test(self):
		self.get_last_completed_build_number()
		self.run_build()
		self.get_lastest_build_number()
		self.get_console_log_url()
		self.check_job_finished_or_not()
		self.get_latest_build_console_log_content()
		self.check_console_log()
		self.get_comparision_report_url()

	def get_comparision_report_url(self):
		Perf_Comparesion_Report_Url = Perf_Jenkins + "/view/ET/job/" + self.build_name + "/" + str(self.lastest_build_number) \
                      + "/performance-report/comparisonReport/" + str(self.last_completed_build_number) +"/monoReport#!/report/_/Perf-build_" \
                      + str(self.lastest_build_number) + "_vs_" + str(self.last_completed_build_number) +"/perfcharts-simple-perfcmp"
        print "=====Congrats, The comparesion report is:", Perf_Comparesion_Report_Url

if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	username = os.environ.get('ET_Perf_User')
	password = os.environ.get('ET_Perf_User_Password')
	if len(sys.argv) == 2 and sys.argv[1] == "smoke":
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI_MIN", 5, 2)
		talk_to_jenkinks_smoke.run_one_test()
	if len(sys.argv) == 2 and sys.argv[1] == "full_perf":
		talk_to_jenkinks_smoke = TalktoPerfCI(username, password, "ET_Baseline_PDI", 40, 2)
		talk_to_jenkinks_smoke.run_one_test()
	if len(sys.argv) == 2 and sys.argv[1] == "all":
		talk_to_jenkinks_smoke = TalktoPerfCI('wlin', 'arNdkN47_', "ET_Baseline_PDI_MIN", 5, 2)
		talk_to_jenkinks_smoke.run_one_test()
		talk_to_jenkinks_smoke = TalktoPerfCI('wlin', 'arNdkN47_', "ET_Baseline_PDI", 40, 2)
		talk_to_jenkinks_smoke.run_one_test()
