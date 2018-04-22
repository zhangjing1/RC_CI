sudo find /tmp  -name "*_content.txt" | xargs sudo rm -rf {}


initial_et_build_version(){
  if [[ ${et_build_name_or_id} =~ "-" ]]; then
    echo "=== ET build name has been provided: ${et_build_name} =="
    et_build_version=$( echo ${et_build_name_or_id} | cut -d '-' -f 2| cut -d '.' -f 2 )
  else
    echo "=== ET build id is provided =="
    et_build_version=${et_build_name_or_id}
  fi
}

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

install_scripts_env
initial_et_build_version
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
result=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  getpagesummary -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space})
if [[ "${result}" =~ "You're not allowed to view that page, or it does not exist." ]] ; then
  echo "=========It does  not exist. Will generate the testing report and add page for it"
  echo "generate_rc_report_content_for_all_testing"
  sudo python regenerate_rc_report_content_for_all_testings.py ${username} ${password} ${et_build_version}
  check_report_content_file_exist ${tmp_dir}
  result_add_page=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  addpage -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space} -P ${parent_page} -f "general_report_content.txt")
  add_update_page_result ${result_add_page}
else
  echo "=========The page has been created, would regenerate the report content=============="
  sudo find /tmp -name "*_content.txt" | xargs sudo rm -rf {}
  sudo python regenerate_rc_report_content_for_all_testings.py ${username} ${password} ${et_build_version}
  check_report_content_file_exist ${tmp_dir}
  # delete the original report page and generate the new one
  #$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  removepage -n "ET Testing Report for RC build ${et_rc_version}"  -s ${space})
  if [[ $(echo $?) -eq 0 ]]; then
    echo "==========Regenerate the testing report====================="
    result_update_page=$(confluence-cli --wikiurl="https://docs.engineering.redhat.com" -u ${username} -p ${password}  updatepage -n "ET Testing Report for build ${et_build_name_or_id}"  -s ${space} -P ${parent_page} -f "general_report_content.txt")
    add_update_page_result ${result_update_page}
  fi
fi

sudo find /tmp  -name "*_content.txt" | xargs sudo rm -rf {}
