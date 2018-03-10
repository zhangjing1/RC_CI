#!/bin/bash
# The script can be used locally to generate rc bug regression
sudo pip install confluence-py
sudo pip install bugzilla
user==$2
password=$3
name=$4
space=%5
bug=$1
echo 
if [[ -e RC_CI ]]; then
	echo "====Removing the useless dir============"
	rm -rf RC_CI
	echo "=============DONE======================="
fi
echo "======Git clone the scripts=============== "
git clone https://github.com/testcara/RC_CI.git
if [[ -e RC_CI ]];then
	echo "======================DONE=================="
else
	echo "=============FAILED to get the file. Exit With error=========="
	exit 1
fi
dir=$(pwd)
cd ${dir}/RC_CI
if [[  -e "${dir}/RC_CI/bug_regression_CI" ]]; then
	echo "=======The target file has been found==============="
	cd ${dir}/RC_CI/bug_regression_CI
	echo "=======Generating the confluence page content for bugs============"
	sudo python generate_confluence_page_for_bugs.py "${bug}"
	if [[ -e 'content.txt' ]]; then
		echo "==============Done========================="
	else
		echo "==========FAILED to generate the content. Exit with error"
		exit 1
	fi
fi
echo "==========Adding page to confluence==========="
result=$(sudo confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${user} -p ${password}  addpage -n "Bugs Regression Testing - ${name}" -s ${space}-f 'content.txt')
if [[ ${result} =~ "https" ]]; then
	echo "=========================Done: confluence page generated===================="
	echo "====URL:https://docs.engineering.redhat.com/display/$5/Bugs Regression Testing - $4"
else
	echo "========FAILED: Creating page. Exit with error.===================="
	echo "=========Error info:============"
	echo ${result}
	exit 1
fi
