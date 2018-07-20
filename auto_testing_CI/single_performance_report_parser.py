import json
import common_usage
class SinglePerformanceReportParser():
	def __init__(self, input_file):
		one_common_usage = common_usage.CommonUsage()
		one_common_usage.check_file_exist(input_file)
		perf_file = open(input_file,'r')
		perf_file_list = perf_file.readlines()
		perf_file.close()
		perf_file_json = json.loads(perf_file_list[0])
		self.perf_summary = perf_file_json['charts'][0]
		self.transactions = []
		self.transactions_time = []
		self.summary_dict = {}

	def get_all_transactions(self):
		for items in self.perf_summary['rows']:
			transaction = items[0]['value']
			if transaction:
				self.transactions.append(transaction)
		#print self.transactions
	

	def get_all_transactions_average_time(self):
		transactions_time_string = ""
		for items_time in self.perf_summary['rows']:
			# get thei min(90% Line data, average time) to do the comparison, the comparison result
			# should be more correct
			transaction_time = min(items_time[4]['value'], items_time[2]['value'])
			if str(transaction_time):
				self.transactions_time.append(transaction_time)
		#print self.transactions_time

	def get_transactions_time_map(self):
		self.summary_dict = dict(zip(self.transactions, self.transactions_time))

	def run_single_report_parser(self):
		self.get_all_transactions()
		self.get_all_transactions_average_time()
		self.get_transactions_time_map()
		return self.summary_dict

if __name__== "__main__":
	perf = SinglePerformanceReportParser("/tmp/rawdata_1/output/data/subreports/Performance.json")
	perf.run_single_report_parser()
