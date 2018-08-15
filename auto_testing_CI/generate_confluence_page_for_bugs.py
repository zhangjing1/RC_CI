#/bin/python2
import pprint
import bugzilla
import sys
import re

'''
    The scripts are used to generate the confluence content for bugs searched from bugzilla.
    The top funcion is 'generate_confluence_page_for_bugs'.
    And it would do the followging steps:
    1. call function to generate the bz account config file.
    2. call function to get bugs and format bugs
    3. call function to generate the confluence content page for the bugs
    4. remove the bz account config file. :)
    The script can be used as 'sudo python generate_confluence_page_for_bugs.py username password '8380529, 123456'
'''

def generate_bugzilla_conf_file(user, password):
	user_account = "[bugzilla.redhat.com]\n" + "user=" + user + "\n" + "password=" + password
	f = open('/etc/bugzillarc', 'w')
	f.write(user_account)
	f.close

def empty_bugzilla_conf_file():
	content = " "
	f = open('/etc/bugzillarc', 'w')
	f.write(content)
	f.close


def get_bug_and_format_bug(bug_id):
	bug_result = ""
	bzapi = bugzilla.Bugzilla("bugzilla.redhat.com")
	bug = bzapi.getbug(int(bug_id))
	# for spike tasks, Let the script add 'qe_auto_coverage' flag automatically if needed
	if bug.summary.find('[Spike]') == 0 and type(bug.get_flags('qe_auto_coverage')) == type(bug.get_flags('abcdefg')):
		# For spike bug, if the 'qe_auto_coverage' flag has not been set, set the flag automatically
		print "Add the flag 'qe_auto_coverage' as '-' to the spike bug {}".format(bug.id)
		auto_flag = {}
		auto_flag['qe_auto_coverage']='-'
		bug.updateflags(auto_flag)
		# refetch the bug
		bug = bzapi.getbug(bug.id)

	# for otherQA bug, Let the script add 'qe_auto_coverage' flag as '-' automatically if needed
	if 'OtherQA' in bug.keywords and type(bug.get_flags('qe_auto_coverage')) == type(bug.get_flags('abcdefg')):
		# For OtherQA bug, if the 'qe_auto_coverage' flag has not been set, set the flag automatically
		print "Add the flag 'qe_auto_coverage' as '-' to the otherQA bug {}".format(bug.id)
		auto_flag = {}
		auto_flag['qe_auto_coverage'] = '-'
		bug.updateflags(auto_flag)
		# refetch the bug
		bug = bzapi.getbug(bug.id)

	qe_flag = False
	for flag in bug.flags:
		if flag['name'] == "qe_auto_coverage":
			qe_flag = True
			qe_bug_flag = flag['status']
		else:
			next
	bug_flag = qe_bug_flag if qe_flag else ""

	# deal with bug.summary: remove unchar letters to avoid the unexpected error when add confluence page
	regex = re.compile('[^a-zA-Z0-9 _\?\[\]{}()]')
	summary = regex.sub('', bug.summary)

	finished_testing_bugs_status = ['RELEASE_PENDING','VERIFIED','CLOSED']
	if bug.status in finished_testing_bugs_status and bug_flag in ['+', '-']:
		bug_result = "PASSED"

	formatted_bug = [ bug.id, summary, bug.component, bug.status, bug.severity, bug.priority, bug_flag, bug.qa_contact, bug_result ]
	return formatted_bug

def get_bugs_and_format_bugs(bugs_list):
	formatted_bugs = []
	for bug in bugs_list:
		formatted_bugs.append(get_bug_and_format_bug(bug))
	return formatted_bugs

# get all passed bug for the second table
def get_formatted_automated_bugs_list(bugs_list):
	formatted_automated_bugs = []
	for bug in bugs_list:
		if bug[8] == "PASSED":
			formatted_automated_bugs.append(bug)
	return formatted_automated_bugs

