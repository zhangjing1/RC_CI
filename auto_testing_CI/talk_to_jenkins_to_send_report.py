#/bin/env python
import jenkins
import time
import sys
import os

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToCIToSendReport():
	def __init__(self, username, password, build_name, et_build_name_or_id, status, brief_summary, space):
		self.username = username
		self.password = password
		self.build_name = build_name
		self.space = space
		self.server = jenkins.Jenkins(RC_Jenkins, self.username, self.password)
		self.et_build_name_or_id = et_build_name_or_id
		self.status = status
		self.brief_summary = brief_summary
		self.previous_last_completed_build_number = 0
		self.last_completed_build_number = 0


	def run_build(self):
		print "===Start to send report==="
		self.server.build_job(self.build_name,  {'et_build_name_or_id': self.et_build_name_or_id, 'status': self.status, 'brief_summary': self.brief_summary, 'space': self.space})

	def get_last_completed_build_number(self):
		self.last_completed_build_number = self.server.get_job_info(self.build_name)['lastCompletedBuild']['number']

	def get_new_build_number(self):
		# we give the jenkins 30s to send out the report
		self.previous_last_completed_build_number = self.last_completed_build_number
		time.sleep(10)
		self.get_last_completed_build_number()
		if self.previous_last_completed_build_number < self.last_completed_build_number:
			print "=== The new job has been generated ==="

	def send_mail_successfully_or_not(self):
		print self.server.get_build_info(self.build_name, self.last_completed_build_number)['result']

	def run_send_report(self):
		self.get_last_completed_build_number()
		self.run_build()
		self.get_new_build_number()
		self.send_mail_successfully_or_not()


if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	username = sys.argv[1]
	password = sys.argv[2]
	build_name = sys.argv[3]
	et_build_name_or_id = sys.argv[4]
	status = sys.argv[5]
	brief_summary = sys.argv[6]
	space = sys.argv[7]
	talk_to_jenkins = TalkToCIToSendReport(username, password, build_name, et_build_name_or_id, status, brief_summary, space)
	talk_to_jenkins.run_send_report()


