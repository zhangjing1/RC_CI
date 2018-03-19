#/bin/bash
# The script is used by 'Trigger Robot Framework UAT Testing Remotely' CI
# Initial the env to run the 'talk_to_robot_framework_jenkins' python script
sudo pip install python-jenkins
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
sudo python  talk_to_robot_framework_jenkins.py ${robotframework_jenkins_user}  ${robotframework_jenkins_password} ${build_name} ${expect_run_time}
testing_result_code=$(echo $?)
if [[ ${testing_result_code} -gt 0 ]]; then
	exit ${testing_result_code}
fi
echo "====removing the useless files===="
rm -rf ${tmp_dir}