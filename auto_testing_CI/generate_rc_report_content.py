#/bin/env python
import talk_to_rc_jenkins
class GenerateRCReportContent():
	#first talk to RC CI and then generate the testing report content
	def __init__(self, build_name):
		self.build_name = build_name
		self.ci_jenkins = talk_to_rc_jenkins.TalkToRCCI(username, password, build_name)
		self.ci_jenkins.get_test_report_for_build()
		self.test_report =self.ci_jenkins.test_report
		self.test_table_html = ""
		self.head_row_html = ""
		self.test_report_row_html = ""

	def generate_head_row_html(self):
		table_column = ['Test Type', 'Test Result', 'Test Result Url', 'Comments']
		head_row = ""
		for column_name in table_column:
			head_row += "<th colspan='1'>" + column_name +"</th>"
		self.head_row_html = "<tr>" + head_row + "</tr>"

	def genreate_test_report_row_html(self):
		test_report_list = test_report.split()
		test_table_row_content_body = ""
		test_table_row_content = ""
		for item in test_report_list:
			test_table_row_content_body += "<td>" + item + "</td>"
		test_report_row_html = "<tr>" + test_table_content_body + "</tr>"

	def generate_test_reprot_html(self):
		self.generate_head_row_html()
		self.genreate_test_report_row_html()
		self.test_table_html = "<table><tbody>" + self.head_row_html + self.genreate_test_report_row_html + "</tbody></table>"

	def write_page_file(self):
		f = open('content.txt','w')
		f.write(self.test_table_html)
		f.close

	def generate_rc_reprot_content(self):
		self.genreate_test_report_row_html()
		self.write_page_file()

if __name__== "__main__":
	#print len(sys.argv)
	#print sys.argv
	username = os.environ.get('ET_RC_User')
	password = os.environ.get('ET_RC_User_Password')
	if len(sys.argv) ==2 :
		build_name = sys.argv[1]
		generate_reprot = GenerateRCReportContent(username, password, build_name)
		generate_reprot.generate_rc_reprot_content()


	
