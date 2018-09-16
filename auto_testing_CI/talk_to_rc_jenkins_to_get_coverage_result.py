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
class TalkToRCCIForTS2Coverage():
  def __init__(self, username, password, build_name):
    self.username = username
    self.password = password
    self.build_name = build_name
    self.server = jenkins.Jenkins(RC_Jenkins, self.username, self.password)
    self.lastest_build_number = 0
    self.console_log_content = ""
    self.coverage =0


  def get_lastest_build_number(self):
    self.lastest_build_number = self.server.get_job_info(self.build_name)['lastBuild']['number']

  def get_ts2_coverage_console_content(self):
    self.console_log_content = self.server.get_build_console_output(self.build_name, self.lastest_build_number)

  def get_TS2_coverage_from_console_content(self):
    self.coverage = re.findall(r'Insert a new row:([^\n]+)', self.console_log_content)[0].strip().split(',')[1].strip().split("'")[1]

  def run_to_get_coverage(self):
    self.get_lastest_build_number()
    self.get_ts2_coverage_console_content()
    self.get_TS2_coverage_from_console_content()

if __name__== "__main__":
  username = sys.argv[1]
  password = sys.argv[2]
  build_name = sys.argv[3]
  talk_to_rc_jenkins = TalkToRCCIForTS2Coverage(username, password, build_name)
  talk_to_rc_jenkins.run_to_get_coverage()


