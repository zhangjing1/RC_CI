import glob
from shutil import copyfile
#get the file lists
class GenerateAllReports():
	def __init__(self):
		self.general_reports_name = "general_report_content.txt"
		self.generate_reports_content = ""
	
	def generate_all_reports(self):
		report_files_list = glob.glob("/tmp/*/RC_CI-master/auto_testing_CI/*_content.txt")
		if len(report_files_list) == 1:
			print "==== Here just one report, copy it as the general report ===="
			copyfile(report_files_list[0], str(self.general_reports_name))
		elif len(report_files_list) > 1:
			print "==== There are some reports, generate the general report for all testing reports"
			for file in report_files_list:
				report = open(file)
				report_content = report.read()
				report_content_remove_table_head = report_content.replace("<table><tbody>","", 1)
				report_content_remove_table_end = report_content_remove_table_head.replace("</tbody></table>","", 1)
				self.generate_reports_content += report_content_remove_table_end
				report.close()
			self.general_report_content = "<table<tbody>" + self.generate_reports_content + "</tbody></table>"
			generate_reports = open(str(self.general_reports_name), 'w')
			generate_reports.write(self.generate_reports_content)
			generate_reports.close()



if __name__== "__main__":
	generate_all_reports= GenerateAllReports()
	generate_all_reports.generate_all_reports()
