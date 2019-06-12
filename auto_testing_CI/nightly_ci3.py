import jenkins
import re
import sys
import time
import talk_to_rc_jenkins as CI3_JENKINS

class NightCI3Moniter():
	def __init__(self, username, password, confluence_username, confluence_password, parent_page, build_rpm_ci_name, build_testing_ci_name, IS_COVERAGE_NEEDED):
		self.username = username
		self.password = password
		self.confluence_username = confluence_username
		self.confluence_password = confluence_password
		self.build_rpm_ci_name = build_rpm_ci_name
		self.build_testing_ci_name = build_testing_ci_name
		self.build_rpm_ci = CI3_JENKINS.TalkToRCCI(self.username, self.password, self.build_rpm_ci_name)
		self.build_rpm_ci_jenkins = self.build_rpm_ci.server
		self.build_testing_ci = CI3_JENKINS.TalkToRCCI(self.username, self.password, self.build_testing_ci_name)
		self.build_testing_ci_jenkins = self.build_rpm_ci.server
		self.build_testing_parameter = {}
		self.parent_page = parent_page
		self.IS_COVERAGE_NEEDED = IS_COVERAGE_NEEDED
		self.et_jenkins_url = "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"


	def get_build_id(self):
		build_rpm_ci_job_id = self.build_rpm_ci_jenkins.get_job_info(self.build_rpm_ci_name)['lastSuccessfulBuild']['number']
		build_rpm_ci_jenkins_url = self.et_jenkins_url + '/job/'+ self.build_rpm_ci_name + "/" + str(build_rpm_ci_job_id)
		print "=== the latest build comes from:"
		print build_rpm_ci_jenkins_url
		self.build_id = build_rpm_ci_job_id

	def run_ci3_build_testing(self):
		old_build_number = self.build_testing_ci_jenkins.get_job_info(self.build_testing_ci_name)['lastBuild']['number']
		self.build_testing_parameter['username'] = self.username
		self.build_testing_parameter['password'] = self.password
		self.build_testing_parameter['confluence_username'] = self.confluence_username
		self.build_testing_parameter['confluence_password'] = self.confluence_password
		self.build_testing_parameter['et_build_name_or_id'] = self.build_id
		self.build_testing_parameter['parent_page'] = self.parent_page
		self.build_testing_parameter['IS_COVERAGE_NEEDED'] = self.IS_COVERAGE_NEEDED
		self.build_testing_ci_jenkins.build_job(self.build_testing_ci_name, self.build_testing_parameter)
		time.sleep(30)
		new_build_number = self.build_testing_ci_jenkins.get_job_info(self.build_testing_ci_name)['lastBuild']['number']
		if int(new_build_number) > int(old_build_number):
			print "=== the new build testing is running, done ==="
			build_testing_jenkins_url = self.et_jenkins_url + "/job/" + self.build_testing_ci_name + "/" + str(new_build_number)
			print "=== For the jobs details, you can refer to:"
			print build_testing_jenkins_url

if __name__ == "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	confluence_username = sys.argv[3]
	confluence_password = sys.argv[4]
	parent_page = sys.argv[5]
	build_rpm_ci_name = sys.argv[6]
	build_testing_ci_name = sys.argv[7]
	IS_COVERAGE_NEEDED = sys.argv[8]
	monitor = NightCI3Moniter(username, password, confluence_username, confluence_password, parent_page, build_rpm_ci_name, build_testing_ci_name, IS_COVERAGE_NEEDED)
	monitor.get_build_id()
	monitor.run_ci3_build_testing()

