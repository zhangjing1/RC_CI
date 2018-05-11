import parser_build_testing_report
import talk_to_jenkins_to_send_report
import confluence_client
import sys

class TalkToJennkinsToParserResultAndSentReports():
	def __init__(self, username, password, et_build_version, title, space, send_report_jenkins_name):
		self.username = username
		self.password = password
		self.et_build_version = et_build_version
		self.title = title
		self.space = space
		self.send_report_jenkins_name = send_report_jenkins_name
		self.confluence_auto_client = confluence_client.ConfluenceClient(self.username, self.password, self.title, self.space, "", "")
		self.testing_report_content = ""
		self.testing_final_result = ""
		self.testing_final_summary = ""

	def get_testing_report_content(self):
		self.confluence_auto_client.get_page_content()
		self.testing_report_content = self.confluence_auto_client.content

	def parser_builds_report(self):
		build_parser = parser_build_testing_report.ParserBuildTestingReport(self.testing_report_content)
		build_parser.get_final_status_and_brief()
		self.testing_final_result = build_parser.final_result
		self.testing_final_summary = build_parser.brief_summary

	def talk_to_jenkins_to_send_report_out(self):
		send_reporter = talk_to_jenkins_to_send_report.TalkToCIToSendReport(self.username, self.password, self.send_report_jenkins_name, self.et_build_version, self.testing_final_result, self.testing_final_summary, self.space)
		send_reporter.run_send_report()

	def run_parser_and_send_report(self):
		print "==== Getting the testing report content ===="
		self.get_testing_report_content()
		print "==== Parsering the build testing reprot ===="
		self.parser_builds_report()
		print "==== Sending the report out ===="
		self.talk_to_jenkins_to_send_report_out()
		print "==== Done ====="

if __name__ == "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	et_build_version = sys.argv[3]
	title = sys.argv[4]
	space = sys.argv[5]
	send_report_jenkins_name = sys.argv[6]
	parser_and_sender = TalkToJennkinsToParserResultAndSentReports(username, password, et_build_version, title, space, send_report_jenkins_name)
	parser_and_sender.run_parser_and_send_report()
