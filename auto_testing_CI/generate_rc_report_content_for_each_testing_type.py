#/bin/env python
import os
import sys
import talk_to_rc_jenkins
import get_all_pub_pulp_product_version_content

class GenerateRCReportContent():
	#first talk to RC CI and then generate the testing report content
	def __init__(self, username, password, build_name, expected_rc_version):
		self.build_name = build_name
		self.ci_jenkins = talk_to_rc_jenkins.TalkToRCCI(username, password, build_name)
		self.ci_jenkins.get_test_report_for_build()
		self.test_report =self.ci_jenkins.test_report
		self.current_rc_version = self.ci_jenkins.current_rc_version
		self.expected_rc_version = "ET RC Version: " + expected_rc_version
		self.test_table_html = ""
		self.head_row_html = ""
		self.test_enviroment_html = ""
		self.test_report_row_html = ""
		self.test_type = ""
		self.perf_env = '''
		<p>ET Server: errata-stage-perf.host.stage.eng.bos.redhat.com</p>
		<p>ET DB: errata-stage-perf-db.host.stage.eng.bos.redhat.com</p>
		'''
		self.robotframework_uat_env = 'ET Server: errata-web-01.host.qe.eng.pek2.redhat.com'
		self.e2e_env = '''
		<p>ET Server: et-e2e.usersys.redhat.com</p>
		<p>Pub Server: pub-e2e.usersys.redhat.com</p>
		<p>pulp Rpm Server: pulp-e2e.usersys.redhat.com</p>
		<p>pulp Docker Server: pulp-docker-e2e.usersys.redhat.com</p>
		<p>Pub and Pulp Versions:</p>
		'''
		self.bug_regression_env = 'ET Server: errata-web-03.host.qe.eng.pek2.redhat.com'
		self.ts2_uat_env = 'ET server: et-system-test-qe-02.usersys.redhat.com'
		self.env_options = ""
		self.get_pub_pulp_content = get_all_pub_pulp_product_version_content.GetAllPubPulpVersionContent(username, password)


	def update_e2e_env_with_pub_pulp(self):
		self.get_pub_pulp_content.get_all_pub_pulp_content()
		self.e2e_env += self.get_pub_pulp_content.all_pub_pulp_content

	def generate_env_options(self):
		self.env_options = {'Performance Baseline Testing':self.perf_env, 'TS2.0 UAT Testing':self.ts2_uat_env,
		                    'RobotFramework UAT Testing':self.robotframework_uat_env, 'E2E Testing':self.e2e_env,
		                    'Bug Regression Testing':self.bug_regression_env}

	def generate_head_row_html(self):
		table_column = ['Test Type', 'Test Result', 'Test Result Url', 'Test Enviroment']
		head_row = ""
		for column_name in table_column:
			head_row += "<th colspan='1'>" + column_name +"</th>"
		self.head_row_html = "<tr>" + head_row + "</tr>"

	def generate_test_report_row_html(self):
		self.test_type = self.test_report[0]
		test_table_row_content_body = ""
		for item in self.test_report:
			if item == "PASSED":
				test_table_row_content_body += "<td>" + "<strong><span style='color: rgb(0,128,0);'>" + item + "</span></strong>" + "</td>"
			if item.find("FAILED") > -1:
				test_table_row_content_body += "<td>" + "<strong><span style='color: rgb(255,0,0);'>" + item + "</span></strong>" + "</td>"
			if item == "IN PROGRESS":
				test_table_row_content_body += "<td>" + "<strong><span style='color: rgb(255,204,0);'>" + item + "</span></strong>" + "</td>"
			if item.find("http") > -1:
				test_table_row_content_body += "<td>" + "<a href='" + item + "'>" + item + "</a>" + "</td>"
			if item.find("Testing") > -1 and item.find("http") <0:
				test_table_row_content_body += "<td>" + item + "</td>"
		test_table_row_content_body += "<td>" + self.env_options[self.test_type] + "</td>"
		self.test_report_row_html = "<tr>" + test_table_row_content_body + "</tr>"

	def generate_test_report_html(self):
		self.update_e2e_env_with_pub_pulp()
		self.generate_env_options()
		self.generate_head_row_html()
		self.generate_test_report_row_html()
		self.test_table_html = "<table><tbody>" + self.head_row_html + self.test_report_row_html + "</tbody></table>"

	def write_page_file(self):
		content_file = self.test_type.replace(' ', "") + "_content.txt"
		f = open(str(content_file),'w')
		f.write(self.test_table_html)
		f.close

	def generate_rc_report_content(self):
		print "===Begin to genreate test report content===="
		self.generate_test_report_html()
		print self.test_table_html
		self.write_page_file()
		print "===End to genreate test report content===="

	def generate_rc_report_for_current_rc_version(self):
		if self.expected_rc_version == self.current_rc_version:
			self.generate_rc_report_content()
		else:
			print "Expect RC Version: " + self.expected_rc_version
			print "The lastest testing RC Version: " + self.current_rc_version
			print  "==========The latest job is not for the current rc build testing, will not generate report====="

if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	if len(sys.argv) ==5 :
		username = sys.argv[1]
		password = sys.argv[2]
		build_name = sys.argv[3]
		et_rc_version = sys.argv[4]
		file = sys.argv[5]
		generate_reprot = GenerateRCReportContent(username, password, build_name, et_rc_version)
		generate_reprot.generate_rc_report_for_current_rc_version()
