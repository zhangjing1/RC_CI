import glob
import sys
import generate_rc_report_content_for_each_testing_type
import generate_rc_report_content_for_all_testings
class RegenerateRCReport():
	def __init__(self, username, password, et_rc_version, file):
		self.username = username
		self.password = password
		self.et_rc_version = et_rc_version
		self.each_rc_report = ""
		self.file = file
		self.build_name_list = ['Trigger_Perf_Testing_Remotely', 'Trigger_RobotFrameWork_UAT_Testing_Remotely', 'Trigger_E2E_Testing', 'Trigger_TS2_UAT_Testing', 'Bug_Regression_Testing']
		self.all_rc_report = generate_rc_report_content_for_all_testings.GenerateAllReports()

	def regenerate_report_for_each_test_type(self):
		for build_name in self.build_name_list:
			self.each_rc_report = generate_rc_report_content_for_each_testing_type.GenerateRCReportContent(self.username, self.password, build_name, self.et_rc_version, self.file)
			self.each_rc_report.generate_rc_report_for_current_rc_version()

	def regenerate_report_for_all_testings(self):
		self.all_rc_report.generate_all_reports()

	def run_regenerate(self):
		self.regenerate_report_for_each_test_type()
		self.regenerate_report_for_all_testings()



if __name__== "__main__":
	username = sys.argv[1]
	password = sys.argv[2]
	et_rc_version = sys.argv[3]
	file = sys.argv[4]
	regenerate_reports= RegenerateRCReport(username, password, et_rc_version, file)
	regenerate_reports.run_regenerate()




