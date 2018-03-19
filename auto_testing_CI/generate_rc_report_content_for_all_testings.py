import glob
from shutil import copyfile
#get the file lists
class GenerateAllReports():
	def __init__(self):
		self.general_reports_name = "general_report_content.txt"
		self.general_reports_content = ""
		self.head_column = "<tr><th colspan='1'>Test Type</th><th colspan='1'>Test Result</th><th colspan='1'>Test Result Url</th><th colspan='1'>Test Enviroment</th><th colspan='1'>Comments</th></tr>"
	
	def generate_all_reports(self):
		report_files_list = glob.glob("/tmp/*/RC_CI-master/auto_testing_CI/*_content.txt")
		#report_files_list = glob.glob("*_content.txt")
		if len(report_files_list) == 1:
			print "==== Here just one report, copy it as the general report ===="
			copyfile(report_files_list[0], str(self.general_reports_name))
		elif len(report_files_list) > 1:
			print "==== There are some reports, generate the general report for all testing reports"
			for file in report_files_list:
				print file
				report = open(file)
				report_content = report.read()
				report.close()
				remove_table_head = report_content.replace("<table><tbody>","", 1)
				remove_table_head_column = remove_table_head.replace(self.head_column,'', 1)
				remove_table_end = remove_table_head_column.replace("</tbody></table>",'', 1)
				print self.general_reports_content
				self.general_reports_content += remove_table_end
				print self.general_reports_content

		self.general_reports_content = "<table><tbody>" + self.head_column + self.general_reports_content + "</tbody></table>"
		print self.general_reports_content

		generate_reports = open(str(self.general_reports_name), 'w')
		generate_reports.write(self.general_reports_content)
		generate_reports.close()



if __name__== "__main__":
	generate_all_reports= GenerateAllReports()
	generate_all_reports.generate_all_reports()
