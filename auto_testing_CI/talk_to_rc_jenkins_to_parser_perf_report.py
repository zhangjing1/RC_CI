import talk_to_rc_jenkins
import common_usage
import performance_report_comparison
import os
import sys

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToRCJenkinsToParserPerfReport():
	def __init__(self, username, password, expected_rc_version, tolerance, max_accepted_time, perf_jmeter_slave_server):
		self.build_name = "Trigger_Perf_Testing_Remotely"
		self.ci_jenkins = talk_to_rc_jenkins.TalkToRCCI(username, password, self.build_name)
		self.ci_jenkins.get_test_report_for_build()
		self.test_report = self.ci_jenkins.test_report
		self.testing_type = self.test_report[0]
		self.testing_result = self.test_report[1]
		self.testing_result_url = self.test_report[2]
		self.current_rc_version = self.ci_jenkins.current_rc_version
		self.expected_rc_version = "ET RC Version: " + expected_rc_version
		self.get_last_successful_build_number = 0
		self.cu = common_usage.CommonUsage()
		self.perf_jmeter_slave_server = perf_jmeter_slave_server
		self.cwd = os.getcwd()
		self.perf_remote_base_path = "/data/jenkins_workspace/workspace/ET_Baseline_PDI/perf-output/builds/"
		self.local_destination_new_report_path = ""
		self.local_destination_old_report_path = ""
		self.worsen_transactions = {}
		self.tolerance = tolerance
		self.max_accepted_time = max_accepted_time


	def parser_current_testing_result(self):
		if self.expected_rc_version != self.current_rc_version:
			print "Expect RC Version: " + self.expected_rc_version
			print "The lastest testing RC Version: " + self.current_rc_version
			print  "========== The latest job is not for the current rc build testing, will not parser the report====="
			return 0
		if self.testing_type != "Performance Baseline Testing":
			print "=== Testing type is not perfomance baseline testing === "
			return 0
		if self.testing_result == "FAILED":
			self.summary_report()
		if self.testing_result == "FINISHED":
			print "=== Scp performance reports from perf jmeter slave== "
			self.scp_perf_builds_reports()
			self.parser_and_comparsion_report()
			self.summary_report()


	def scp_perf_builds_reports(self):
		new_build = self.testing_result_url.split('/')[7]
		old_build = self.testing_result_url.split('/')[10]

		remote_perfomance_new_report_path = self.perf_remote_base_path + str(new_build) + "/report/data/subreports/Performance.json"
		self.local_destination_new_report_path = self.cwd + "/new_performance.json"

		remote_perfomance_old_report_path = self.perf_remote_base_path + str(old_build) + "/report/data/subreports/Performance.json"
		self.local_destination_old_report_path = self.cwd + "/old_performance.json"

		print "=== Scp performance files:"
		print remote_perfomance_old_report_path, "as", self.local_destination_old_report_path
		print remote_perfomance_new_report_path, "as", self.local_destination_new_report_path

		self.cu.python_scp_get_files(self.perf_jmeter_slave_server, remote_perfomance_new_report_path, self.local_destination_new_report_path)
		self.cu.python_scp_get_files(self.perf_jmeter_slave_server, remote_perfomance_old_report_path, self.local_destination_old_report_path)

	def parser_and_comparsion_report(self):
		print "=== Parsering the report ==="
		comparison_parser = performance_report_comparison.PerformanceReportsComparison(self.local_destination_new_report_path, self.local_destination_old_report_path, self.tolerance, self.max_accepted_time)
		comparison_parser.run_one_comparison()
		self.testing_result = comparison_parser.comparison_result
		self.worsen_transactions = comparison_parser.worsen_transactions


	def summary_report(self):
		print "=====================Testing Report: Begin=================="
		print self.expected_rc_version
		print "Testing Type: " + "Performance Baseline Testing"
		print "Testing Result: " + self.testing_result
		print "Testing Report URL: " + self.testing_result_url
		print "=====================Testing Report: End================"
		if len(self.worsen_transactions) > 0:
			print "== The following transactions have block performance fallback: "
			print "Worsen Transactions: ", self.worsen_transactions
		else:
			print "== According to the max_accepted_time and tolerance, there is block performance fallback issues"
			print "== Cheers =="


if __name__== "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	expected_rc_version = sys.argv[3]
	tolerance = sys.argv[4]
	max_accepted_time = sys.argv[5]
	perf_jmeter_slave_server = sys.argv[6]
	perf = TalkToRCJenkinsToParserPerfReport(username, password, expected_rc_version, tolerance, max_accepted_time, perf_jmeter_slave_server)
	perf.parser_current_testing_result()
