#/bin/bash
# The script is one backup file which is copied from 'generating bug regression' CI.

#1. get the bugs list
bugs=$(echo ${bugs_link} | cut -d "=" -f 2 | sed  "s/&list_id//" | sed 's/%2C/ /g')
echo "====Bugs: ${bugs}==================="
#2. set the bugzilla username, confluence username
bugzilla_username="${username}@redhat.com"
confluence_username=${username}
echo "The bugzilla account is ${bugzilla_username}, the confluence account is ${confluence_username}"
#3. first install the confluence-py and bugzilla module, then get and run script to generate the conflunce content for the bug page, finally create the page on confluence
sudo pip install confluence-py
sudo pip install bugzilla
sudo pip install requests

tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
echo "===============Download the CI files under $(pwd)=========="
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI-master
if [[  -e "${tmp_dir}/RC_CI-master/bug_regression_CI" ]]; then
	echo "=======The target file has been found==============="
	cd ${tmp_dir}/RC_CI-master/bug_regression_CI
	echo "=======Generating the confluence page content for bugs============"
	sudo python generate_confluence_page_for_bugs.py ${bugzilla_username} ${password} ${bugs}
	if [[ -e 'content.txt' ]]; then
		echo "==============Done========================="
	else
		echo "==========FAILED to generate the content. Exit with error"
		exit 1
	fi
fi
echo "==========Adding page to confluence==========="
result=$(sudo confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${confluence_username} -p ${password}  addpage -n "Bugs Regression Testing - ${et_build_name}" -s ${space} -f 'content.txt')
if [[ ${result} =~ "https" ]]; then
	echo "=========================Done: confluence page generated===================="
	echo "====URL:https://docs.engineering.redhat.com/display/$5/Bugs Regression Testing - $4"
else
	echo "========FAILED: Creating page. Exit with error.===================="
	echo "=========Error info:============"
	echo ${result}
	exit 1
fi
echo "========Removing the useless files==========="
rm -rf ${tmp_dir}
echo "====================Done=============="