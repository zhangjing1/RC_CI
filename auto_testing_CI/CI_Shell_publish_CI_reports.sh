#/bin/bash
parent_page=30869307
space="~wlin"
et_rc_version="3.16.2.1 git1234"


#check the rc report content has been generated.
check_report_content_file_exist() {
	if [[ -e "${1}/RC_CI-master/auto_testing_CI/general_report_content.txt" ]]; then
		echo "=============The general report content has been generated==========="
	else
		echo "=============There is no general_report_content to publish report======"
		echo "=============Failed ==================================================="
		exit 1
	fi
}

install_scripts_env() {
	sudo pip install --upgrade pip
	sudo pip install confluence-py
	sudo pip install python-jenkins
	if [[ $(wget --version | head -1) =~ "GNU Wget" ]]; then
		echo "=====wget has been installed======";
	else
		echo "=====wget has not been installed, Would intall git======"
		sudo yum install wget -y
	fi
}

add_update_page_result(){
	if [[ ${1} =~ "https" ]]; then
		echo "=========================Done: confluence page generated===================="
		echo "====URL:${1}"
	else
		echo "========FAILED: Creating page. Exit with error.===================="
		echo "=========Error info:============"
		echo ${1}
		exit 1
	fi
}

install_scripts_env()

tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
echo "===============Download the CI files under $(pwd)=========="
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI-master/auto_testing_CI
# first check the page exists or not, if not, generate for all content
echo "==============All files had beeen Download==============="
echo "=============Firstly, let us check the page existing or not"
result=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u 'wlin' -p 'arNdkN47_'  getpagesummary -n "ET RC Testing Report ${et_rc_version}"  -s ${space})
if [[ "${result}" =~ "You're not allowed to view that page, or it does not exist."]] ; then
	echo "=========It does  not exist. Will generate the testing report and add page for it"
	echo "generate_rc_report_content_for_all_testing"
	sudo python generate_rc_report_content_for_all_testing.py 
	check_report_content_file_exist()  ${tmp_dir}
	result_add_page=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u 'wlin' -p 'arNdkN47_'  addpage -n "ET RC Testing Report ${et_rc_version}"  -s ${space} -f "general_report_content.txt")
    add_update_page_result() ${result_add_page}
else
	echo "=========The page has been created, would regenerate the report content=============="
	sudo python regenerate_rc_report_content_for_all_testing.py
	check_report_content_file_exist() ${tmp_dir}
	# delete the original report page and generate the new one
	$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u 'wlin' -p 'arNdkN47_'  removepage -n "ET RC Testing Report ${et_rc_version}"  -s ${space} -f "general_report_content.txt")
	if [[ $(echo $?) -gt 0 ]]; then
		echo "==========Regenerate the testing report====================="
		result_update_page=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u 'wlin' -p 'arNdkN47_'  addpage -n "ET RC Testing Report ${et_rc_version}"  -s ${space} -f "general_report_content.txt")
		add_update_page_result() ${result_update_page}
	fi
fi

sudo find /tmp  -name "*_content.txt" | xargs rm -rf {}
