import glob
import generate_rc_report_content_for_each_testing_type
import generate_rc_report_content_for_all_testings
class RegenerateRCReport():
	def __init__(self, username, password, et_rc_version)
	self.username = username
	self.password = password
	self.build_name = build_name
	self.et_rc_version = et_rc_version
	self.each_rc_report = ""
	self.build_name_list = ['Trigger_Perf_Testing_Remotely', 'Trigger_RobotFrameWork_UAT_Remotely']
	self.all_rc_report = generate_rc_report_content_for_all_testings.GenerateAllReports()

	def regenerate_report_for_each_test_type(self):
		for build_name in self.build_name_list:
			self.each_rc_report = generate_rc_report_content_for_each_testing_type.GenerateRCReportContent(self.username, self.password, build_name, self.et_rc_version)
			self.each_rc_report.generate_rc_report_for_current_rc_version()

	def regenerate_report_for_all_testings(self):
		all_rc_report.generate_all_reports()

	def run_regenerate(self):
		self.regenerate_report_for_each_test_type()
		self.regenerate_report_for_all_testings()



if __name__== "__main__":
	regenerate_reports= RegenerateRCReport(username, password, build_name,)
	regenerate_reports.run_regenerate()




