import sys
class ParserBuildTestingReport():
	def __init__(self, content):
		self.content_list = content.split("</tr>")
		self.passed_testing = []
		self.failed_testing = []
		self.inprocess_testing = []
		self.testing_type_numbers = len(self.content_list) - 2
		self.final_result = ""
		self.brief_summary=""
		self.result_and_brief = ""

	def get_testing_type_and_result(self):
		for index in range(1, len(self.content_list)-1):
			testing_type = self.content_list[index].split("</td>")[0].split("<td>")[1]
			testing_result = self.content_list[index].split("</td>")[1].split("<td>")[1]
			if testing_result.find("FAILED") > -1:
				self.failed_testing.append(testing_type)
			elif testing_result.find("PASSED") > -1:
				self.passed_testing.append(testing_type)
			else:
				self.inprocess_testing.append(testing_type)

	def summerize_testing_status(self):
		if len(self.passed_testing) == self.testing_type_numbers:
			self.final_result = "PASSED"
		elif len(self.inprocess_testing) > 0:
			self.final_result = "IN PROCESS"
		else:
			self.final_result = "FAILED"

	def get_report_brief(self):
		self.brief_summary = str(self.testing_type_numbers) + " testings: "
		if len(self.inprocess_testing) == 1:
			self.brief_summary += "1 testing in process(" + self.inprocess_testing[0] + "). "
		elif len(self.inprocess_testing) >= 2:
			self.brief_summary += str(len(self.inprocess_testing)) + " in process testings(" + ", ".join(self.inprocess_testing) +"). "
		if len(self.failed_testing) == 1:
			self.brief_summary += "1 failed testing(" + self.failed_testing[0] + ")."
		elif len(self.failed_testing) >=2:
			self.brief_summary += str(len(self.failed_testing)) + " failed testings(" + ", ".join(self.failed_testing) + ")."
		if len(self.passed_testing) == 1:
			self.brief_summary += "1 passed testing(" + self.passed_testing[0] + "). "
		elif len(self.passed_testing) >= 2:
			self.brief_summary += str(len(self.passed_testing)) + " passed testings(" + ", ".join(self.passed_testing) +"). "


	def get_final_status_and_brief(self):
		self.get_testing_type_and_result()
		self.summerize_testing_status()
		self.get_report_brief()
		self.result_and_brief = self.final_result + "-" + self.brief_summary


if __name__== "__main__":
	report_parser = ParserBuildTestingReport(sys.argv[1])
	report_parser.get_final_status_and_brief()