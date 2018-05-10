import glob
from shutil import copyfile
#get the file lists
class GenerateAllReports():
	def __init__(self):
		self.general_reports_name = "general_report_content.txt"
		self.general_reports_content = ""
		self.report_files_list = []
		self.head_column = "<tr><th colspan='1'>Test Type</th><th colspan='1'>Test Result</th><th colspan='1'>Test Result Url</th><th colspan='1'>Test Enviroment</th></tr>"
	
	def generate_all_reports(self):
		self.report_files_list = glob.glob("/tmp/*/RC_CI-master/auto_testing_CI/*_content.txt")
		print "==========Find the following report files:=========="
		for file in self.report_files_list:
			print file
		if len(self.report_files_list) == 1:
			print "==== Here just one report, read it as the general report ===="
			general_reports_content_file = open(self.report_files_list[0], 'r')
			general_report_content = general_reports_content_file.readlines()
			general_reports_content_file.close()
			self.general_reports_content = general_report_content[0]
		elif len(self.report_files_list) > 1:
			print "==== There are some reports, generate the general report for all testing reports"
			for file in self.report_files_list:
				print file
				report = open(file)
				report_content = report.read()
				report.close()
				remove_table_head = report_content.replace("<table><tbody>","", 1)
				remove_table_head_column = remove_table_head.replace(self.head_column,'', 1)
				remove_table_end = remove_table_head_column.replace("</tbody></table>",'', 1)
				self.general_reports_content += remove_table_end
			self.general_reports_content = "<table><tbody>" + self.head_column + self.general_reports_content + "</tbody></table>"


if __name__== "__main__":
	generate_all_reports= GenerateAllReports()
	generate_all_reports.generate_all_reports()
