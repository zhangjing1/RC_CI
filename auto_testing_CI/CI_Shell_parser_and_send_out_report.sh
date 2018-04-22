#!/bin/bash
# the script will do the following steps:
# 1. get the build report
# 2. parser the report then trigger the sending report CI
# 3. mail is sent out by sending report CI
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

install_scripts_env
tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
# Wget the files
echo "===============Download the CI files under $(pwd)=========="
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI-master/auto_testing_CI
# Run the script
echo "==============Start the testing==============="
echo "==============Firstly, Get the confluence content first=="
result=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  getpagesummary -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space})
if [[ "${result}" =~ "You're not allowed to view that page, or it does not exist." ]] ; then
  echo "=========It does  not exist======="
  exit 1
else
  echo "=========The page exist============="
#echo confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  getpagecontent -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space} > ${tmp_dir}/build_report.txt
  confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  getpagecontent -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space} > ${tmp_dir}/build_report.txt
fi
cat ${tmp_dir}/build_report.txt
if [[ -e "${tmp_dir}/build_report.txt" ]]; then
  	echo "==The report has been got from confluence=="
  	echo "==Will begin to parser it=="
fi
tr -d '\n' < ${tmp_dir}/build_report.txt > ${tmp_dir}/build_report_final.txt
cat ${tmp_dir}/build_report_final.txt
general_result_and_brief_summary=$( sudo python parser_build_testing_report.py "${tmp_dir}/build_report_final.txt" )
echo ${general_result_and_brief_summary}
echo "==Parsering it===="
general_result=$( echo ${general_result_and_brief_summary} | cut -d "-" -f 1 )
echo "==Parser Done====="
echo "==Will send the report out=="
brief_summary=$( echo ${general_result_and_brief_summary} | cut -d "-" -f 2 )
echo sudo python talk_to_jenkins_to_send_report.py ${username} ${password} ${send_report_ci_name} ${et_build_name_or_id} "\"${general_result}\"" "\"${brief_summary}\""
echo "==sending the report=="
send_mail_result=$( sudo python talk_to_jenkins_to_send_report.py ${username} ${password} ${send_report_ci_name} ${et_build_name_or_id} "\"${general_result}\"" "\"${brief_summary}\"")
echo "==sending the report==" )
if [[ $(echo ${send_mail_result}) == "SUCCESS" ]]; then
  echo "== Cheer, the report mail has been sent out! =="
else
  echo "== Sorry, failed to send mail. =="
fi
sudo rm -rf ${tmp_dir}