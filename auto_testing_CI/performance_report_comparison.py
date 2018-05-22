import single_performance_report_parser
import common_usage

class PerformanceReportsComparison():
	def __init__(self, report_1, report_2, tolerance, max_accepted_time):
		report_1_parser = single_performance_report_parser.SinglePerformanceReportParser(report_1)
		report_2_parser = single_performance_report_parser.SinglePerformanceReportParser(report_2)
		self.parsered_report_1 = report_1_parser.run_single_report_parser()
		self.parsered_report_2 = report_2_parser.run_single_report_parser()
		self.worsen_transactions = {}
		self.tolerance = tolerance
		self.comparison_result = ""
		self.max_accepted_time = max_accepted_time

	def compare_reports(self):
		if self.parsered_report_2.keys() == self.parsered_report_1.keys():
			print "=== The Transactions are kept the same ==="
			print "=== Comparing the reports ==="
			self.get_worsen_transactions()
		else:
			print "=== The transactions are different this time ==="
			print "=== Will not do the comparison ===="

	def get_worsen_transactions(self):
		print "== I am filtering out the block transactions if its time exceeds the max_accepted_time and its fallback overs the tolerance"
		for transaction in self.parsered_report_2.keys():
			new_time = self.parsered_report_1[transaction]
			old_time = self.parsered_report_2[transaction]

			if new_time > old_time and new_time > float(self.max_accepted_time):
				increasement = float(new_time) - float(old_time)
				increasement_percentage = increasement / old_time
				print new_time, old_time, increasement_percentage
				if increasement_percentage > float(self.tolerance):
					self.worsen_transactions[transaction] = increasement_percentage

	def comparison_summary(self):
		if len(self.worsen_transactions) == 0 :
			self.comparison_result = "PASSED"
		else:
			self.comparison_result = "FAILED"

	def run_one_comparison(self):
		self.compare_reports()
		self.comparison_summary()



		

if __name__== "__main__":
	perf = PerformanceReportsComparison("/tmp/rawdata_1/output/data/subreports/Performance.json", "/tmp/rawdata_2/output/data/subreports/Performance.json", 0.25)
	perf.compare_reports()
	perf.comparsion_summary()








