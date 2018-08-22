initial_et_build_id(){
	if [[ "${1}" =~ 'git' ]]; then
		et_build_id=$( echo "${1}" | cut -d '-' -f 2| cut -d '.' -f 2 )
	elif [[ "${1}" =~ '-' ]]; then
		et_build_id=$(echo "${1}" | cut -d '-' -f 1 | sed 's/\.//g')
	else
		et_build_id=${1}
	fi
	echo "${et_build_id}"
}

initial_et_build_version(){
	echo "${1}" | cut -d "-" -f 1 | sed 's/\.//g'
}

get_system_raw_version(){
	curl http://"${1}"/system_version.json | sed 's/"//g'
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
	if [[ "${3}" == "downgrade" ]]
    then
		ansible_command_part_3="-e errata_downgrade=true"
	fi
	ansible_command_part_4=" playbooks/qe/deploy-errata-qe.yml"
	ansible_command="${ansible_command_part_1} ${ansible_command_part_2} ${ansible_command_part_3} ${ansible_command_part_4}"
	echo "${ansible_command}"
}


get_ansible_commands_with_build_id(){
	ansible_command_part_1="ansible-playbook -vv --user root --skip-tags 'et-application-config'"
	ansible_command_part_2=" --limit ${1} -e errata_jenkins_build=${2} "
	ansible_command_part_3=" playbooks/qe/deploy-errata-qe.yml"
	ansible_command="${ansible_command_part_1} ${ansible_command_part_2} ${ansible_command_part_3}"
	echo "${ansible_command}"
}

compare_version_or_id(){
    #echo "=== Format the compared versions again ==="
    first_version=$(printf '%-6d' ${1} | sed 's/ /0/g')
    second_version=$(printf '%-6d' ${2} | sed 's/ /0/g')
    #echo "The first version is: ${first_version}"
    #echo "The second version is: ${second_version}"
    comparison_result="downgrade"
    if [[ "${first_version}" == "${second_version}" ]]; then
        comparison_result="same"
    elif [[ "${first_version}" -lt "${second_version}" ]]; then
        comparison_result="upgrade"
    fi
    #echo "=== The comparison result is: ${comparison_result} =="
    echo ${comparison_result}
}

perf_restore_db() {
	if [[ "${1}" =~ "perf"  ]]
		then
		echo "=== [INFO] === Restoring the perf db"
		ssh  root@errata-stage-perf-db.host.stage.eng.bos.redhat.com "cd /var/lib;./restore_db.sh"
	fi
}

initialize_e2e_pub_errata_xmlrpc_settings() {
	if [[ "$1" =~ "e2e" ]]; then
		echo "=== Updating the errata_xmlprc settings to the target et against the e2e pub server"
		ssh root@pub-e2e.usersys.redhat.com 'sed -i "s/et.test.eng.redhat.com/et-e2e.usersys.redhat.com/g" /etc/pub/pubd.conf'
		ssh root@pub-e2e.usersys.redhat.com '/etc/init.d/pubd restart'
	fi
}

e2e_env_workaround() {
    if [[ "${1}" =~ "e2e" ]]; then
    	echo "== Running the e2e env ansible workaround to ignore the kinit ansible problems"
        # e2e env has some problem which would raise 2 errors
        # the workaround 1 to fix the e2e env kinit ansible problem
        echo "  ignore_errors: yes" >> ${2}/playbooks/qe/roles/errata-tool/restart-application/tasks/refresh-kerb-ticket.yml
        # the workaround 2 to make sure the system version can be updated successfully
        echo "  ignore_errors: yes" >> ${2}/playbooks/qe/roles/errata-tool/verify-deploy/tasks/main.yml
        # the workaround 3 is to make sure the key tab related error can be ignored
        sed -i '/name: copy over krb5.conf/a \  ignore_errors: True' ${2}/playbooks/qe/roles/kerberos/tasks/main.yml
        sed -i '/copy host keytab/a \  ignore_errors: True' ${2}/playbooks/qe/roles/kerberos/tasks/main.yml
        sed -i '/install kerberos client packages on RedHat based platforms/a \  ignore_errors: True' ${2}/playbooks/qe/roles/kerberos/tasks/main.yml
    fi
}

update_setting() {
	if [[ "${1}" =~ "perf" ]]; then
		echo "=== [INFO] Custom the brew & bugzilla settings of testing server ==="
		ssh root@errata-stage-perf.host.stage.eng.bos.redhat.com 'cd ~;./check_stub.sh'
	fi

	if [[ "${1}" =~ "e2e" ]]; then
		echo "=== [INFO] Custom the pub & bugzilla settings of the e2e server ==="
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/bz-qgong.usersys.redhat.com/bz-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/bugzilla.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pub-et-qe.usersys.redhat.com/pub-e2e.usersys.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/pdc-et.host.qe.eng.pek2.redhat.com/pdc.engineering.redhat.com/" /var/www/errata_rails/config/initializers/credentials/pub.rb'
		echo "=== [INFO] Custom the brew settings of the e2e server"
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/brewweb.engineering.redhat.com/brew-qa.usersys.redhat.com/" /var/www/errata_rails/config/initializers/settings.rb'
		ssh root@et-e2e.usersys.redhat.com 'sed -i "s/brewhub.engineering.redhat.com/brew-qa.usersys.redhat.com/" /var/www/errata_rails/config/initializers/settings.rb '
	fi
	# clean the cache for all testing servers
	ssh root@"${1}" 'rm -rf /var/www/errata_rails/tmp/cache/*'
	# enable qe menu for all testing servers
	ssh root@"${1}" "sed -i \"s/errata.app.qa.eng.nay.redhat.com/${1}/g\" /var/www/errata_rails/app/controllers/concerns/user_authentication.rb"
}

do_db_migration() {
	if [[ "${1}" =~ "perf" ]]; then
		echo "== Doing the db migration on perf env =="
		db_migrate_command="cd /var/www/errata_rails && source scl_source enable rh-ruby22 && SILENCE_DEPRECATIONS=1 RAILS_ENV=staging bundle exec rake db:migrate"
		ssh root@errata-stage-perf.host.stage.eng.bos.redhat.com "${db_migrate_command}"
	fi
}

restart_service() {
	echo "=== [INFO] Restarting the services on the testing server =="
	ssh root@"${1}" '/etc/init.d/httpd24-httpd restart'
	ssh root@"${1}" '/etc/init.d/delayed_job restart'
	ssh root@"${1}" '/etc/init.d/messaging_service restart'
	ssh root@"${1}" '/etc/init.d/qpid_service restart'
	# For e2e server, let us stop the qpid service as default
	if [[ "${1}" =~ "e2e" ]]; then
		echo "=== [INFO] Stop the qpid service for the e2e server ==="
		ssh root@et-e2e.usersys.redhat.com "/etc/init.d/qpid_service stop"
	fi
}
