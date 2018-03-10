#/bin/python2
import pprint
import bugzilla
import sys

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
	qe_flag = False
	for flag in bug.flags:
		if flag['name'] == "qe_auto_coverage":
			qe_flag = True
			qe_bug_flag = flag['status']
		else:
			next
	bug_flag = qe_bug_flag if qe_flag else ""
		

	formatted_bug = [ bug.id, bug.summary, bug.component, bug.status, bug.severity, bug.priority, bug_flag, bug.qa_contact, bug_result ]
	return formatted_bug

def get_bugs_and_format_bugs(bugs_list):
	formatted_bugs =[]
	for bug in bugs_list:
		formatted_bugs.append(get_bug_and_format_bug(bug))
	return formatted_bugs

def generate_page_content(formmatted_bugs_list):
	table_column = ['ID', 'Summary', 'Component', 'Status', 'Severity', 'Priority', 'Flags', 'QAOwner', 'Result']
	head_row = ""
	for column_name in table_column:
		head_row += "<th colspan='1'>" + column_name +"</th>"
	headrow_html = "<tr>" + head_row + "</tr>"
	bug_rows_html = ""
	for formatted_bug in formmatted_bugs_list:
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
		bug_row += "<td>" + bug_item + "</td>"
	bug_row_html = "<tr>" + bug_id_td_html + bug_row + "</tr>"
	return bug_row_html


def generate_confluence_page_for_bugs(user, password, bugs):
	generate_bugzilla_conf_file(user, password)
	formatted_bugs_list = get_bugs_and_format_bugs(bugs)
	html = generate_page_content(formatted_bugs_list)
	write_page_file(html)
	empty_bugzilla_conf_file()


if __name__== "__main__":
	if len(sys.argv) < 4:
		print len(sys.argv)
		print "===Error===, username, password, bugs parameters are needed!"
	else:
		username = sys.argv[1]
		password = sys.argv[2]
        bugs_list = sys.argv[3:]
        generate_confluence_page_for_bugs(username, password, bugs_list)