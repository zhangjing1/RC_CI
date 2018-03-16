#/bin/bash
user='wlin'
password="arNdkN47_"
parent_page=30869307
space="~wlin"
test_jenkins_build_name="Trigger_Perf_Testing_Remotely"
et_rc_version="3.16.2.1 git1234"

sudo pip install --upgrade pip
sudo pip install confluence-py
sudo pip install python-jenkins

if [[ $(wget --version | head -1) =~ "GNU Wget" ]]
then
	echo "=====wget has been installed======";
else
	echo "=====wget has not been installed, Would intall git======"
	sudo yum install wget -y
fi

tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
echo "===============Download the CI files under $(pwd)=========="
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI-master
if [[  -e "${tmp_dir}/RC_CI-master/auto_testing_CI" ]]; then
	echo "=======The target file has been found==============="
	cd ${tmp_dir}/RC_CI-master/auto_testing_CI
	echo "=======Generating the confluence page content for rc testing============"
	sudo python generate_rc_report_content.py ${user} ${password} ${test_jenkins_build_name}
	if [[ -e 'content.txt' ]]; then
		echo "==============Done========================="
	else
		echo "==========FAILED to generate the content. Exit with error"
		exit 1
	fi
fi
echo "==========Adding page to confluence==========="
result=$(sudo confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${user} -p ${password}  addpage -n "ET RC ${et_rc_version} Testing Report" -P ${parent_page} -s "${space}" -f 'content.txt')
if [[ ${result} =~ "https" ]]; then
	echo "=========================Done: confluence page generated===================="
	echo "====URL:${result}"
else
	echo "========FAILED: Creating page. Exit with error.===================="
	echo "=========Error info:============"
	echo ${result}
	exit 1
fi

echo "========Removing the useless files==========="
#rm -rf ${tmp_dir}
echo "====================Done=============="

