#!/bin/bash
# The script can be used locally to generate rc bug regression
sudo pip install confluence-py
sudo pip install bugzilla
user==$2
password=$3
name=$4
space=%5
bug=$1
tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
echo "===============Download the CI files under $(pwd)"
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI
if [[  -e "${tmp_dir}/RC_CI/bug_regression_CI" ]]; then
	echo "=======The target file has been found==============="
	cd ${tmp_dir}/RC_CI/bug_regression_CI
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