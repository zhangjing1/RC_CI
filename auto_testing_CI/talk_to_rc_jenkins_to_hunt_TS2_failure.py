#/bin/env python
# -*- coding: utf-8 -*-
import jenkins
import time
import re
import os
import commands
import sys
import requests
import ts2_failure_parser
import talk_to_jenkins_to_send_ts2_hunter_report

RC_Jenkins = os.environ.get("RC_Jenkins_URL") or "https://errata-jenkins.rhev-ci-vms.eng.rdu2.redhat.com"
class TalkToRCCIForTS2Failure():
  def __init__(self, username, password, build_name):
    self.username = username
    self.password = password
    self.build_name = build_name
    self.server = jenkins.Jenkins(RC_Jenkins, self.username, self.password)
    self.et_build_version = ""
    self.lastest_build_number = 0
    self.TS2_testing_report_url = ""
    self.TS2_testing_result = ""
    self.TS2_testing_console_log_url = ""
    self.console_log_content = ""
    self.failed_scenarios = []
    self.failure_detailed_report = ""
    self.failure_report = ""
    self.pending_report = ""
    self.pending_scenarios_report=""
    # add variables for coverage report
    self.coverage_report = ""
    self.coverage_result = ""
    self.is_coverage_testing = False
    self.general_report = ""
    self.send_report_ci = 'ts2.0_failure_hunter_send_reports'
    th_content = ['Owner', 'Commit', 'Commit Time', 'Scenario']
    self.th_html = ''.join(["<th>{}</th>".format(content) for content in th_content])

  def get_lastest_build_number(self):
    self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

  def get_ts2_console_content(self):
    self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

  def parser_ts2_cucumber_report_for_failures(self):
    self.et_build_version = re.search(r"ET RC Version: (\d+)", self.console_log_content).group(1)
    self.TS2_testing_result = re.search(r"Testing Result: (\w+)", self.console_log_content).group(1)
    self.TS2_testing_report_url = re.search(r"Testing Report URL: (.*$)", self.console_log_content, re.MULTILINE).group(1)
    th_header = "<h1>TS2.0 Hunter Reports for TS2.0 Failed Scenarios</h1>"
    if self.TS2_testing_result == "PASSED":
      print "==== The TS2.0 testing run has been PASSED, No failure hunter is needed. Cheers!"
      th_summary = "<p>The TS2.0 testing run has been PASSED! No more info is provided! Cheers!</p>"
      self.th_html = ""
    else:
      if re.search(r"console", self.TS2_testing_report_url):
        self.TS2_testing_result = "ERROR"
        print "==== Something happens unexpectedly. The cucumber report is not avaiable. "
        th_summary = "<p>Error! Cucumber report is not avaible. See the console log: {} </p>".format(self.TS2_testing_report_url)
        self.th_html = ""
      else:
        self.TS2_testing_result = "FAILED"
        print "==== Hunting the failure owners"
        self.TS2_testing_report_url = self.TS2_testing_report_url.replace('overview-features','overview-failures')
        cucumber_failure_report_html = requests.get(self.TS2_testing_report_url, auth=(self.username, self.password), verify=False).content
        ts2_report_parser = ts2_failure_parser.TS2FailurePaser(cucumber_failure_report_html)
        self.failed_scenarios = ts2_report_parser.get_failed_scenarios()
        for scenario in self.failed_scenarios[:30]:
            get_feature_file_command = 'grep -r -i "' + scenario + '" features ' + ' | sort -u | cut -d ":" -f 1'
            feature_file = commands.getoutput(get_feature_file_command)
            get_failure_owner_command = 'git blame ' + feature_file + ' | grep "' + scenario + '"'
            failed_scenarios_info = commands.getoutput(get_failure_owner_command)
            failed_scenarios_info = self.format_one_blame(failed_scenarios_info)
            failed_scenarios_info_td = ""
            for content in failed_scenarios_info:
                failed_scenarios_info_td += "<td>{}</td>".format(content.strip())
            self.failure_detailed_report += "<tr>{}<tr>".format(failed_scenarios_info_td)

        feature_report_url = self.TS2_testing_report_url.replace("failures", "features")
        th_summary = "<p>Generally, " + str(len(self.failed_scenarios)) + " scenarios are failed. The report can show 30 scenarios at most. You can reach" + "<a href='{}'> the original report</a> for details.</p>".format(feature_report_url)

    self.failure_report = th_header + th_summary + "<table>{}{}</table>".format(self.th_html, self.failure_detailed_report)
    print "=== The failure hunter has got the failures owners for failures"

  def collect_pending_scenarios(self):
        print "=== begin to hunter the disabled/pending features/scenarios. As usual, these cases are not run by TS2.0"
        get_pending_scenarios = 'grep -r -i "@disable" -A1 -B1'
        #get_pending_scenarios = 'grep -r -i "@pending" -A1 -B1'
        pending_scenarios_report = commands.getoutput(get_pending_scenarios)
        # Let us show more info in the pending report and make it much nicer
        split_report = pending_scenarios_report.split('--')
        # Let us get the scenarios count
        feature_count = 0
        scenario_count_without_feature = scenario_count = len(split_report) - 2
        split_report[0]="\n{}".format(split_report[0])
        split_report[-1]="{}\n".format(split_report[-1])

        pending_list = []
        for report in split_report:
            if report.count('\n') < 3:
                pass
            else:
                pending_list.append(report.split("\n")[-2].replace('feature-F','feature-  F').split("-  ")[1])

        #format pending_list, remove the feature and add all scenarios into the feature
        for pending in pending_list:
            get_feature_file_command = 'grep -r -i "{}" features | sort -u | cut -d ":" -f 1'.format(pending)
            feature_file = commands.getoutput(get_feature_file_command)
            if re.findall('Feature', pending) != []:
                # for feature file, let us get the scenarios then show all owners
                get_all_scenarios_of_files_command = "grep -r -i 'Scenario' {} | sed 's/^  //1'".format(feature_file)
                scenarios_list_for_feature = commands.getoutput(get_all_scenarios_of_files_command).split("\n")
                pending_list.remove(pending)
                pending_list += scenarios_list_for_feature

        for pending in pending_list:
            get_feature_file_command = 'grep -r -i "{}" features | sort -u | cut -d ":" -f 1'.format(pending)
            feature_file = commands.getoutput(get_feature_file_command)
            get_pending_owner_command = 'git blame {} | grep "{}"'.format(feature_file, pending)
            pending_scenarios_info = commands.getoutput(get_pending_owner_command)
            pending_scenarios_info = self.format_one_blame(pending_scenarios_info)
            pending_scenarios_info_td = ""
            for content in pending_scenarios_info:
                pending_scenarios_info_td += "<td>{}</td>".format(content)
            self.pending_scenarios_report += "<tr>{}</tr>".format(pending_scenarios_info_td)

        th_header = "<h1>TS2.0 Hunter Reports for TS2.0 Pending Scenarios</h1>"
        if len(pending_list) > 0:
            th_summary = "<p>Generally, {} scenarios are pending. Please help to clean them ASAP, otherwise we need to run them manually for RC build.</p>".format( \
                          len(pending_list), scenario_count_without_feature, feature_count)
        else:
            th_summary ="<p>There is no pending scenarios! No more info is provided! Cheers!</p>"
            self.th_html = ""

        self.pending_report = th_header + th_summary + '<table>' + self.th_html + self.pending_scenarios_report + '</table>'
        print "=== The pending scenarios hunter has got the pending lists"


  def parser_ts2_cucumber_report_for_coverage(self):
    self.is_coverage_testing = re.search(r"Is_Coverage_Testing: (\w+)", self.console_log_content).group(1)
    self.coverage_result =  re.search(r"Coverage Result: ([^\n]+)", self.console_log_content).group(1)
    self.coverage_report_url = re.search(r'General Coverage Report: (\w+:+/+\w+.+)',self.console_log_content).group(1)
    th_header = "<h1> TS2.0 Hunter Reports for TS2.0 Coverage Testing</h1>"
    th_summary = "<p>Is_Coverage_Testing: {}</p>".format(self.is_coverage_testing.capitalize())
    th_summary = th_summary + "<p>The current/latest coverage result: {}</p>".format(self.coverage_result)
    th_summary = th_summary + "Reminder: You can get the general coverage trend by the" + " <a href='{}'>".format(self.coverage_report_url) + \
                   "coverge google sheet" + "</a>"
    self.coverage_report = th_header + th_summary


  def format_one_blame(self, scenario_info):
      scenarios_info = scenario_info.replace('(',')').split(')')
      scenarios_info[:] = [item.strip() for item in scenarios_info]
      commit = scenarios_info[0].split(" ")[0]
      owner_and_time_list = re.split(r'([a-zA-Z ]+)', scenarios_info[1])
      owner_and_time_list[:] = [ item for item in owner_and_time_list if item != '' ]
      owner = owner_and_time_list[0]
      time = owner_and_time_list[1]
      scenario = scenarios_info[2]
      return [owner, commit, time, scenario]


  def format_hunter_report(self):
    print "=== Begin to format the hunter report"
    html_css_start = '''
    <html>
    <body>
    <style>
    table, th, td {
    border: 1px solid black;
    padding: 3px
    }
    table {
    width:80%
    }
    </style>
    '''
    html_css_end = '''
    </body>
    </html>
    '''

    cheers = "<br><p>Reminder: The report is provided by QE 'TS2.0 Hunter CI' automatically. Please do not reply it directly.<p>"
    self.general_report = html_css_start +  self.failure_report + self.pending_report + self.coverage_report+ html_css_end + cheers
    print self.general_report
    print "=== Done to format the hunter report"

  def send_report_out(self):
    print "=== Begin to send the hunter output"
    send_report_ci = talk_to_jenkins_to_send_ts2_hunter_report.TalkToCIToSendReport(self.username, self.password, self.send_report_ci, \
              self.et_build_version, self.TS2_testing_report_url, self.general_report)
    send_report_ci.run_send_report()
    print "=== Done to send the hunter output"

  def prepare_errata_rails_features_data(self):
      os.system('git clone https://code.engineering.redhat.com/gerrit/errata-rails')
      path = os.getcwd() + '/errata-rails'
      os.chdir(path)
      os.chmod(path, 777)
      os.system('git checkout develop')

  def run_ts2_hunter(self):
    self.get_lastest_build_number()
    self.get_ts2_console_content()
    self.prepare_errata_rails_features_data()
    self.parser_ts2_cucumber_report_for_failures()
    self.collect_pending_scenarios()
    self.parser_ts2_cucumber_report_for_coverage()
    self.format_hunter_report()
    self.send_report_out()

if __name__== "__main__":
  username = sys.argv[1]
  password = sys.argv[2]
  build_name = sys.argv[3]
  talk_to_rc_jenkins = TalkToRCCIForTS2Failure(username, password, build_name)
  talk_to_rc_jenkins.run_ts2_hunter()


