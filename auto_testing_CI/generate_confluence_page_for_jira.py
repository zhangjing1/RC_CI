#/bin/python2
import pprint
import sys
import re
from jira import JIRA

'''
    The scripts are used to generate the confluence content for jiras searched from jira.
    The top funcion is 'generate_confluence_page_for_jiras' and the parameter is the fix_version in jira issue
    And it would do the followging steps:
    1. call function to get jiras and format jiras
    2. Update qe_auto_coverage for the Spike and OtherQA issue to '-' if it has not been set
    3. Call function to generate the confluence content page for the jiras, the parameter for jira query should be fix_version, like '3.18.0-1'
    The script can be used as 'sudo python generate_confluence_page_for_jira.py "<username>" "<password>" "3.18.1-0"
'''

def get_issue_and_format_issue(issue):
    issue_result = ''
    issue_qe_auto_coverage = ''
    # for spike tasks, Let the script add 'qe_auto_coverage' flag '-' automatically if it is not set yet
    if issue.fields.summary.find('[Spike]') == 0 and issue.fields.customfield_13700 == None:
        print "Add the flag 'qe_auto_coverage' as '-' to the spike jira {}".format(issue.key)
        issue.update(fields={'customfield_13700': {'value': '-'}})

    # for otherQA bug, Let the script add 'qe_auto_coverage' flag as '-' automatically if it is not set yet
    if 'OtherQA' in issue.fields.labels and issue.fields.customfield_13700 == None:
        print "Add the flag 'issue_qe_auto_coverage' as '-' to the otherQA jira {}".format(issue.key)
        issue.update(fields={'customfield_13700': {'value': '-'}})

    # deal with jira issue summary: remove unchar letters to avoid the unexpected error' when add confluence page
    regex = re.compile('[^a-zA-Z0-9 _\?\[\]{}()]')
    summary = regex.sub('', issue.fields.summary)

    finished_testing_issues_status = ['Resolved','Closed','Done','Verified']

    # customfield_13700 is customed qe_auto_coverage
    if issue.fields.customfield_13700:
        issue_qe_auto_coverage = issue.fields.customfield_13700.value
    else:
        issue_qe_auto_coverage = ""

    if issue.fields.status.name in finished_testing_issues_status and issue_qe_auto_coverage in ['+', '-']:
        issue_result = 'PASSED'

    if issue.fields.components:
        issue_component = issue.fields.components[0].name
    else:
        issue_component = ''

    if issue.fields.customfield_11704:
    	issue_qe_contact = issue.fields.customfield_11704.name
    else:
    	issue_qe_contact = ''

    formatted_issue = [ issue.key, summary, issue_component, issue.fields.priority.name, issue.fields.status.name, issue_qe_auto_coverage, issue_qe_contact, issue_result ]
    return formatted_issue

def get_issues_and_format_issues(user, password, fix_version):
    jira_url = "https://projects.engineering.redhat.com"
    jira = JIRA(jira_url, basic_auth=(user, password))

    issues_list = jira.search_issues('project = ERRATA AND fixVersion = ' + fix_version)
    formatted_issues = []
    for issue in issues_list:
        formatted_issues.append(get_issue_and_format_issue(issue))
    return formatted_issues

# get all passed jira for the second table
def get_formatted_automated_issues_list(issues_list):
    formatted_automated_issues = []
    for issue in issues_list:
        if issue[7] == "PASSED":
           formatted_automated_issues.append(issue)
    return formatted_automated_issues

# get all manual testing jiras for the first table
def get_formatted_manual_issues_list(issues_list):
    formatted_manual_issues = []
    for issue in issues_list:
        if issue[7] != "PASSED":
            formatted_manual_issues.append(issue)
    return formatted_manual_issues


def generate_page_content(formatted_issues_list):
    table_column = ['ID', 'Summary', 'Component', 'Priority', 'Status', 'qe_auto_coverage', 'QAOwner', 'Result']
    head_row = ""
    for column_name in table_column:
        head_row += "<th colspan='1'>" + column_name +"</th>"
    headrow_html = "<tr>" + head_row + "</tr>"
    issue_rows_html = ""
    for formatted_issue in formatted_issues_list:
        issue_rows_html += generate_issue_content(formatted_issue)
    table_content = "<table><tbody>" + headrow_html + issue_rows_html + "</tbody></table>"
    return table_content

def write_page_file(table_content):
    f = open('content.txt','w')
    f.write(table_content)
    f.close

def generate_issue_content(formatted_issue):
    issue_row = ""
    issue_key = str(formatted_issue[0])
    issue_details = formatted_issue[1:]
    issue_key_td_html = '<td><a href=' + '"https://projects.engineering.redhat.com/browse/' + issue_key + '">' + issue_key + "</a></td>"
    for issue_item in issue_details:
        if issue_item == "PASSED":
            issue_row += "<td>" + "<strong><span style='color: rgb(0,128,0);'>" + issue_item + "</span></strong>"  + "</td>"
        else:
            issue_row += "<td>" + issue_item + "</td>"
    issue_row_html = "<tr>" + issue_key_td_html + issue_row + "</tr>"
    return issue_row_html

def generate_confluence_page_for_issues(user, password, fix_version):
    formatted_issues_list = get_issues_and_format_issues(user, password, fix_version)
    formatted_automated_issues = get_formatted_automated_issues_list(formatted_issues_list)
    formatted_manual_issues = get_formatted_manual_issues_list(formatted_issues_list)
    print "-----generate for automated issues---"
    formatted_automated_issues_html = generate_page_content(formatted_automated_issues)
    formatted_manual_issues_html = generate_page_content(formatted_manual_issues)
    #info_for_manual_testing = "[Warning] jiras in the following table have not been covered by automated testing, please verify them manually!"
    #info_for_automated_testing = "[Warning] jiras in the following table have been covered by automated testing! No more verification needed!"
    info_for_manual_testing_html = '<p>' + "'' and '?' of 'qe_auto_coverage' of the following table means QE have not finished the automation tasks of the jira issues." + "<strong>" + " Manual testing is needed! " + "</strong></p>"
    info_for_automated_testing_html = "<p>" + "'-' of 'qe_auto_coverage' of the following table means QE have confirmed that "+ "<strong>" + "no more manual testing is needed." + "</strong>" + " For dev's autoated testing has been covered or it is minor UI change or unimportant negative case can be ingored! "+ '<strong>' + "Mark as 'PASSED' directly!" +'</strong></p>'
    info_for_automated_testing_html += "<p>" + "'+' means QE have completed the automation tasks."  + "<strong>" + "TS2.0 has been covered it. Mark as PASSED directly!" + "</strong></p>"
    page_notice = "'qe_auto_coverage' on the page shows QE automation status for jira issues."
    page_notice_html = "<p>" + page_notice + "</p>"
    html = page_notice_html + info_for_manual_testing_html + formatted_manual_issues_html + info_for_automated_testing_html + formatted_automated_issues_html
    # print html
    write_page_file(html)
    print "Done!"


if __name__== "__main__":
    print sys.argv
    if len(sys.argv) < 3:
        #print len(sys.argv)
        print "===Error===, username, password, jiras issue fix version are needed!"
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        fix_version = sys.argv[3]
        #print username, password, jiras_list
        generate_confluence_page_for_issues(username, password, fix_version)
