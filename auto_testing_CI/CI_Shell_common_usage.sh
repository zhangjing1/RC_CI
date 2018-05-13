initial_et_build_id(){
	et_build_id=""
	if [[ "${1}" =~ 'git' ]]; then
		et_build_id=$( echo "${1}" | cut -d '-' -f 2| cut -d '.' -f 2 )
	else
		et_build_id="${1}"
	fi
	echo "${et_build_id}"
}

initial_et_build_version(){
	echo "${1}" | sed 's/\.//g' | sed 's/-//g'
}

get_system_raw_version(){
	curl http://"${1}"/system_version.json
}

get_et_product_version(){
	et_product_version_on_brew=$(get_system_raw_version "${1}")
	et_product_version=$(initial_et_build_version "${et_product_version_on_brew}")
	echo "${et_product_version}"
}

get_deployed_et_version(){
	et_testing_server_raw_version=$(get_system_raw_version "${1}")
	et_testing_server_version=$(initial_et_build_version "${et_testing_server_raw_version}")
	echo "${et_testing_server_version}"
}

get_deployed_et_id(){
	et_testing_server_raw_version=$(get_system_raw_version "${1}")
	et_testing_server_version_id=$(initial_et_build_id "${et_testing_server_raw_version}")
	echo "${et_testing_server_version_id}"
}

get_ansible_commands_with_product_et_version(){
	ansible_command_part_1="ansible-playbook -vv --user root --skip-tags 'et-application-config'"
	ansible_command_part_2=" --limit ${1} -e errata_version=${2} -e errata_fetch_brew_build=true"
	ansible_command_part_3=""
	if [[ "${3}" == "true" ]]
    then
		ansible_command_part_3="-e errata_downgrade=true"
	fi
	ansible_command_part_4=" ${4}/playbooks/errata-tool/qe/deploy-errata-qe.yml"
	ansible_command="${ansible_command_part_1} ${ansible_command_part_2} ${ansible_command_part_3} ${ansible_command_part_4}"
	echo "${ansible_command}"
}


get_ansible_commands_with_build_id(){
	ansible_command_part_1="ansible-playbook -vv --user root --skip-tags 'et-application-config'"
	ansible_command_part_2=" --limit ${1} -e errata_jenkins_build=${2} "
	ansible_command_part_3=" ${3}/playbooks/errata-tool/qe/deploy-errata-qe.yml"
	ansible_command="${ansible_command_part_1} ${ansible_command_part_2} ${ansible_command_part_3}"
	echo "${ansible_command}"
}


run_ansible(){
	ansible_command=""
	set -x
	env
	cd "${2}/playbooks/errata-tool" || exit
	make clean-roles
	make qe-roles
	e2e_env_workaround "${1}" "${2}"
	"${3}"
}


keep_the_env_as_product_version(){
	downgrade="false"
	need_deploy="true"
	et_product_raw_version=$(get_system_raw_version "${1}")
	et_product_version=$(get_et_product_version "${1}")
	et_depolyed_version=$(get_deployed_et_version "${2}")
	echo "=== Get the following vesions:"
	echo "Proudct Version: ${et_product_version}"
	echo "Installed version: ${et_depolyed_version}"
	if [[ "${et_product_version}" == "${et_depolyed_version}" ]]; then
		echo "=== The deployed version is the same as the product version"
		need_deploy="false"
	elif [[ "${et_product_version}" -lt "${et_depolyed_version}" ]]; then
		downgrade="true"
	else
		downgrade="false"
	fi
	if [[ "${need_deploy}" == "false" ]]; then
		echo "=== There is no need to deploy the product version again"
	else
		perf_restore_db "${2}"
		ansible=$(get_ansible_commands_with_product_et_version "${2}" "${et_product_raw_version}" "${downgrade}" "${3}")
		echo "=== Ansible commands: ${ansible}"
		run_ansible "${2}" "${3}" "${ansible}"
		update_setting "${1}"
		restart_service "${1}"
	fi
}

confirm_deployed_version_with_expected_version(){
	et_deployed_version=$(get_deployed_et_id "${1}")
	et_expected_version=$(initial_et_build_id "${2}")
	echo "=== Get the following vesions:"
	echo "Expected Version: ${et_expected_version}"
	echo "Installed version: ${et_depolyed_version}"
	if [[ "${et_deployed_version}" == "${et_expected_version}" ]]; then
		echo "=== SUCCESS ==="
	else
		echo "=== FAILED ==="
	fi
}

upgrade_the_env_to_expect_version(){
	et_expected_version=$(initial_et_build_id "${2}")
	ansible=$(get_ansible_commands_with_build_id "${1}" "${et_expected_version}"  "${3}")
	echo "== Upgrade the env"
	echo "=== Ansible commands: ${ansible}"
	run_ansible "${1}" "${3}" "${ansible}"
	update_setting "${1}"
	restart_service "${1}"
}


perf_restore_db() {
	if [[ "${1}" =~ "perf"  ]]
		then
		echo "=== [INFO] === Restoring the perf db"
		ssh  root@errata-stage-perf-db.host.stage.eng.bos.redhat.com "cd /var/lib;./restore_db.sh"
	fi
}

e2e_env_workaround() {
    if [[ "${1}" =~ "e2e" ]]
    then
        # e2e env has some problem which would raise 2 errors
        # the workaround 1 to fix the e2e env kinit ansible problem
        echo "  ignore_errors: yes" >> "${2}"/playbooks/errata-tool/qe/roles/errata-tool/restart-application/tasks/refresh-kerb-ticket.yml
        # the workaround 2 to make sure the system version can be updated successfully
        echo "  ignore_errors: yes" >> "${2}"/playbooks/errata-tool/qe/roles/errata-tool/verify-deploy/tasks/main.yml
    fi
}

update_setting() {
	if [[ "${1}" =~ "perf" ]]; then
		echo "=== [INFO] Custom the brew & bugzilla settings of testing server ==="
		ssh root@errata-stage-perf-db.host.stage.eng.bos.redhat.com 'cd ~;./check_stub.sh'
	fi

	if [[ "${1}" =~ "e2e" ]]; then
		echo "=== [INFO] Custom the pub & bugzilla settings of testing server ==="
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/bz-qgong.usersys.redhat.com/bz-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/bugzilla.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pub-devopsqe.usersys.redhat.com/pub-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pdc-et.host.qe.eng.pek2.redhat.com/pdc.engineering.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
	fi
	# clean the cache for all testing servers
	ssh root@"${1}" 'rm -rf /var/www/errata_rails/tmp/cache/*'
	# enable qe menu for all testing servers
	ssh root@"${1}" "sed -i \"s/errata.app.qa.eng.nay.redhat.com/${1}/g\" /var/www/errata_rails/app/controllers/concerns/user_authentication.rb"
}

restart_service() {
	echo "=== [INFO] Restarting the services on the testing server =="
	ssh root@"${1}" '/etc/init.d/httpd24-httpd restart'
	ssh root@"${1}" '/etc/init.d/delayed_job restart'
	ssh root@"${1}" '/etc/init.d/messaging_service restart'
}
