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
    self.failure_detailed_report=""
    self.pending_scenarios_report=""
    self.general_report = ""
    self.send_report_ci = 'ts2.0_failure_hunter_send_reports'

  def get_lastest_build_number(self):
    self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

  def get_ts2_console_content(self):
    self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

  def parser_ts2_cucumber_report_for_failures(self):
    self.et_build_version = re.search(r"ET RC Version: (\d+)", self.console_log_content).group(1)
    self.TS2_testing_result = re.search(r"Testing Result: (\w+)", self.console_log_content).group(1)
    self.TS2_testing_report_url = re.search(r"Testing Report URL: (.*$)", self.console_log_content, re.MULTILINE).group(1)
    if self.TS2_testing_result == "PASSED":
      print "==== The TS2.0 testing run has been PASSED, No failure hunter is needed. Cheers!"
    else:
      if re.search(r"console", self.TS2_testing_report_url):
        self.TS2_testing_result = "ERROR"
        print "==== Something happens unexpectedly. The cucumber report is not avaiable. No failure hounter is needed. Cheers! Anyway."
      else:
        self.TS2_testing_result = "FAILED"
        print "==== Hunting the failure owners"
        self.TS2_testing_report_url = self.TS2_testing_report_url.replace('overview-features','overview-failures')
        cucumber_failure_report_html = requests.get(self.TS2_testing_report_url, auth=(self.username, self.password), verify=False).content
        ts2_report_parser = ts2_failure_parser.TS2FailurePaser(cucumber_failure_report_html)
        self.failed_scenarios = ts2_report_parser.get_failed_scenarios()
        os.system('git clone https://code.engineering.redhat.com/gerrit/errata-rails')
        path = os.getcwd() + '/errata-rails'
        os.chdir(path)
        os.chmod(path, 777)
        os.system('git checkout develop')
        for scenario in self.failed_scenarios:
            get_feature_file_command = 'grep -r -i "' + scenario + '" features ' + ' | sort -u | cut -d ":" -f 1'
            feature_file = commands.getoutput(get_feature_file_command)
            get_failure_owner_command = 'git blame ' + feature_file + ' | grep "' + scenario + '"'
            self.failure_detailed_report += commands.getoutput(get_failure_owner_command) + "\n"
        print "=== The failure hunter has got the failures owners for failures"

  def collect_pending_scenarios(self):
        print "=== begin to hunter the disabled/pending features/scenarios. As usual, these cases are not run by TS2.0"
        get_pending_scenarios = 'grep -r -i "@disable" -A1 -B1'
        self.pending_scenarios_report = commands.getoutput(get_pending_scenarios)
        print "=== The pending scenarios hunter has got the pending lists"

  def format_hunter_report(self):
    print "=== Begin to format the hunter report"
    failure_report_header = "==================== TS2.0 Hunter Reports for TS2.0 Failed Scenarios ===================="
    if self.TS2_testing_result == "PASSED":
        failure_report_general = "No failures, no failure hunters, Cheers!\n"
        failure_report_details_general = ""
        failure_report_details = ""
    if self.TS2_testing_result == "ERROR":
        failure_report_general = "Something happens unexpectedly. The cucumber report is not avaiable. No failure hounter is needed.\n"
        failure_report_details_general = "Please check the report directly, " + str(self.TS2_testing_report_url) + "\n"
        failure_report_details = ""
    if self.TS2_testing_result == "FAILED":
        failure_report_general = "Generally, " + str(len(self.failed_scenarios)) + " scenarios Failed. If the count > 10, It should be environmental problems!\n"
        failure_report_details_general = "See the details below, commit, owner, scenario will be listed\n"
        failure_report_details = self.failure_detailed_report
    pending_report_header = "==================== TS2.0 Hunter Reports for TS2.0 Pending Scenarios ===================="
    pending_report_general = "Reminder: TS2.0 does not run those cases. Please clean them or run them manually for RC build.\n"
    pending_report_details = self.pending_scenarios_report
    report_end = "====================================== Report Ends =====================================\n"
    self.general_report = "<strong><font size='3'>" +  failure_report_header + "</font></strong><pre>" + failure_report_general + failure_report_details_general + "\n" + \
                          failure_report_details + "</pre><strong><font size='3'>" + pending_report_header + "</font></strong><pre>" + \
                          pending_report_general + "--\n"+ pending_report_details + "</pre><strong><font size='3'>" + report_end + "</font></strong>"
    print "=== Done to format the hunter report"

  def send_report_out(self):
    print "=== Begin to send the hunter output"
    send_report_ci = talk_to_jenkins_to_send_ts2_hunter_report.TalkToCIToSendReport(self.username, self.password, self.send_report_ci, \
              self.et_build_version, self.TS2_testing_report_url, self.general_report)
    send_report_ci.run_send_report()
    print "=== Done to send the hunter output"

  def run_ts2_hunter(self):
    self.get_lastest_build_number()
    self.get_ts2_console_content()
    self.parser_ts2_cucumber_report_for_failures()
    self.collect_pending_scenarios()
    self.format_hunter_report()
    self.send_report_out()

if __name__== "__main__":
  username = sys.argv[1]
  password = sys.argv[2]
  build_name = sys.argv[3]
  talk_to_rc_jenkins = TalkToRCCIForTS2Failure(username, password, build_name)
  talk_to_rc_jenkins.run_ts2_hunter()