# get all manual testing bugs for the first table
def get_formatted_manual_bugs_list(bugs_list):
	formatted_manual_bugs = []
	for bug in bugs_list:
		if bug[8] != "PASSED":
			formatted_manual_bugs.append(bug)
	return formatted_manual_bugs


def generate_page_content(formatted_bugs_list):
	table_column = ['ID', 'Summary', 'Component', 'Status', 'Severity', 'Priority', 'qe_auto_coverage', 'QAOwner', 'Result']
	head_row = ""
	for column_name in table_column:
		head_row += "<th colspan='1'>" + column_name +"</th>"
	headrow_html = "<tr>" + head_row + "</tr>"
	bug_rows_html = ""
	for formatted_bug in formatted_bugs_list:
		bug_rows_html += generate_bug_content(formatted_bug)
	table_content = "<table><tbody>" + headrow_html + bug_rows_html + "</tbody></table>"
	return table_content

def write_page_file(table_content):
	f = open('content.txt','w')
	f.write(table_content)
	f.close

def generate_bug_content(formatted_bug):
	bug_row = ""
	bug_id = str(formatted_bug[0])
	bug_details = formatted_bug[1:]
	bug_id_td_html = '<td><a href=' + '"https://bugzilla.redhat.com/show_bug.cgi?id=' + bug_id + '">' + bug_id + "</a></td>"
	for bug_item in bug_details:
		if bug_item == "PASSED":
			bug_row += "<td>" + "<strong><span style='color: rgb(0,128,0);'>" + bug_item + "</span></strong>"  + "</td>"
		else:
			bug_row += "<td>" + bug_item + "</td>"
	bug_row_html = "<tr>" + bug_id_td_html + bug_row + "</tr>"
	return bug_row_html

def generate_confluence_page_for_bugs(user, password, bugs):
	generate_bugzilla_conf_file(user, password)
	formatted_bugs_list = get_bugs_and_format_bugs(bugs)
	formatted_automated_bugs = get_formatted_automated_bugs_list(formatted_bugs_list)
	formatted_manual_bugs = get_formatted_manual_bugs_list(formatted_bugs_list)
	print "-----generate for automated bugs---"
	formatted_automated_bugs_html = generate_page_content(formatted_automated_bugs)
	formatted_manual_bugs_html = generate_page_content(formatted_manual_bugs)
	#info_for_manual_testing = "[Warning] Bugs in the following table have not been covered by automated testing, please verify them manually!"
	#info_for_automated_testing = "[Warning] Bugs in the following table have been covered by automated testing! No more verification needed!"
	info_for_manual_testing_html = '<p>' + "'' and '?' of 'qe_auto_coverage' of the following table means QE have not finished the automation tasks of the bugs." + "<strong>" + " Manual testing is needed! " + "</strong></p>"
	info_for_automated_testing_html = "<p>" + "'-' of 'qe_auto_coverage' of the following table means QE have confirmed that "+ "<strong>" + "no more manual testing is needed." + "</strong>" + " For dev's autoated testing has been covered or it is minor UI change or unimportant negative case can be ingored! "+ '<strong>' + "Mark as 'PASSED' directly!" +'</strong></p>'
	info_for_automated_testing_html += "<p>" + "'+' means QE have completed the automation tasks."  + "<strong>" + "TS2.0 has been covered it. Mark as PASSED directly!" + "</strong></p>"
	page_notice = "'qe_auto_coverage' on the page shows QE automation status for bugs."
	page_notice_html = "<p>" + page_notice + "</p>"
	html = page_notice_html + info_for_manual_testing_html + formatted_manual_bugs_html + info_for_automated_testing_html + formatted_automated_bugs_html
	write_page_file(html)
	empty_bugzilla_conf_file()


if __name__== "__main__":
	print sys.argv
	if len(sys.argv) < 4:
		#print len(sys.argv)
		print "===Error===, username, password, bugs parameters are needed!"
	else:
		username = sys.argv[1]
		password = sys.argv[2]
        bugs_list = sys.argv[3:]
        #print username, password, bugs_list
        generate_confluence_page_for_bugs(username, password, bugs_list)
