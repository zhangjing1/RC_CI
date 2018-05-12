initial_et_build_version(){
	if [[ ${1} =~ "git" ]]; then
		et_build_version=$( echo ${1} | cut -d '-' -f 2| cut -d '.' -f 2 )
	elif [[ ${1} =~ "-" ]]; then
		et_build_version=$( echo ${1} | sed 's/\.//g' | sed 's/-//g' )
	fi
	echo ${et_build_version}
}

get_et_product_version(){
	et_product_version_on_brew=$(curl http://errata.devel.redhat.com/system_version.json  | tr -d '"'| cut -d "-" -f 1)
	et_product_version=$(initial_et_build_version ${et_product_version_on_brew})
	echo ${et_product_version}
}

get_deployed_version(){
	et_testing_server_raw_version=$(curl http://${1}/system_version.json)
	et_testing_server_version=$(initial_et_build_version ${et_testing_server_raw_version})
	echo ${et_testing_server_version}
}
# if the deployed et version is the same with the expected version, then there is no updated
compare_deployed_et_to_expect_et() {
	need_deploy="false"
	et_testing_server_version=$(get_deployed_version ${1})
	if [[ "${et_testing_server_version}"  ==  "${2}" ]]; then
		need_deploy="false"
	elif [[ $(echo ${et_testing_server_version})  -gt  "$(echo ${2})" ]]; then
		need_deploy="downgrade"
	else
		need_deploy="upgrade"
	fi
	echo  ${need_deploy}
}

# if the expect et version is null or the same with the product version, then just initial the env
compare_expect_et_to_product_et() {
	same_version_with_product="false"
	et_product_version=$(get_et_product_version)
	et_expect_version=$1
	if [[ -z "${et_expect_version}" ]]; then
		same_version_with_product="true"
	elif [[ "${et_expect_version}" == "${et_product_version}" ]]; then
		same_version_with_product="true"
	fi
	echo ${same_version_with_product}
}

compare_deployed_et_to_product_et() {
	initial_with_product="true"
	et_product_version=$(get_et_product_version)
	et_testing_server_version=$(get_deployed_version ${1})
	if [[ "${et_product_version}" == "${et_testing_server_version}" ]]; then
		initial_with_product="false"
	elif [[ $(echo ${et_product_version}) -lt $(echo ${et_testing_server_version}) ]]; then
		initial_with_product="downgrade"
	else
		initial_with_product="upgrade"
	fi
	echo ${initial_with_product}
}


check_et_for_initial_et_ci() {
	need_initalize="false"
	if [[ -z $1 ]]; then
		same_version_with_product=$(compare_expect_et_to_product_et $1)
		if [[ "${same_version_with_product}" == "true" ]]; then
			need_initalize="false"
		fi
	else
		same_version_with_expect=$(compare_deployed_et_to_expect_et $1)
		if [[ "${same_version_with_expect}" == "true" ]]; then
			need_initalize="false"
		else
			need_initalize=$(compare_deployed_et_to_product_et $1)
		fi
	fi
	echo ${need_initalize}
}

check_et_for_upgrade_et_ci() {
	need_deploy="false"
	if [[ -z $1 ]]; then
		need_deploy="false"
	else
		need_deploy=$(compare_deployed_et_to_expect_et ${2} ${1})
	fi
	echo ${need_deploy}
}


perf_restore_db() {
	if [[ ${1} =~ "perf"  ]]
		then
		echo "=== [INFO] === Restoring the perf db"
		ssh  root@errata-stage-perf-db.host.stage.eng.bos.redhat.com "cd /var/lib;./restore_db.sh"
	fi
}

perf_backup_db() {
	if [[ ${1} == true ]]
		then
		#backup the db after its migration
		ssh  root@errata-stage-perf-db.host.stage.eng.bos.redhat.com "cd /var/lib/;./backup_db.sh"
		#change the perf env settings for brew&bugzilla stub.
		ssh  root@errata-stage-perf.host.stage.eng.bos.redhat.com "cd ~; ./check_stub.sh"
	fi
}
e2e_env_workaround() {
    if [[ ${1} == true ]]
    then
        # e2e env has some problem which would raise 2 errors
        # the workaround 1 to fix the e2e env kinit ansible problem
        echo "  ignore_errors: yes" >> ${2}/playbooks/errata-tool/qe/roles/errata-tool/restart-application/tasks/refresh-kerb-ticket.yml
        # the workaround 2 to make sure the system version can be updated successfully
        echo "  ignore_errors: yes" >> ${2}/playbooks/errata-tool/qe/roles/errata-tool/verify-deploy/tasks/main.yml
    fi
}

update_setting() {
	if [[ ${1} =~ "perf" ]]; then
		echo "=== [INFO] Custom the brew & bugzilla settings of testing server ==="
		ssh root@errata-stage-perf-db.host.stage.eng.bos.redhat.com 'cd ~;./check_stub.sh'
	fi

	if [[ ${1} =~ "e2e" ]]; then
		echo "=== [INFO] Custom the pub & bugzilla settings of testing server ==="
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/bz-qgong.usersys.redhat.com/bz-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/bugzilla.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pub-devopsqe.usersys.redhat.com/pub-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pdc-et.host.qe.eng.pek2.redhat.com/pdc.engineering.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
	fi
	# clean the cache for all testing servers
	ssh root@${1} 'rm -rf /var/www/errata_rails/tmp/cache/*'
	# enable qe menu for all testing servers
	ssh root@${1} "sed -i \"s/errata.app.qa.eng.nay.redhat.com/${1}/g\" /var/www/errata_rails/app/controllers/concerns/user_authentication.rb"
}

restart_service() {
	echo "=== [INFO] Restarting the services on the testing server =="
	ssh root@${1} '/etc/init.d/httpd24-httpd restart'
	ssh root@${1} '/etc/init.d/delayed_job restart'
	ssh root@${1} '/etc/init.d/messaging_service restart'
}


get_ansible_commands(){
	ansible_command_part_1="ansible-playbook -vv --user root --skip-tags 'et-application-config'"
	ansible_command_part_2=" --limit ${1} -e errata_version=${2} -e errata_fetch_brew_build=true"
	ansible_command_part_3=""
	if [[ "${3}" == "true" ]]
    then
		ansible_command_part_3="-e errata_downgrade=true"
	fi
	ansible_command_part_4=" playbooks/errata-tool/qe/deploy-errata-qe.yml"
	ansible_command="${ansible_command_part_1} ${ansible_command_part_2} ${ansible_command_part_3} ${ansible_command_part_4}"
	echo ${ansible_command}
}

