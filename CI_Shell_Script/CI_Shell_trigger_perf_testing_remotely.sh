#/bin/bash
# The script is used by 'Trigger Perf Testing Remotely' CI
# Initial the env to run the 'talk_to_perf_jenkins' python script
sudo pip install python-jenkins
export ET_Perf_User=${perf_jenkins_user}
export ET_Perf_User_Password=${perf_jenkins_password}
tmp_dir="/tmp/$(date +'%s')"
mkdir -p ${tmp_dir}
cd ${tmp_dir}
# Wget the files
echo "===============Download the CI files under $(pwd)=========="
wget http://github.com/testcara/RC_CI/archive/master.zip
unzip master.zip
cd ${tmp_dir}/RC_CI-master/talk_to_jenkins
# Run the script
echo "==============Start the testing==============="
sudo python  talk_to_perf_jenkins.py ${test_type}
testing_result_code=$(echo $?) 
if [[ ${testing_result_code} -gt 0 ]]; then
	exit ${testing_result_code}
fi
echo "====removing the useless files===="
rm -rf ${tmp_dir}