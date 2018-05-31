import jenkins
import re
import sys
import time
import talk_to_rc_jenkins as CI3_JENKINS

class NightCI3Moniter():
	def __init__(self, username, password, parent_page, build_rpm_ci_name, build_testing_ci_name):
		self.username = username
		self.password = password
		self.build_rpm_ci_name = build_rpm_ci_name
		self.build_testing_ci_name = build_testing_ci_name
		self.build_rpm_ci = CI3_JENKINS.TalkToRCCI(self.username, self.password, self.build_rpm_ci_name)
		self.build_testing_ci = CI3_JENKINS.TalkToRCCI(self.username, self.password, self.build_testing_ci_name)
		self.build_testing_ci_jenkins = self.build_rpm_ci.server
		self.build_rpm_ci_console = ""
		self.build_testing_parameter = {}
		self.parent_page = parent_page
		self.ci3_jenkins_url = "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com/job/ET_Builds_Testing/"


	def get_build_id(self):
		self.build_rpm_ci.get_last_completed_build_number()
		build_rpm_ci_job_id = self.build_rpm_ci.last_completed_build_number
		build_id_jenkins_url = self.ci3_jenkins_url + str(build_rpm_ci_job_id)
		print "=== the latest build comes from:"
		print "=== " build_id_jenkins_url
		self.build_rpm_ci.get_latest_build_console_log_content()
		self.build_rpm_ci_console = self.build_rpm_ci.console_log_content
		self.build_id = str(re.findall('\d{4}', self.build_rpm_ci_console)[-1])
		print(self.build_id)

	def run_ci3_build_testing(self):
		old_build_number = self.build_testing_ci_jenkins.get_job_info(self.build_testing_ci_name)['lastBuild']['number']
		self.build_testing_parameter['username'] = self.username
		self.build_testing_parameter['password'] = self.password
		self.build_testing_parameter['et_build_name_or_id'] = self.build_id
		self.build_testing_parameter['parent_page'] = self.parent_page
		self.build_testing_ci_jenkins.build_job(self.build_testing_ci_name, self.build_testing_parameter)
		time.sleep(30)
		new_build_number = self.build_testing_ci_jenkins.get_job_info(self.build_testing_ci_name)['lastBuild']['number']
		if int(new_build_number) > int(old_build_number):
			print "=== the new build testing is running, done ==="
			jenkins_url = "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com/job/ET_Builds_Testing/" + str(new_build_number)
			print "=== For the jobs details, you can refer to:"
			print jenkins_url

if __name__ == "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	parent_page = sys.argv[3]
	build_rpm_ci_name = sys.argv[4]
	build_testing_ci_name = sys.argv[5]
	monitor = NightCI3Moniter(username, password, parent_page, build_rpm_ci_name, build_testing_ci_name)
	monitor.get_build_id()
	monitor.run_ci3_build_testing()

