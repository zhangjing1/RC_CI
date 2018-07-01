#!/bin/bash
set -eo pipefail
IFS=$'\n\t'

install_scripts_env(){
	pip install --upgrade pip
	pip install confluence-py
	pip install python-jenkins==0.4.16
	pip install scp
	yum install wget -y
	yum install git -y
}

initial_et_build_version(){
	if [[ ${et_build_name_or_id} =~ "-" ]]; then
		echo "=== ET build name has been provided: ${et_build_name} =="
		et_build_version=$( echo ${et_build_name_or_id} | cut -d '-' -f 2| cut -d '.' -f 2 )
	else
		echo "=== ET build id is provided =="
		et_build_version=${et_build_name_or_id}
	fi
}


run_target_scripts(){
	python /workdir/RC_CI-master/auto_testing_CI/talk_to_rc_jenkins_to_parser_perf_report.py ${username} ${password} ${et_build_version} ${tolerance} ${max_accepted_time} ${perf_jmeter_slave_server}
}


install_scripts_env
initial_et_build_version
run_target_scripts
