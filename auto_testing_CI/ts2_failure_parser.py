from BeautifulSoup import BeautifulSoup
import re
import os

class TS2FailurePaser:
  def __init__(self, failure_html_content):
    self.soup = BeautifulSoup(failure_html_content)
    self.failed_scenarios = []

  def get_failed_scenarios(self):
    failed_scenarios = []
    for elem in self.soup(text=re.compile(r'Scenario')):
      failed_scenarios.append(elem.findNext())
    for failed_scenario in failed_scenarios:
      failed_scenario = str(failed_scenario).replace('<span class="name">','').replace('</span>','')
      self.failed_scenarios.append(failed_scenario)
    return self.failed_scenarios


if __name__ == "__main__":
  file = open("/tmp/overview-failures.html", 'r')
  html_content = file.read()
  file.close()

  soup = TS2FailureParser(html_content)
  soup.get_failed_scenarios()
  print soup.failed_scenarios
